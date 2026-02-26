"""
Seed system pipeline templates on startup.

Called from app/main.py lifespan to ensure the `paper_default` template
exists in the database. Idempotent — skips if already present.
"""
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import PipelineTemplate

logger = logging.getLogger(__name__)

# Fixed UUID for the system paper_default template — ensures idempotency
PAPER_DEFAULT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


def _paper_default_definition() -> dict:
    """
    Build the paper_default pipeline definition dict from the live Pipeline object.
    This keeps the seed data in sync with pipelines.py automatically.
    """
    from app.operators.pipelines import paper_default

    pipeline = paper_default()
    return {
        "steps": [
            {
                "key": s.key,
                "label": s.label,
                "position": s.position,
                "operators": [
                    {
                        "id": op.id,
                        "operator_key": op.operator_key,
                        "config_overrides": op.config_overrides,
                    }
                    for op in s.operators
                ],
            }
            for s in pipeline.steps
        ],
        "edges": [
            {
                "id": e.id,
                "source_op": e.source_op,
                "source_port": e.source_port,
                "target_op": e.target_op,
                "target_port": e.target_port,
            }
            for e in pipeline.edges
        ],
    }


async def seed_system_pipelines(db: AsyncSession) -> None:
    """
    Upsert the system `paper_default` pipeline template.
    
    Called on every startup. If the template already exists, updates its
    definition to match the latest code (keeps the DAG in sync).
    """
    stmt = select(PipelineTemplate).where(PipelineTemplate.id == PAPER_DEFAULT_ID)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    definition = _paper_default_definition()
    now = datetime.now(timezone.utc)

    if existing:
        # Update definition to match latest code
        existing.definition = definition
        existing.updated_at = now
        logger.info("Updated system pipeline template: paper_default")
    else:
        template = PipelineTemplate(
            id=PAPER_DEFAULT_ID,
            user_id=None,
            name="Paper Processing (Default)",
            description="Default pipeline for processing academic papers: fetch PDF → generate summary, reading notes, flashcards → extract and associate figures.",
            is_system=True,
            definition=definition,
            created_at=now,
            updated_at=now,
        )
        db.add(template)
        logger.info("Created system pipeline template: paper_default")

    await db.commit()
