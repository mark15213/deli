"""figure_association operator — matches PDF figures to reading note sections."""

from typing import Any

from app.operators.base import Port, PortType
from app.operators.registry import register_operator
from app.operators.llm import LLMOperator


@register_operator
class FigureAssociationOperator(LLMOperator):
    key = "figure_association"
    name = "Figure Association"
    description = "Associates extracted PDF figures with reading note sections."
    prompt_file = "figure_association"
    output_schema = {
        "type": "object",
        "properties": {
            "associations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "section_index": {"type": "integer", "minimum": 1, "maximum": 9},
                        "figure_indices": {"type": "array", "items": {"type": "integer"}},
                        "reason": {"type": "string"},
                    },
                    "required": ["section_index", "figure_indices"],
                },
            },
        },
        "required": ["associations"],
    }

    input_ports = [
        Port(key="notes", type=PortType.JSON, description="Reading notes data"),
        Port(key="images", type=PortType.IMAGES, description="Optimised figure image bytes", required=False),
    ]
    output_ports = [
        Port(key="associations", type=PortType.JSON, description="Section-to-figure mapping"),
    ]

    def _map_output(self, content: Any) -> dict[str, Any]:
        if isinstance(content, dict) and "associations" in content:
            return {"associations": content["associations"]}
        return {"associations": content}
