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
                        "section_index": {"type": "integer", "minimum": 0, "maximum": 8},
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

    async def execute(self, inputs: dict[str, Any], context: "RunContext") -> dict[str, Any]:
        if "notes" not in inputs:
            # Support pipeline resumption where reading_notes step was skipped
            import uuid
            from sqlalchemy import select
            from app.models.models import Card

            stmt = (
                select(Card)
                .where(
                    Card.source_material_id == uuid.UUID(context.source_material_id),
                    Card.type == "reading_note",
                )
                .order_by(Card.batch_index)
            )
            cards = (await context.db.execute(stmt)).scalars().all()
            if cards:
                inputs["notes"] = [c.content for c in cards]
            else:
                inputs["notes"] = []

        if not inputs.get("images"):
            from app.core.config import get_settings
            from pathlib import Path
            import re
            settings = get_settings()
            source_dir = Path(settings.storage_dir) / "images" / str(context.source_id)
            if source_dir.exists():
                def sort_key(p):
                    match = re.search(r"(\d+)", p.name)
                    return int(match.group(1)) if match else 999
                files = sorted([f for f in source_dir.iterdir() if f.is_file() and not f.name.startswith('.')], key=sort_key)
                inputs["images"] = [f.read_bytes() for f in files]

        return await super().execute(inputs, context)
