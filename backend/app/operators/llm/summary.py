"""summary operator — TL;DR of a paper."""

from typing import Any

from app.operators.base import Port, PortType
from app.operators.registry import register_operator
from app.operators.llm import LLMOperator


@register_operator
class SummaryOperator(LLMOperator):
    key = "summary"
    name = "TL;DR Summary"
    description = "Generates a concise summary of the source content."
    prompt_file = "default_summary"
    output_schema = None  # free-form text

    input_ports = [
        Port(key="text", type=PortType.TEXT, description="Source text to summarise"),
    ]
    output_ports = [
        Port(key="summary", type=PortType.TEXT, description="Generated summary"),
    ]

    def _map_output(self, content: Any) -> dict[str, Any]:
        return {"summary": content if isinstance(content, str) else str(content)}
