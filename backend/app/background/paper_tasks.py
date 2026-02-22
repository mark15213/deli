"""
Background task — process a newly submitted paper source using PipelineEngine.

Replaces the old RunnerService linear orchestration with the DAG-based
operator pipeline (pdf_fetch → summary / reading_notes / quiz / figures).
"""

import asyncio
import logging
import traceback
from uuid import UUID

from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.models import Source, SourceMaterial, SourceLog

logger = logging.getLogger(__name__)

# Limit concurrent paper processing tasks to prevent resource exhaustion
_concurrency_limit = asyncio.Semaphore(3)


async def process_paper_background(source_id: UUID):
    """
    Background task to process a new paper source.
    Manages its own DB session and uses PipelineEngine.
    """
    async with _concurrency_limit:
        try:
            logger.info("[BACKGROUND] Starting processing for source %s", source_id)
            async with async_session_maker() as session:
                await _run_pipeline(session, source_id)
            logger.info("[BACKGROUND] Successfully completed processing for source %s", source_id)
        except Exception as e:
            logger.error("[BACKGROUND] Error processing source %s: %s", source_id, e)
            logger.error("[BACKGROUND] Traceback: %s", traceback.format_exc())

            # Write failure log to DB so frontend stops polling
            try:
                async with async_session_maker() as log_session:
                    stmt = select(Source).where(Source.id == source_id)
                    res = await log_session.execute(stmt)
                    source_obj = res.scalar_one_or_none()
                    if source_obj:
                        source_obj.status = "FAILED"
                        source_obj.error_log = f"Background processing failed: {e}"

                    error_log = SourceLog(
                        source_id=source_id,
                        event_type="error",
                        status="failed",
                        message=f"Background processing failed: {e}",
                        extra_data={"traceback": traceback.format_exc()},
                    )
                    log_session.add(error_log)
                    await log_session.commit()
            except Exception as log_err:
                logger.error("[BACKGROUND] Failed to write error log to DB: %s", log_err)


async def _run_pipeline(session, source_id: UUID):
    """Core logic: fetch source, ensure material, run pipeline."""
    from app.operators.engine import PipelineEngine
    from app.operators.pipelines import paper_default
    from app.operators.base import RunContext

    # 1. Fetch Source ----------------------------------------------------------
    stmt = select(Source).where(Source.id == source_id)
    result = await session.execute(stmt)
    source = result.scalar_one_or_none()

    if not source:
        logger.error("Source %s not found", source_id)
        return

    # 2. Update status to PROCESSING -------------------------------------------
    if source.status != "PROCESSING":
        source.status = "PROCESSING"
        await session.commit()

    # 3. Resolve URL -----------------------------------------------------------
    url = source.connection_config.get("url") or source.connection_config.get("base_url")
    if not url:
        source.status = "FAILED"
        source.error_log = "No URL configured for source"
        await session.commit()
        return

    # 4. Ensure SourceMaterial exists ------------------------------------------
    stmt_mat = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
    res_mat = await session.execute(stmt_mat)
    source_material = res_mat.scalars().first()

    if not source_material:
        external_id = url
        # Check if a material with this external_id already exists for the user
        stmt_exist = select(SourceMaterial).where(
            SourceMaterial.user_id == source.user_id,
            SourceMaterial.external_id == external_id,
        )
        res_exist = await session.execute(stmt_exist)
        existing_material = res_exist.scalars().first()

        if existing_material:
            logger.info("Found existing material, re-linking to source %s", source.id)
            source_material = existing_material
            if source_material.source_id != source.id:
                source_material.source_id = source.id
                await session.flush()
        else:
            source_material = SourceMaterial(
                user_id=source.user_id,
                source_id=source.id,
                external_id=external_id,
                title=source.name,
                rich_data={},
            )
            session.add(source_material)
            await session.flush()  # get ID

    # 5. Build context and run pipeline ----------------------------------------
    context = RunContext(
        db=session,
        source_id=str(source.id),
        user_id=str(source.user_id),
        source_material_id=str(source_material.id),
    )

    pipeline = paper_default()
    initial_inputs = {"url": url}

    engine = PipelineEngine()
    op_outputs, failed_ops = await engine.run(pipeline, initial_inputs, context)

    # 6. Mark completed or failed ----------------------------------------------
    await session.execute(select(Source).where(Source.id == source_id))  # refresh
    
    if failed_ops:
        source.status = "FAILED"
        source.error_log = f"Pipeline failed on operators: {', '.join(failed_ops)}"
        log_event_type = "sync_failed"
        log_status = "failed"
        log_message = f"Source processing failed on operators: {', '.join(failed_ops)}"
    else:
        source.status = "COMPLETED"
        log_event_type = "sync_completed"
        log_status = "completed"
        log_message = "Source processing finished successfully"

    log = SourceLog(
        source_id=source_id,
        event_type=log_event_type,
        status=log_status,
        message=log_message,
    )
    session.add(log)
    await session.commit()

    if failed_ops:
        logger.error("Finished processing source %s with errors", source_id)
    else:
        logger.info("Finished processing source %s", source_id)
