"""save_summary handler — persists the summary to SourceMaterial.rich_data."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models.models import SourceMaterial
from app.operators.base import RunContext

logger = logging.getLogger(__name__)


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    summary = inputs["summary"]

    stmt = select(SourceMaterial).where(
        SourceMaterial.id == UUID(context.source_material_id)
    )
    result = await context.db.execute(stmt)
    sm = result.scalar_one_or_none()

    if sm:
        new_data = dict(sm.rich_data or {})
        new_data["summary"] = summary
        new_data.setdefault("suggestions", [])
        sm.rich_data = new_data
        await context.db.commit()
        logger.info("Saved summary to source_material %s", context.source_material_id)
    else:
        logger.warning("SourceMaterial %s not found, summary not saved", context.source_material_id)

    return {"done": "ok"}
