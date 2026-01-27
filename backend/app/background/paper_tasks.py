import logging
from uuid import UUID
from app.core.database import async_session_maker
from app.services.runner_service import RunnerService

logger = logging.getLogger(__name__)

async def process_paper_background(source_id: UUID):
    """
    Background task to process a new paper source.
    Manages its own DB session.
    """
    async with async_session_maker() as session:
        runner = RunnerService(session)
        await runner.process_new_source(source_id)
