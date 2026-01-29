import logging
import traceback
from uuid import UUID
from app.core.database import async_session_maker
from app.services.runner_service import RunnerService

logger = logging.getLogger(__name__)

async def process_paper_background(source_id: UUID):
    """
    Background task to process a new paper source.
    Manages its own DB session.
    """
    try:
        logger.info(f"[BACKGROUND] Starting processing for source {source_id}")
        async with async_session_maker() as session:
            runner = RunnerService(session)
            await runner.process_new_source(source_id)
        logger.info(f"[BACKGROUND] Successfully completed processing for source {source_id}")
    except Exception as e:
        logger.error(f"[BACKGROUND] Error processing source {source_id}: {str(e)}")
        logger.error(f"[BACKGROUND] Traceback: {traceback.format_exc()}")
        # Don't re-raise - background tasks should not crash the app

