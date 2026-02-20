"""
LLM operator base — handles prompt rendering, LLM call, and JSON parsing.
Concrete LLM operators only need to declare ports and implement ``_map_output``.
"""

from __future__ import annotations

import json
import logging
import re
import time
from abc import abstractmethod
from typing import Any, Optional

from openai import AsyncOpenAI

from app.core.config import get_settings
from app.core.llm_monitor import LLMMonitor
from app.lenses.registry import load_prompt_config
from app.operators.base import OperatorBase, RunContext

logger = logging.getLogger(__name__)


class LLMOperator(OperatorBase):
    """
    Base class for LLM-powered operators.

    Subclasses set:
        prompt_file   – name of the YAML in lenses/prompts/ (without .yaml)
        output_schema – optional JSON Schema dict for structured output
    and implement ``_map_output`` to route the parsed LLM response to output ports.
    """

    kind = "llm"
    prompt_file: str                          # e.g. "default_summary"
    output_schema: Optional[dict] = None

    # ------------------------------------------------------------------
    # execute
    # ------------------------------------------------------------------

    async def execute(
        self,
        inputs: dict[str, Any],
        context: RunContext,
    ) -> dict[str, Any]:
        self.validate_inputs(inputs)

        config = load_prompt_config(self.prompt_file)
        messages = self._render_messages(config, inputs)

        settings = get_settings()
        client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
        )
        model = settings.llm_model

        kwargs: dict[str, Any] = {
            "temperature": 0.7,
            "timeout": 180,
        }
        if self.output_schema:
            kwargs["response_format"] = {"type": "json_object"}

        from tenacity import (
            retry,
            stop_after_attempt,
            wait_exponential,
            retry_if_exception,
            before_sleep_log,
        )
        from openai import APIStatusError, AuthenticationError

        def _is_retryable(exc: BaseException) -> bool:
            """Only retry on 429 (rate limit) and 5xx (server error)."""
            if isinstance(exc, AuthenticationError):
                return False
            if isinstance(exc, APIStatusError):
                return exc.status_code == 429 or exc.status_code >= 500
            return False

        @retry(
            wait=wait_exponential(multiplier=1, min=2, max=60),
            stop=stop_after_attempt(5),
            retry=retry_if_exception(_is_retryable),
            before_sleep=before_sleep_log(logger, logging.WARNING),
        )
        async def _call(m, msgs, **kw):
            return await client.chat.completions.create(model=m, messages=msgs, **kw)

        logger.info("LLM REQUEST [operator=%s] model=%s", self.key, model)

        from uuid import UUID

        async with LLMMonitor(
            db=context.db,
            source_id=UUID(context.source_id) if context.source_id else None,
            lens_key=self.key,
            model=model,
        ) as llm_log:
            llm_log.record_request(messages, **kwargs)
            start = time.time()
            response = await _call(model, messages, **kwargs)
            llm_log.record_response(response)

        content = response.choices[0].message.content
        logger.info("LLM RESPONSE [operator=%s]: %s...", self.key, content[:200])

        if self.output_schema:
            content = self._parse_json_robust(content)

        return self._map_output(content)

    # ------------------------------------------------------------------
    # Prompt rendering
    # ------------------------------------------------------------------

    def _render_messages(
        self,
        config: dict,
        inputs: dict[str, Any],
    ) -> list[dict]:
        system_prompt = config["system_prompt"]
        user_prompt = config["user_prompt_template"]

        class SafeDict(dict):
            def __missing__(self, key):
                return "{" + key + "}"

        safe_inputs = SafeDict()
        for k, v in inputs.items():
            if k == "images":
                continue
            if isinstance(v, (dict, list)):
                safe_inputs[k] = json.dumps(v, indent=2, ensure_ascii=False)
            else:
                safe_inputs[k] = str(v)

        user_prompt = user_prompt.format_map(safe_inputs)

        user_content: list[dict] = [{"type": "text", "text": user_prompt}]

        # Attach images if present
        images: list[bytes] | None = inputs.get("images")
        if images:
            import base64 as b64

            for img_bytes in images:
                data_url = f"data:image/jpeg;base64,{b64.b64encode(img_bytes).decode()}"
                user_content.append(
                    {"type": "image_url", "image_url": {"url": data_url}}
                )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    # ------------------------------------------------------------------
    # JSON parsing (ported from RunnerService._parse_json_robust)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json_robust(content: str) -> Any:
        # First, escape unescaped backslashes inside JSON strings
        content = re.sub(
            r'(?<!\\)\\(?![\\"/bfnrt]|u[0-9a-fA-F]{4})', r"\\\\", content
        )

        # 1. Try to extract from ```json block
        match = re.search(r'```(?:json)?\s*(.*?)```', content, re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            try:
                return json.loads(extracted)
            except Exception:
                pass # fallthrough
        
        # 2. Find first { or [
        start_idx = -1
        for i, c in enumerate(content):
            if c in ('{', '['):
                start_idx = i
                break
                
        if start_idx == -1:
            return json.loads(content) # will fail but raise normal error
            
        extracted = content[start_idx:]
        
        # 3. Use raw_decode to parse just the JSON part and ignore trailing chars
        decoder = json.JSONDecoder()
        try:
            obj, idx = decoder.raw_decode(extracted)
            return obj
        except Exception:
            # fallback to naive parse
            pass
            
        return json.loads(extracted)

    # ------------------------------------------------------------------
    # Abstract: subclass maps LLM output → output port dict
    # ------------------------------------------------------------------

    @abstractmethod
    def _map_output(self, content: Any) -> dict[str, Any]:
        """Map parsed LLM response to ``{port_key: value}``."""
        ...
