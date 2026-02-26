# LLM Call Monitoring and Logging
import os
import json
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.models import SourceLog

logger = logging.getLogger(__name__)


class LLMCallLog:
    """Container for a single LLM call's metrics."""

    def __init__(
        self,
        source_id: Optional[UUID] = None,
        lens_key: Optional[str] = None,
        model: str = "",
    ):
        self.source_id = source_id
        self.lens_key = lens_key
        self.model = model
        self.start_time = time.time()
        self.end_time: Optional[float] = None

        # Token usage
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.total_tokens: int = 0

        # Request/Response data
        self.messages: list = []
        self.response_content: str = ""
        self.error: Optional[str] = None

    def record_request(self, messages: list, **kwargs):
        """Record the request details."""
        self.messages = messages

    def record_response(self, response):
        """Extract metrics from OpenAI response object."""
        self.end_time = time.time()

        # Extract token usage
        if hasattr(response, 'usage') and response.usage:
            self.prompt_tokens = response.usage.prompt_tokens
            self.completion_tokens = response.usage.completion_tokens
            self.total_tokens = response.usage.total_tokens

        # Extract response content
        if hasattr(response, 'choices') and response.choices:
            self.response_content = response.choices[0].message.content or ""

    def record_error(self, error: Exception):
        """Record error information."""
        self.end_time = time.time()
        self.error = str(error)

    @property
    def duration_ms(self) -> int:
        """Calculate duration in milliseconds."""
        if self.end_time:
            return int((self.end_time - self.start_time) * 1000)
        return 0

    @staticmethod
    def _sanitize_for_pg(value: Any) -> Any:
        """Recursively strip \\u0000 null bytes from strings (PostgreSQL rejects them in JSONB)."""
        if isinstance(value, str):
            return value.replace("\x00", "")
        if isinstance(value, dict):
            return {k: LLMCallLog._sanitize_for_pg(v) for k, v in value.items()}
        if isinstance(value, list):
            return [LLMCallLog._sanitize_for_pg(item) for item in value]
        return value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage (sanitised for PostgreSQL)."""
        data = {
            "model": self.model,
            "duration_ms": self.duration_ms,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "messages": self._truncate_messages(self.messages),
            "response_preview": self.response_content[:500] if self.response_content else "",
            "error": self.error,
        }
        return self._sanitize_for_pg(data)

    def _truncate_messages(self, messages: list, max_length: int = 1000) -> list:
        """Truncate message content for storage."""
        truncated = []
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", "")
                if isinstance(content, str) and len(content) > max_length:
                    truncated.append({
                        **msg,
                        "content": content[:max_length] + "... [truncated]"
                    })
                else:
                    truncated.append(msg)
            else:
                truncated.append(msg)
        return truncated

    async def save_to_db(self, db: AsyncSession):
        """Save this LLM call log to database."""
        if not self.source_id:
            logger.warning("Cannot save LLM log without source_id")
            return

        log = SourceLog(
            source_id=self.source_id,
            event_type="llm_call",
            status="completed" if not self.error else "failed",
            lens_key=self.lens_key,
            message=f"LLM call: {self.model} ({self.total_tokens} tokens)",
            duration_ms=self.duration_ms,
            extra_data=self.to_dict()
        )
        db.add(log)
        # Don't commit here - let caller handle transaction

    def save_debug_log(self):
        """Save full un-truncated LLM call details to a local JSON file if enabled."""
        settings = get_settings()
        if not settings.llm_debug_logging:
            return
            
        try:
            log_dir = "logs/llm"
            os.makedirs(log_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            lens_name = self.lens_key or "unknown"
            filename = os.path.join(log_dir, f"{timestamp}_{self.model}_{lens_name}.json")
            
            debug_data = {
                "source_id": str(self.source_id) if self.source_id else None,
                "lens_key": self.lens_key,
                "model": self.model,
                "duration_ms": self.duration_ms,
                "error": self.error,
                "messages": self.messages,
                "response_content": self.response_content,
                "prompt_tokens": self.prompt_tokens,
                "completion_tokens": self.completion_tokens,
                "total_tokens": self.total_tokens,
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(debug_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Wrote LLM debug log to {filename}")
        except Exception as e:
            logger.error(f"Failed to write LLM debug log: {e}")

class LLMMonitor:
    """Context manager for monitoring LLM calls."""

    def __init__(
        self,
        db: AsyncSession,
        source_id: Optional[UUID] = None,
        lens_key: Optional[str] = None,
        model: str = "",
    ):
        self.db = db
        self.log = LLMCallLog(source_id=source_id, lens_key=lens_key, model=model)

    def __enter__(self):
        return self.log

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log.record_error(exc_val)
        return False

    async def __aenter__(self):
        return self.log

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.log.record_error(exc_val)

        # Save to database
        await self.log.save_to_db(self.db)

        # Save debug log if enabled
        self.log.save_debug_log()

        # Log to console
        if self.log.error:
            logger.error(
                f"LLM call failed: {self.log.lens_key or 'unknown'} "
                f"({self.log.duration_ms}ms) - {self.log.error}"
            )
        else:
            logger.info(
                f"LLM call completed: {self.log.lens_key or 'unknown'} "
                f"({self.log.duration_ms}ms, {self.log.total_tokens} tokens)"
            )

        return False
