import logging
import time
import os
import json
import re
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from openai import OpenAI, AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.lens import SourceData, Lens, Artifact
from app.core.config import get_settings
from app.models.models import Source, SourceMaterial, Card, CardStatus, SourceLog
from app.lenses.registry import get_default_summary_lens, get_profiler_lens, get_reading_notes_lens, get_study_quiz_lens, get_figure_association_lens
from app.services.pdf_extractor import extract_figures_from_pdf, save_figures_to_local, get_figure_info_for_prompt
import uuid as uuid_module

logger = logging.getLogger(__name__)

class RunnerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize Google GenAI Client
        settings = get_settings()
        # Priority: GEMINI_API_KEY -> OPENAI_API_KEY (fallback)
        api_key = settings.gemini_api_key
        if not api_key:
            api_key = settings.openai_api_key
            if api_key:
                 logger.info("Using OPENAI_API_KEY as fallback for Gemini Client.")
            else:
                 logger.warning("No API key found (GEMINI_API_KEY or OPENAI_API_KEY).")

        from google import genai
        self.client = genai.Client(api_key=api_key)

    async def _log_event(
        self,
        source_id: UUID,
        event_type: str,
        status: str,
        lens_key: str = None,
        message: str = None,
        duration_ms: int = None,
        extra_data: dict = None
    ):
        """
        Log a source processing event.
        """
        log = SourceLog(
            source_id=source_id,
            event_type=event_type,
            status=status,
            lens_key=lens_key,
            message=message,
            duration_ms=duration_ms,
            extra_data=extra_data or {}
        )
        self.db.add(log)
        # Don't commit here - let caller handle transaction
        return log
    
    async def _update_lens_log(
        self,
        source_id: UUID,
        lens_key: str,
        status: str,
        message: str = None,
        duration_ms: int = None,
        extra_data: dict = None
    ):
        """
        Update an existing lens log entry instead of creating a new one.
        This prevents duplicate log entries for the same lens execution.
        """
        # Find the most recent running log for this lens
        stmt = (
            select(SourceLog)
            .where(
                SourceLog.source_id == source_id,
                SourceLog.lens_key == lens_key,
                SourceLog.status == "running"
            )
            .order_by(SourceLog.created_at.desc())
            .limit(1)
        )
        result = await self.db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            # Update existing log
            log.status = status
            log.event_type = "lens_completed" if status == "completed" else "lens_failed"
            if message is not None:
                log.message = message
            if duration_ms is not None:
                log.duration_ms = duration_ms
            if extra_data:
                log.extra_data = extra_data
        else:
            # Fallback: create new log if no running log found
            log = SourceLog(
                source_id=source_id,
                event_type="lens_completed" if status == "completed" else "lens_failed",
                status=status,
                lens_key=lens_key,
                message=message,
                duration_ms=duration_ms,
                extra_data=extra_data or {}
            )
            self.db.add(log)
        
        return log

    def _parse_json_robust(self, content: str) -> Any:
        """
        Attempt to parse JSON from a string, handling markdown fences and common LLM quirks.
        """
        # 1. Strip markdown fences
        content = content.replace("```json", "").replace("```", "").strip()
        
        # 2. Try identifying the JSON block boundaries (first { or [ and last } or ])
        # This helps if there is conversational text around the JSON
        start_matrix = {
            "{": content.find("{"),
            "[": content.find("[")
        }
        # Filter -1
        valid_starts = [idx for idx in start_matrix.values() if idx != -1]
        
        if valid_starts:
            start_idx = min(valid_starts)
            # Determine end char based on start char
            start_char = content[start_idx]
            end_char = "}" if start_char == "{" else "]"
            end_idx = content.rfind(end_char)
            
            if end_idx != -1 and end_idx > start_idx:
                 content = content[start_idx : end_idx + 1]

        # 3. Handle common escape issues (e.g. LaTeX backslashes)
        # Repair invalid escapes: matching backslash that is NOT followed by a valid escape char
        # Valid JSON escapes: ", \, /, b, f, n, r, t, uXXXX
        content = re.sub(r'(?<!\\)\\(?![\\"/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', content)

        return json.loads(content)

    async def run_lens(self, source_data: SourceData, lens: Lens) -> Artifact:
        """
        Execute a single Lens against a Source using google-genai SDK.
        """
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
        from google.genai import types
        from google.genai.errors import ServerError, ClientError

        # Define retry strategy
        @retry(
            wait=wait_exponential(multiplier=1, min=2, max=60),
            stop=stop_after_attempt(5),
            retry=retry_if_exception_type(ServerError), # Retry on 5xx
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        async def _make_api_call(model, contents, config):
            return await self.client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )

        try:
            # Construct Contents
            contents = []
            
            # System Prompt (Gemini supports system_instruction in config, but putting it in contents matches older patterns too. 
            # However, SDK recommends config.system_instruction. Let's use config if possible, or prepended text.)
            # For simplicity with the unified contents structure, let's strictly follow SDK 'system_instruction' config if we want, 
            # OR just prepend it to the user message which is often more robust across models.
            # Let's use the config.system_instruction approach for cleanliness.
            system_instruction = lens.system_prompt
            
            # User Prompt Construction
            prompt_text = lens.user_prompt_template
            if source_data.text:
                 try:
                     prompt_text = prompt_text.format(text=source_data.text)
                 except KeyError:
                     pass
            else:
                 if "{text}" in prompt_text:
                     prompt_text = prompt_text.replace("{text}", "this document")

            # Content Parts
            parts = []
            parts.append(types.Part.from_text(text=prompt_text))

            if source_data.base64_data and source_data.mime_type:
                # Add image/pdf part
                import base64
                clean_b64 = source_data.base64_data.replace("\n", "").replace("\r", "")
                image_bytes = base64.b64decode(clean_b64)
                parts.append(types.Part.from_bytes(data=image_bytes, mime_type=source_data.mime_type))
            
            # Add multimodal images (e.g. for figure association)
            if source_data.images:
                logger.info(f"Adding {len(source_data.images)} images to multimodal request")
                for i, img_bytes in enumerate(source_data.images):
                    parts.append(types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"))

            contents.append(types.Content(role="user", parts=parts))

            # Determine Model
            settings = get_settings()
            env_model = settings.gemini_model or "gemini-2.0-flash-exp"
            model_name = lens.parameters.get("model", env_model)
            
            # Config
            config = types.GenerateContentConfig(
                temperature=lens.parameters.get("temperature", 0.7),
                system_instruction=system_instruction,
                http_options=types.HttpOptions(timeout=180000) # 180 seconds in ms
            )
            
            # JSON Schema enforcement
            if lens.output_schema:
                 # Check if schema is a Pydantic model or dict
                 if isinstance(lens.output_schema, dict):
                     # For raw dict schema, we might need to rely on prompt instruction + parser, 
                     # OR use response_mime_type="application/json"
                     config.response_mime_type = "application/json"
                     if "response_schema" in lens.output_schema:
                          config.response_schema = lens.output_schema["response_schema"]
                 else:
                     # If it's a Pydantic class (from instructor pattern before)
                     # We can pass it if we convert it to schema, but usually lens.output_schema here is likely a dict or None from registry
                     config.response_mime_type = "application/json"

            # DEBUG: Log
            logger.info(f"LLM REQUEST [lens={lens.key}] Model={model_name}")
            
            start_time = time.time()
            
            # Call API
            response = await _make_api_call(model=model_name, contents=contents, config=config)
            
            end_time = time.time()
            
            content = response.text
            logger.info(f"LLM RESPONSE [lens={lens.key}]: {content[:200]}...") # Log 200 chars
            
            # Parse JSON if needed
            if lens.output_schema:
                try:
                    content = self._parse_json_robust(content)
                except Exception as e:
                    logger.warning(f"Failed to parse JSON output for lens {lens.key}: {e}")
            
            return Artifact(
                lens_key=lens.key,
                source_id=source_data.id,
                content=content,
                created_at=end_time,
                usage={"duration_ms": int((end_time - start_time) * 1000)}
            )
            
        except Exception as e:
            logger.error(f"Error running lens {lens.key}: {e}")
            raise e

    async def process_new_source(self, source_id: UUID):
        """
        Orchestrator: Fetch Source -> Create SourceData -> Run Default Lenses -> Persist.
        """
        logger.info(f"Processing new source: {source_id}")
        
        # 1. Fetch Source
        stmt = select(Source).where(Source.id == source_id)
        result = await self.db.execute(stmt)
        source = result.scalar_one_or_none()
        
        if not source:
            logger.error(f"Source {source_id} not found")
            return

        # Log start of processing (Sync Started)
        process_start_time = time.time()
        await self._log_event(source.id, "sync_started", "running", message="Starting source processing")
        await self.db.commit()

        # 2. Extract Content (Text or Base64)
        try:
            fetched_content = await self._fetch_source_content(source)
        except Exception as e:
            await self._log_event(source.id, "error", "failed", message=f"Unexpected error fetching content: {str(e)}")
            await self.db.commit()
            return

        if not fetched_content:
            msg = f"No content extracted for source {source_id}. Check URL validity."
            logger.warning(msg)
            await self._log_event(source.id, "error", "failed", message=msg)
            await self.db.commit()
            return
            
        # 3. Create SourceData
        source_data = SourceData(
            id=str(source.id),
            text=fetched_content.get("text"),
            base64_data=fetched_content.get("base64_data"),
            mime_type=fetched_content.get("mime_type"),
            metadata={"title": source.name, "url": source.connection_config.get("url")}
        )
        
        # 4. Run Default Summary Lens
        summary_lens = get_default_summary_lens()
        start_time = time.time()
        await self._log_event(source.id, "lens_started", "running", lens_key="default_summary", message="Starting summary generation")
        await self.db.commit()  # Commit so log is visible immediately
        try:
            summary_artifact = await self.run_lens(source_data, summary_lens)
            duration_ms = int((time.time() - start_time) * 1000)
            await self._update_lens_log(source.id, "default_summary", "completed", 
                                       message="Summary generated successfully", duration_ms=duration_ms)
        except Exception as e:
            import traceback
            duration_ms = int((time.time() - start_time) * 1000)
            err_msg = str(e) or f"Error: {type(e).__name__}"
            logger.error(f"Lens summary failed: {err_msg}\n{traceback.format_exc()}")
            await self._update_lens_log(source.id, "default_summary", "failed",
                                       message=err_msg, duration_ms=duration_ms)
            summary_artifact = Artifact(lens_key="default_summary", source_id=str(source.id), content={"error": err_msg}, created_at=time.time())
        
        # Create dummy artifact for suggestions so we don't break strict structure if expected
        profiler_artifact = Artifact(
            lens_key="profiler_meta", 
            source_id=str(source.id), 
            content=[], # Empty suggestions
            created_at=time.time()
        )
        
        # 6. Persist to SourceMaterial
        stmt_mat = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
        res_mat = await self.db.execute(stmt_mat)
        source_material = res_mat.scalars().first()
        
        if not source_material:
            external_id = source.connection_config.get("url", "unknown")
            stmt_exist = select(SourceMaterial).where(
                SourceMaterial.user_id == source.user_id,
                SourceMaterial.external_id == external_id
            )
            res_exist = await self.db.execute(stmt_exist)
            existing_material = res_exist.scalars().first()
            
            if existing_material:
                logger.info(f"Found existing material used by another source, re-linking to source {source.id}")
                source_material = existing_material
                source_material.source_id = source.id
            else:
                 source_material = SourceMaterial(
                    user_id=source.user_id,
                    source_id=source.id,
                    external_id=external_id,
                    title=source.name,
                    rich_data={}
                )
                 self.db.add(source_material)
        
        # Update rich_data
        if source_material.rich_data is None:
            source_material.rich_data = {}
            
        new_data = dict(source_material.rich_data)
        new_data["summary"] = summary_artifact.content
        new_data["suggestions"] = profiler_artifact.content
        
        source_material.rich_data = new_data
        
        await self.db.commit()
        
        # 7. For paper sources, generate reading notes cards
        batch_id = None
        if self._is_paper_source(source):
            start_time = time.time()
            await self._log_event(source.id, "lens_started", "running", lens_key="reading_notes", message="Generating reading notes")
            await self.db.commit()  # Commit so log is visible immediately
            try:
                batch_id = await self._generate_reading_notes(source, source_data, source_material)
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "reading_notes", "completed",
                                           message="Reading notes generated", duration_ms=duration_ms)
            except Exception as e:
                import traceback
                logger.error(f"Reading notes generation failed details: {traceback.format_exc()}")
                
                err_msg = str(e)
                if not err_msg:
                    err_msg = f"Error: {type(e).__name__}"
                
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "reading_notes", "failed",
                                           message=err_msg, duration_ms=duration_ms)
        
        # Throttle between lenses to avoid 429/503 from local LLM
        import asyncio
        await asyncio.sleep(2)

        # 8. Run Study Quiz Lens (Flashcards)
        if self._is_paper_source(source):
            start_time = time.time()
            await self._log_event(source.id, "lens_started", "running", lens_key="study_quiz", message="Generating flashcards & quiz")
            await self.db.commit()
            try:
                await self._generate_study_quiz(source, source_data, source_material)
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "study_quiz", "completed",
                                            message="Flashcards generated", duration_ms=duration_ms)
            except Exception as e:
                import traceback
                duration_ms = int((time.time() - start_time) * 1000)
                err_msg = str(e) or f"Error: {type(e).__name__}"
                logger.error(f"Study quiz generation failed: {err_msg}\n{traceback.format_exc()}")
                await self._update_lens_log(source.id, "study_quiz", "failed",
                                           message=err_msg, duration_ms=duration_ms)
        
        # Throttle
        await asyncio.sleep(2)

        # 9. Run Figure Association Lens (extract and associate PDF figures with notes)
        if self._is_paper_source(source) and fetched_content.get("pdf_bytes"):
            start_time = time.time()
            await self._log_event(source.id, "lens_started", "running", lens_key="figure_association", message="Extracting and associating figures")
            await self.db.commit()
            try:
                await self._generate_figure_associations(source, source_material, fetched_content.get("pdf_bytes"), batch_id=batch_id)
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "figure_association", "completed",
                                            message="Figures extracted and associated", duration_ms=duration_ms)
            except Exception as e:
                import traceback
                duration_ms = int((time.time() - start_time) * 1000)
                err_msg = str(e) or f"Error: {type(e).__name__}"
                logger.error(f"Figure association failed: {err_msg}\n{traceback.format_exc()}")
                await self._update_lens_log(source.id, "figure_association", "failed",
                                           message=err_msg, duration_ms=duration_ms)
        
        await self.db.commit()
        
        # 8. Mark the initial sync log as completed
        # We need to re-fetch or update the log we created at the start
        # Since we didn't keep the ID, let's find the running sync_started log
        stmt_log = (
            select(SourceLog)
            .where(
                SourceLog.source_id == source.id,
                SourceLog.event_type == "sync_started",
                SourceLog.status == "running"
            )
            .order_by(SourceLog.created_at.desc())
            .limit(1)
        )
        res_log = await self.db.execute(stmt_log)
        init_log = res_log.scalar_one_or_none()
        
        if init_log:
            init_log.status = "completed"
            init_log.event_type = "sync_completed"
            init_log.message = "Source processing finished successfully"
            init_log.duration_ms = int((time.time() - process_start_time) * 1000) # approximate total time
        
        # Update source status to COMPLETED
        source.status = "COMPLETED"
        await self.db.commit()

        logger.info(f"Finished processing source {source_id}")

    async def _fetch_source_content(self, source: Source) -> Dict[str, Any]:
        """
        Fetches content from source. Returns dict with 'text', 'base64_data', 'mime_type'.
        """
        # MVP: Basic request support if it is a URL
        url = source.connection_config.get("url") or source.connection_config.get("base_url")
        if not url:
            return {}
            
        if "arxiv.org" in url:
            try:
                import requests
                import base64
                
                # Normalize to PDF URL
                # e.g. https://arxiv.org/abs/2310.00000 -> https://arxiv.org/pdf/2310.00000.pdf
                pdf_url = url.replace("/abs/", "/pdf/")
                if not pdf_url.endswith(".pdf"):
                    pdf_url += ".pdf"
                
                # Download
                logger.info(f"Downloading PDF from {pdf_url}")
                response = requests.get(pdf_url)
                if response.status_code == 200:
                    pdf_bytes = response.content
                    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
                    return {
                        "text": None, # No text extraction needed for this mode
                        "base64_data": base64_pdf,
                        "mime_type": "application/pdf",
                        "pdf_bytes": pdf_bytes  # Keep raw bytes for figure extraction
                    }
                else:
                    logger.error(f"Failed to download PDF: {response.status_code}")
                    return {}
            except Exception as e:
                logger.error(f"Failed to fetch arxiv: {e}")
                return {}
        
        return {}

    def _is_paper_source(self, source: Source) -> bool:
        """
        Detect if the source is an academic paper (arxiv, etc.).
        """
        url = source.connection_config.get("url", "") or ""
        # Detect arxiv papers
        if "arxiv.org" in url:
            return True
        # Can extend to detect other paper sources (semanticscholar, etc.)
        return False

    async def _generate_reading_notes(self, source: Source, source_data: SourceData, source_material: SourceMaterial):
        """
        Generate reading notes cards from a paper source.
        Creates 9 structured notes with batch_id linking them together.
        """
        logger.info(f"Generating reading notes for source {source.id}")
        
        lens = get_reading_notes_lens()
        artifact = await self.run_lens(source_data, lens)
        notes = artifact.content  # Should be list of {title, content}
        
        # Helper: Unpack if wrapped in a dict key (common LLM behavior)
        if isinstance(notes, dict):
            for key in ["notes", "sections", "parts", "content"]:
                if key in notes and isinstance(notes[key], list):
                    notes = notes[key]
                    break

        # Helper: Parse if string (fallback if run_lens failed to parse)
        if isinstance(notes, str):
            try:
                notes = self._parse_json_robust(notes)
            except Exception as e:
                logger.warning(f"Failed to parse string notes as JSON: {str(e)}")
                # Log a snippet of the failed string for debugging
                logger.warning(f"Failed content snippet: {notes[:200]}")

        if not isinstance(notes, list):
            raise ValueError(f"Reading notes lens returned non-list data: {type(notes)} - {str(notes)[:100]}...")
        
        # Create batch_id to link all notes together
        batch_id = uuid_module.uuid4()
        cards_created = 0
        
        for index, note in enumerate(notes, start=1):
            if not isinstance(note, dict) or "title" not in note or "content" not in note:
                logger.warning(f"Skipping invalid note at index {index}: {note}")
                continue
                
            card = Card(
                owner_id=source.user_id,
                source_material_id=source_material.id,
                type="reading_note",
                content={
                    "question": note["title"],  # Descriptive headline
                    "answer": note["content"],  # Markdown content
                },
                status=CardStatus.PENDING,
                batch_id=batch_id,
                batch_index=index,
            )
            self.db.add(card)
            cards_created += 1
        
        if cards_created == 0:
            raise ValueError("No valid reading notes could be generated from the lens output.")

        await self.db.commit()
        logger.info(f"Generated {cards_created} reading notes for source {source.id} with batch_id {batch_id}")
        return batch_id


    async def _generate_study_quiz(self, source: Source, source_data: SourceData, source_material: SourceMaterial):
        """
        Generate study quiz and flashcards.
        """
        logger.info(f"Generating study quiz for source {source.id}")
        
        lens = get_study_quiz_lens()
        artifact = await self.run_lens(source_data, lens)
        result = artifact.content
        
        if not isinstance(result, dict) or "flashcards" not in result:
             raise ValueError("Study Quiz lens returned invalid format")
             
        batch_id = uuid_module.uuid4()
        cards_created = 0
            
        # 1. Create Flashcards
            
        # 2. Create Flashcards
        for index, item in enumerate(result.get("flashcards", []), start=1):
            if "question" not in item or "answer" not in item:
                continue
                
            card = Card(
                owner_id=source.user_id,
                source_material_id=source_material.id,
                type="flashcard",
                content={
                    "question": item["question"],
                    "answer": item["answer"]
                },
                status=CardStatus.PENDING,
                batch_id=batch_id,
                batch_index=index
            )
            self.db.add(card)
            cards_created += 1
            
        await self.db.commit()
        logger.info(f"Generated {cards_created} cards (guide + flashcards) for source {source.id}")

    async def _generate_figure_associations(self, source: Source, source_material: SourceMaterial, pdf_bytes: bytes, batch_id: UUID = None):
        """
        Extract figures from PDF and associate them with reading note cards.
        
        1. Extract all significant figures from PDF
        2. Save figures to local static directory
        3. Run LLM to determine which figures belong to which reading note sections
        4. Update the reading note cards with image paths
        """
        logger.info(f"Generating figure associations for source {source.id}")
        
        # 1. Extract figures
        from app.services.pdf_extractor import extract_figures_from_arxiv_source
        
        figures = []
        # Check if source is Arxiv and try source extraction first
        url = source.connection_config.get("url", "")
        arxiv_id = None
        if "arxiv.org/abs/" in url:
            arxiv_id = url.split("arxiv.org/abs/")[-1].split("v")[0] # Simple parse
        elif "arxiv.org/pdf/" in url:
            arxiv_id = url.split("arxiv.org/pdf/")[-1].replace(".pdf", "").split("v")[0]
            
        if arxiv_id:
            logger.info(f"Detected Arxiv ID {arxiv_id}, attempting source extraction...")
            try:
                figures = extract_figures_from_arxiv_source(arxiv_id)
            except Exception as e:
                logger.error(f"Arxiv source extraction failed: {e}")
                
        # Fallback to PDF extraction if no figures found from source
        if not figures:
            logger.info("Falling back to standard PDF extraction...")
            try:
                figures = extract_figures_from_pdf(pdf_bytes)
            except Exception as e:
                logger.error(f"Failed to extract figures from PDF: {e}")
                return
        
        if not figures:
            logger.info(f"No significant figures found in PDF/Source for source {source.id}")
            return
        
        # 2. Save figures to local storage
        saved_paths = save_figures_to_local(str(source.id), figures)
        if not saved_paths:
            logger.warning(f"Failed to save any figures for source {source.id}")
            return
        
        logger.info(f"Saved {len(saved_paths)} figures for source {source.id}")
        
        # 3. Run Figure Association lens to match figures to notes
        figure_info = get_figure_info_for_prompt(figures)
        
        # 2b. Fetch reading note cards EARLY for context construction
        stmt = select(Card).where(
            Card.source_material_id == source_material.id,
            Card.type == "reading_note"
        )
        
        if batch_id:
            logger.info(f"Filtering reading notes by batch_id: {batch_id}")
            stmt = stmt.where(Card.batch_id == batch_id)
            
        stmt = stmt.order_by(Card.batch_index)

        result = await self.db.execute(stmt)
        reading_note_cards = result.scalars().all()
        
        if not reading_note_cards:
            logger.warning(f"No reading note cards found for source material {source_material.id}, cannot associate figures.")
            return

        # Format reading notes for context
        notes_text = "Reading Notes Content:\n\n"
        for card in reading_note_cards:
             if card.content:
                 title = card.content.get("question", "Untitled")
                 content = card.content.get("answer", "")
                 notes_text += f"[Section {card.batch_index}] {title}\n{content}\n\n"
        
        combined_text = f"{notes_text}\n\nExtracted Figures Info:\n{figure_info}"

        # 4. Optimize images for Gemini
        from app.services.pdf_extractor import optimize_images_for_gemini
        optimized_images = optimize_images_for_gemini(figures)
        logger.info(f"Optimized {len(optimized_images)} images for multimodal request")

        # Create SourceData for the lens
        from app.core.lens import SourceData
        source_data = SourceData(
            id=str(source.id),
            text=combined_text,  # Combine notes and figure info (text context)
            images=optimized_images, # Actual image data for multimodal reasoning
            metadata={"title": source.name}
        )
        
        lens = get_figure_association_lens()
        try:
            artifact = await self.run_lens(source_data, lens)
            associations = artifact.content
        except Exception as e:
            logger.error(f"Figure association lens failed: {e}")
            # Fall back to hardcoded association (figures 0-1 to Overview of Approach section 2)
            associations = {"associations": [{"section_index": 2, "figure_indices": [0, 1] if len(figures) > 1 else [0]}]}
        
        # Parse associations
        if isinstance(associations, dict) and "associations" in associations:
            assoc_list = associations["associations"]
        else:
            logger.warning(f"Unexpected associations format: {type(associations)}")
            return
        
        # 5. Update cards with associated figure paths
        
        # 5. Update cards with associated figure paths
        cards_updated = 0
        for assoc in assoc_list:
            section_index = assoc.get("section_index")
            figure_indices = assoc.get("figure_indices", [])
            
            if not section_index or not figure_indices:
                continue
            
            # Find the card matching this section index (batch_index corresponds to section)
            matching_card = None
            for card in reading_note_cards:
                if card.batch_index == section_index:
                    matching_card = card
                    break
            
            if not matching_card:
                logger.debug(f"No card found for section_index {section_index}")
                continue
            
            # Get image paths for these figure indices
            image_paths = []
            for fig_idx in figure_indices:
                if 0 <= fig_idx < len(saved_paths):
                    image_paths.append(saved_paths[fig_idx])
            
            if image_paths:
                # Update card content with images
                new_content = dict(matching_card.content)
                new_content["images"] = image_paths
                matching_card.content = new_content
                cards_updated += 1
                logger.debug(f"Added {len(image_paths)} images to card {matching_card.id} (section {section_index})")
        
        await self.db.commit()
        logger.info(f"Updated {cards_updated} reading note cards with figure associations for source {source.id}")

