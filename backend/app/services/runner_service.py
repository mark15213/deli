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
from app.models.models import Source, SourceMaterial
from app.lenses.registry import get_default_summary_lens, get_profiler_lens

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

        # 2. Extract Content (Text or Base64)
        fetched_content = await self._fetch_source_content(source)
        
        if not fetched_content:
            logger.warning(f"No content extracted for source {source_id}")
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
        # Default Summary Lens expects {text}. If we give it a PDF, we might need to adjust the prompt or Lens.
        # But our new run_lens handles the substitution of {text} -> "this document" if text is missing.
        summary_lens = get_default_summary_lens()
        try:
            summary_artifact = await self.run_lens(source_data, summary_lens)
        except Exception as e:
            logger.error(f"Lens summary failed: {e}")
            summary_artifact = Artifact(lens_key="default_summary", source_id=str(source.id), content={"error": str(e)}, created_at=time.time())
        
        # 5. Run Profiler Lens
        profiler_lens = get_profiler_lens()
        try:
            profiler_artifact = await self.run_lens(source_data, profiler_lens)
        except Exception as e:
            logger.error(f"Lens profiler failed: {e}")
            profiler_artifact = Artifact(lens_key="profiler_meta", source_id=str(source.id), content={"error": str(e)}, created_at=time.time())
        
        # 6. Persist to SourceMaterial
        # Find existing or create
        stmt_mat = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
        res_mat = await self.db.execute(stmt_mat)
        source_material = res_mat.scalars().first()
        
        if not source_material:
            # Check if one exists with same external_id (re-ingestion) to avoid unique constraint error
            # uq_source_user_extid
            external_id = source.connection_config.get("url", "unknown")
            stmt_exist = select(SourceMaterial).where(
                SourceMaterial.user_id == source.user_id,
                SourceMaterial.external_id == external_id
            )
            res_exist = await self.db.execute(stmt_exist)
            existing_material = res_exist.scalars().first()
            
            if existing_material:
                logger.info(f"Fonud existing material used by another source, re-linking to source {source.id}")
                source_material = existing_material
                # Re-link? Or just update content? 
                # If we re-link, the old source loses its material reference (if 1:1). 
                # But since we are creating new source every time, this is likely what we want.
                source_material.source_id = source.id
            else:
                # Create new
                 source_material = SourceMaterial(
                    user_id=source.user_id,
                    source_id=source.id,
                    external_id=external_id,
                    title=source.name,
                    rich_data={}
                )
                 self.db.add(source_material)
        
        # Update rich_data
        # Ensure dict exists
        if source_material.rich_data is None:
            source_material.rich_data = {}
            
        # We need to clone the dict to ensure SQLAlchemy detects change if it's mutable
        new_data = dict(source_material.rich_data)
        new_data["summary"] = summary_artifact.content
        new_data["suggestions"] = profiler_artifact.content
        
        source_material.rich_data = new_data
        
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
