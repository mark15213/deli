"""reading_notes operator — 9-section structured research notes."""

from typing import Any

from app.operators.base import Port, PortType
from app.operators.registry import register_operator
from app.operators.llm import LLMOperator


@register_operator
class ReadingNotesOperator(LLMOperator):
    key = "reading_notes"
    name = "Reading Notes"
    description = "Generates 9 structured research report sections from a paper."
    prompt_file = "reading_notes"
    output_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["title", "content"],
        },
        "minItems": 9,
        "maxItems": 9,
    }

    input_ports = [
        Port(key="text", type=PortType.TEXT, description="Paper full text"),
    ]
    output_ports = [
        Port(key="notes", type=PortType.JSON, description="List of {title, content} note sections"),
    ]

    def _map_output(self, content: Any) -> dict[str, Any]:
        notes = content
        # Unwrap if LLM wrapped in a dict
        if isinstance(notes, dict):
            for k in ("notes", "sections", "parts", "content"):
                if k in notes and isinstance(notes[k], list):
                    notes = notes[k]
                    break
        return {"notes": notes}
