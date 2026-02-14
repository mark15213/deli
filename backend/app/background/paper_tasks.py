import logging
import traceback
import asyncio
from uuid import UUID
from app.core.database import async_session_maker
from app.services.runner_service import RunnerService

logger = logging.getLogger(__name__)

# Limit concurrent paper processing tasks to prevent resource exhaustion
_concurrency_limit = asyncio.Semaphore(3)

async def process_paper_background(source_id: UUID):
    """
    Background task to process a new paper source.
    Manages its own DB session.
    """
    async with _concurrency_limit:
        try:
            logger.info(f"[BACKGROUND] Starting processing for source {source_id}")
            async with async_session_maker() as session:
                runner = RunnerService(session)
                await runner.process_new_source(source_id)
            logger.info(f"[BACKGROUND] Successfully completed processing for source {source_id}")
        except Exception as e:
            logger.error(f"[BACKGROUND] Error processing source {source_id}: {str(e)}")
            logger.error(f"[BACKGROUND] Traceback: {traceback.format_exc()}")
            
            # Write failure log to DB so frontend stops polling
            try:
                # Create a NEW session for logging to ensure it doesn't conflict with any previous session state
                async with async_session_maker() as log_session:
                    from app.models.models import SourceLog, Source
                    
                    # Update Source status to FAILED
                    from sqlalchemy import select
                    stmt = select(Source).where(Source.id == source_id)
                    res = await log_session.execute(stmt)
                    source_obj = res.scalar_one_or_none()
                    if source_obj:
                        source_obj.status = "FAILED"
                        source_obj.error_log = f"Background processing failed: {str(e)}"
                    
                    error_log = SourceLog(
                        source_id=source_id,
                        event_type="error",
                        status="failed",
                        message=f"Background processing failed: {str(e)}",
                        extra_data={"traceback": traceback.format_exc()}
                    )
                    log_session.add(error_log)
                    await log_session.commit()
            except Exception as log_err:
                 # Last resort logging
                 logger.error(f"[BACKGROUND] Failed to write error log to DB: {log_err}")

            # Don't re-raise - background tasks should not crash the app


