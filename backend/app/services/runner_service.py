import logging
import time
import os
import json
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

from openai import OpenAI, AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.lens import SourceData, Lens, Artifact
from app.models.models import Source, SourceMaterial, Card, CardStatus, SourceLog
from app.lenses.registry import get_default_summary_lens, get_profiler_lens, get_reading_notes_lens
import uuid as uuid_module

logger = logging.getLogger(__name__)

class RunnerService:
    def __init__(self, db: AsyncSession):
        self.db = db
        # Initialize OpenAI client with custom base_url
        base_url = os.environ.get("OPENAI_BASE_URL", "http://127.0.0.1:8045/v1")
        # Do not load API key from source code
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("OPENAI_API_KEY environment variable is not set.")
            
        self.client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key
        )

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
            if message:
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

    async def run_lens(self, source_data: SourceData, lens: Lens) -> Artifact:
        """
        Execute a single Lens against a Source.
        """
        try:
            # Construct Prompt
            messages = []
            
            # System Prompt
            if lens.system_prompt:
                messages.append({"role": "system", "content": lens.system_prompt})
            
            # User Prompt
            user_content = []
            
            # Add text prompt (template filled or generic)
            # If text is available, format it into the template.
            # If only base64 is available, we use the template but maybe without {text} if it's just "Summarize this document".
            # But the template likely contains {text}. We should handle this.
            # For PDF chat, the text is the PDF itself. The prompt is the instruction.
            
            prompt_text = lens.user_prompt_template
            if source_data.text:
                 try:
                     prompt_text = prompt_text.format(text=source_data.text)
                 except KeyError:
                     # If template expects text but we don't have it, or vice versa
                     pass
            else:
                 # If no text (e.g. PDF only), we might need to strip {text} from template or just use the template as is if it doesn't have {text} variable
                 # A simple fallback:
                 if "{text}" in prompt_text:
                     prompt_text = prompt_text.replace("{text}", "this document")

            user_content.append({"type": "text", "text": prompt_text})

            if source_data.base64_data and source_data.mime_type:
                # Use image_url trick for PDF base64 (common proxy pattern for Gemini)
                # Ensure no newlines in base64
                clean_b64 = source_data.base64_data.replace("\n", "").replace("\r", "")
                
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{source_data.mime_type};base64,{clean_b64}"
                    }
                })
            
            messages.append({"role": "user", "content": user_content})
            
            model_name = lens.parameters.get("model", "gemini-3-flash")
            
            # DEBUG: Log payload
            logger.info(f"Sending to OpenAI: model={model_name}, messages={json.dumps(messages, default=str)}")
            
            # Generate
            start_time = time.time()
            
            # Use raw httpx to bypass OpenAI SDK validation for 'input_file' type
            api_url = f"{self.client.base_url}chat/completions"
            headers = {
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model_name,
                "messages": messages,
                "stream": False
            }
            
            # Remove /v1//v1 if double appended or ensure clean join
            # base_url usually ends with /v1/
            if not str(self.client.base_url).endswith("/"):
                 api_url = f"{self.client.base_url}/chat/completions"
            
            import httpx
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                resp = await http_client.post(api_url, headers=headers, json=payload)
                if resp.status_code != 200:
                    logger.error(f"OpenAI API Error {resp.status_code}: {resp.text}")
                resp.raise_for_status()
                response_data = resp.json()
            
            end_time = time.time()
            
            content = response_data["choices"][0]["message"]["content"]
            
            # If output_schema is JSON, try to parse
            if lens.output_schema:
                try:
                    # naive attempt to extract json if model wraps it in ```json ... ```
                    cleaned_content = content.replace("```json", "").replace("```", "").strip()
                    content = json.loads(cleaned_content)
                except Exception as e:
                    logger.warning(f"Failed to parse JSON output for lens {lens.key}: {e}")
            
            return Artifact(
                lens_key=lens.key,
                source_id=source_data.id,
                content=content, # This might be None if content is null?
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
            duration_ms = int((time.time() - start_time) * 1000)
            await self._update_lens_log(source.id, "default_summary", "failed",
                                       message=str(e), duration_ms=duration_ms)
            logger.error(f"Lens summary failed: {e}")
            summary_artifact = Artifact(lens_key="default_summary", source_id=str(source.id), content={"error": str(e)}, created_at=time.time())
        
        # 5. Run Profiler Lens
        profiler_lens = get_profiler_lens()
        start_time = time.time()
        await self._log_event(source.id, "lens_started", "running", lens_key="profiler_meta", message="Starting lens profiling")
        await self.db.commit()  # Commit so log is visible immediately
        try:
            profiler_artifact = await self.run_lens(source_data, profiler_lens)
            duration_ms = int((time.time() - start_time) * 1000)
            await self._update_lens_log(source.id, "profiler_meta", "completed",
                                       message="Lens suggestions generated", duration_ms=duration_ms)
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            await self._update_lens_log(source.id, "profiler_meta", "failed",
                                       message=str(e), duration_ms=duration_ms)
            logger.error(f"Lens profiler failed: {e}")
            profiler_artifact = Artifact(lens_key="profiler_meta", source_id=str(source.id), content={"error": str(e)}, created_at=time.time())
        
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
        if self._is_paper_source(source):
            start_time = time.time()
            await self._log_event(source.id, "lens_started", "running", lens_key="reading_notes", message="Generating reading notes")
            await self.db.commit()  # Commit so log is visible immediately
            try:
                await self._generate_reading_notes(source, source_data, source_material)
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "reading_notes", "completed",
                                           message="Reading notes generated", duration_ms=duration_ms)
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000)
                await self._update_lens_log(source.id, "reading_notes", "failed",
                                           message=str(e), duration_ms=duration_ms)
        
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
                        "mime_type": "application/pdf"
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

