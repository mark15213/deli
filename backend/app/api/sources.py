import uuid
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.api.deps import is_shared_mode
from app.models.models import User, Source
from app.schemas.source_schemas import SourceCreate, SourceUpdate, SourceResponse
from app.schemas.detect_schemas import DetectRequest, DetectResponse
from app.services.source_detector import source_detector
from app.schemas.source_schemas import SourceType

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("", response_model=List[SourceResponse])
async def get_sources(
    current_user: User = Depends(deps.get_current_user),
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve current user's sources.
    Only returns top-level sources (no parent). Child sources are accessed via parent.
    """
    from sqlalchemy import func
    
    # Get top-level sources only (parent_source_id is NULL)
    stmt = (
        select(Source)
        .options(selectinload(Source.source_materials))
        .where(Source.parent_source_id == None)
    )
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    stmt = stmt.offset(skip).limit(limit
    )
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    # Batch query for children counts (avoid N+1)
    source_ids = [s.id for s in sources]
    children_counts = {}
    if source_ids:
        count_stmt = (
            select(Source.parent_source_id, func.count().label("cnt"))
            .where(Source.parent_source_id.in_(source_ids))
            .group_by(Source.parent_source_id)
        )
        count_result = await db.execute(count_stmt)
        children_counts = {row.parent_source_id: row.cnt for row in count_result.fetchall()}
    
    # Build response
    response_sources = []
    for source in sources:
        children_count = children_counts.get(source.id, 0)
        
        source_dict = {
            "id": source.id,
            "name": source.name,
            "type": source.type,
            "category": source.category,
            "connection_config": source.connection_config,
            "ingestion_rules": source.ingestion_rules,
            "subscription_config": source.subscription_config,
            "status": source.status,
            "last_synced_at": source.last_synced_at,
            "next_sync_at": source.next_sync_at,
            "parent_source_id": source.parent_source_id,
            "children_count": children_count,
            "source_materials": source.source_materials,
            "created_at": source.created_at,
        }
        response_sources.append(source_dict)
    
    return response_sources

@router.post("/detect", response_model=DetectResponse)
async def detect_source_type(
    detect_in: DetectRequest,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Analyze a URL or text to detect source type and metadata.
    """
    return source_detector.detect(detect_in.input, check_connectivity=detect_in.check_connectivity)

@router.post("", response_model=SourceResponse)
async def create_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_in: SourceCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Create new source.
    Automatically determines category based on type and triggers appropriate processing.
    """
    import logging
    import asyncio
    from datetime import datetime, timedelta
    from sqlalchemy.orm import selectinload
    from app.background.paper_tasks import process_paper_background
    from app.schemas.source_schemas import get_category_for_type, SourceCategory
    
    logger = logging.getLogger(__name__)
    
    # Determine category from type
    category = get_category_for_type(source_in.type)
    
    # Set initial status based on category
    if category == SourceCategory.SNAPSHOT:
        initial_status = "PENDING"
        next_sync = None
    else:
        initial_status = "ACTIVE"
        # Calculate next sync time based on subscription config
        sync_freq = (source_in.subscription_config or {}).get("sync_frequency", "DAILY")
        freq_hours = {"HOURLY": 1, "DAILY": 24, "WEEKLY": 168}
        next_sync = datetime.utcnow() + timedelta(hours=freq_hours.get(sync_freq, 24))
    
    source = Source(
        id=uuid.uuid4(),
        user_id=current_user.id,
        name=source_in.name,
        type=source_in.type.value,
        category=category.value,
        connection_config=source_in.connection_config,
        ingestion_rules=source_in.ingestion_rules,
        subscription_config=source_in.subscription_config,
        status=initial_status,
        next_sync_at=next_sync,
    )
    db.add(source)
    await db.commit()
    
    # Re-fetch with eager loading
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source.id)
    result = await db.execute(stmt)
    source = result.scalar_one()
    
    # Trigger processing for snapshot sources
    if category == SourceCategory.SNAPSHOT:
        # For papers and other snapshot types, trigger background processing
        if source.type in [SourceType.ARXIV_PAPER.value, "ARXIV_PAPER"]:
            logger.info(f"[API] Starting background processing for paper source {source.id}")
            asyncio.create_task(process_paper_background(source.id))
        # TODO: Add handlers for other snapshot types (WEB_ARTICLE, GITHUB_REPO, etc.)

    return source

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get source by ID.
    """
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@router.get("/{source_id}/children", response_model=List[SourceResponse])
async def get_child_sources(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get child sources for a subscription source.
    """
    # Verify parent source exists and belongs to user
    parent_stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        parent_stmt = parent_stmt.where(Source.user_id == current_user.id)
    parent_result = await db.execute(parent_stmt)
    parent = parent_result.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Get child sources
    stmt = (
        select(Source)
        .options(selectinload(Source.source_materials))
        .where(Source.parent_source_id == source_id)
        .order_by(Source.created_at.desc())
    )
    result = await db.execute(stmt)
    children = result.scalars().all()
    return children

@router.post("/{source_id}/retry", response_model=SourceResponse)
async def retry_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Retry a failed source.
    Resets status to PENDING and triggers background processing.
    """
    import asyncio
    from app.background.paper_tasks import process_paper_background
    import logging
    
    logger = logging.getLogger(__name__)

    # Get source
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    # Only allow retrying failed or stuck items
    # (Allowing PENDING re-trigger might be useful too if it's really stuck)
    
    # Reset status
    source.status = "PENDING"
    source.error_log = None # Clear error
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    # Trigger processing
    if source.type in ["ARXIV_PAPER", "arxiv_paper"]:
         logger.info(f"[API] Retrying processing for paper source {source.id}")
         asyncio.create_task(process_paper_background(source.id))
         
    return source

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    source_in: SourceUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update source.
    """
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Only update fields that were provided
    if source_in.name is not None:
        source.name = source_in.name
    if source_in.ingestion_rules is not None:
        source.ingestion_rules = source_in.ingestion_rules
    if source_in.subscription_config is not None:
        source.subscription_config = source_in.subscription_config
    if source_in.status is not None:
        source.status = source_in.status
    
    db.add(source)
    await db.commit()
    await db.refresh(source)
    
    # Re-fetch with relationships
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id)
    result = await db.execute(stmt)
    source = result.scalar_one()

    return source

@router.delete("/{source_id}")
async def delete_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    _admin: User = Depends(deps.require_admin),
) -> Any:
    """
    Delete source.
    """
    stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    await db.delete(source)
    await db.commit()
    
    # Clean up associated images
    import shutil
    from pathlib import Path
    from app.core.config import get_settings
    images_dir = Path(get_settings().storage_dir) / "images" / str(source_id)
    if images_dir.exists():
        shutil.rmtree(images_dir, ignore_errors=True)
    
    return {"ok": True}

@router.post("/{source_id}/sync")
async def sync_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Trigger source sync manually for subscription sources.
    Fetches new items and creates source materials.
    """
    # Get source
    stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    if source.category == "SNAPSHOT":
        # For snapshots (papers), manual sync means re-triggering processing
        from app.background.paper_tasks import process_paper_background
        import asyncio
        asyncio.create_task(process_paper_background(source.id))
        return {"status": "processing_triggered", "message": f"Processing triggered for source {source.id}"}

    return await sync_source_internal(db, source)


async def sync_source_internal(db: AsyncSession, source: Source) -> dict:
    """
    Internal sync function - can be called by API or scheduler.
    """
    from app.subscriptions.registry import subscription_registry
    from app.models.models import SourceMaterial
    from datetime import datetime
    import asyncio
    import logging
    from app.background.paper_tasks import process_paper_background
    
    logger = logging.getLogger(__name__)
    
    # Check if it's a subscription type
    if not subscription_registry.is_subscription_type(source.type):
        return {"status": "error", "error": "Source is not a subscription type"}
    
    try:
        # Get fetcher and config
        fetcher = subscription_registry.create_fetcher(source.type)
        config = subscription_registry.parse_config(
            source.type, 
            source.subscription_config or {}
        )
        
        # Fetch new items
        items, new_cursor = await fetcher.fetch_new_items(
            config=config,
            connection_config=source.connection_config or {},
            since_cursor=None  # Fetch latest items
        )
        
        created_count = 0
        papers_to_process = []  # Track paper sources to process after commit
        for item in items:
            # Check if already exists (unique constraint is on user_id + external_id)
            existing_stmt = select(SourceMaterial).where(
                SourceMaterial.user_id == source.user_id,
                SourceMaterial.external_id == item.external_id
            )
            existing_result = await db.execute(existing_stmt)
            if existing_result.scalar_one_or_none():
                logger.info(f"Skipping existing material creation: {item.external_id}")
                # Do NOT continue here - we still need to check if the child source (paper) exists
            else:
                # Create source material
                material = SourceMaterial(
                    user_id=source.user_id,
                    source_id=source.id,
                    external_id=item.external_id,
                    external_url=item.url,
                    title=item.title,
                    rich_data=item.metadata or {},
                )
                db.add(material)
                created_count += 1
            
            # For HF papers, create an individual ARXIV_PAPER source and trigger processing
            if source.type == "HF_DAILY_PAPERS" and item.metadata and item.metadata.get("arxiv_id"):
                arxiv_id = item.metadata["arxiv_id"]
                arxiv_url = f"https://arxiv.org/abs/{arxiv_id}"
                
                # Check if paper source already exists
                existing_paper_stmt = select(Source).where(
                    Source.user_id == source.user_id,
                    Source.type == "ARXIV_PAPER",
                    Source.connection_config["url"].astext == arxiv_url
                )
                existing_paper_result = await db.execute(existing_paper_stmt)
                existing_paper = existing_paper_result.scalar_one_or_none()
                
                if not existing_paper:
                    # Create new paper source with parent reference
                    paper_source = Source(
                        id=uuid.uuid4(),
                        user_id=source.user_id,
                        parent_source_id=source.id,  # Link to subscription source
                        name=item.title,
                        type="ARXIV_PAPER",
                        category="SNAPSHOT",
                        connection_config={"url": arxiv_url},
                        ingestion_rules={},
                        status="PENDING",
                    )
                    db.add(paper_source)
                    await db.flush()  # Get the ID without committing
                    
                    # Queue for processing after commit
                    papers_to_process.append(paper_source.id)
                    logger.info(f"Created paper source {paper_source.id} for {arxiv_url} (parent: {source.id})")
        
        # Update source sync time
        source.last_synced_at = datetime.utcnow()
        await db.commit()
        
        # Trigger paper processing for each new paper source
        for paper_id in papers_to_process:
            logger.info(f"Triggering lens processing for paper {paper_id}")
            asyncio.create_task(process_paper_background(paper_id))
        
        return {
            "status": "sync_completed", 
            "items_fetched": len(items),
            "items_created": created_count,
            "papers_queued": len(papers_to_process)
        }
        
    except Exception as e:
        import traceback
        logger.error(f"Sync failed: {e}\n{traceback.format_exc()}")
        return {"status": "sync_failed", "error": str(e)}


from fastapi import UploadFile, File
from app.services.document_parser import document_parser
from app.models.models import Card, CardStatus, SourceMaterial


@router.post("/{source_id}/upload")
async def upload_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload a document (CSV, MD, TXT) to parse into cards.
    Cards are created with PENDING status for user review.
    """
    # Verify source exists and belongs to user
    stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        stmt = stmt.where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Read file content
    content = await file.read()
    filename = file.filename or "upload.txt"
    
    # Parse document into cards
    try:
        parsed_cards = document_parser.parse(filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not parsed_cards:
        raise HTTPException(status_code=400, detail="No cards could be parsed from the document")
    
    # Create SourceMaterial for tracking
    source_material = SourceMaterial(
        id=uuid.uuid4(),
        user_id=current_user.id,
        source_id=source_id,
        external_id=f"upload_{uuid.uuid4().hex[:8]}",
        title=filename,
        rich_data={"upload_filename": filename, "parsed_count": len(parsed_cards)},
    )
    db.add(source_material)
    
    # Create Card objects
    created_cards = []
    for pc in parsed_cards:
        card = Card(
            id=uuid.uuid4(),
            owner_id=current_user.id,
            source_material_id=source_material.id,
            type=pc.type,
            content={
                "question": pc.question,
                "answer": pc.answer,
                "options": pc.options,
                "explanation": pc.explanation,
            },
            status=CardStatus.PENDING,
            tags=pc.tags,
        )
        db.add(card)
        created_cards.append({
            "id": str(card.id),
            "type": card.type,
            "question": pc.question,
        })
    
    await db.commit()
    
    return {
        "status": "success",
        "source_material_id": str(source_material.id),
        "cards_created": len(created_cards),
        "cards": created_cards,
    }


from pydantic import BaseModel
from datetime import datetime
from app.models.models import SourceLog

class SourceLogResponse(BaseModel):
    id: UUID
    source_id: UUID
    event_type: str
    lens_key: Optional[str]
    status: str
    message: Optional[str]
    duration_ms: Optional[int]
    extra_data: dict
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/{source_id}/logs", response_model=List[SourceLogResponse])
async def get_source_logs(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    limit: int = 50,
) -> Any:
    """
    Get processing logs for a source.
    """
    # Verify source exists and belongs to user
    source_stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        source_stmt = source_stmt.where(Source.user_id == current_user.id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    # Fetch logs
    logs_stmt = (
        select(SourceLog)
        .where(SourceLog.source_id == source_id)
        .order_by(SourceLog.created_at.desc())
        .limit(limit)
    )
    logs_result = await db.execute(logs_stmt)
    logs = logs_result.scalars().all()

    return logs


@router.get("/{source_id}/llm-calls", response_model=List[SourceLogResponse])
async def get_source_llm_calls(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
    limit: int = 50,
) -> Any:
    """
    Get LLM call logs for a source (filtered by event_type='llm_call').
    Includes token usage, duration, and error information.
    """
    # Verify source exists and belongs to user
    source_stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        source_stmt = source_stmt.where(Source.user_id == current_user.id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Fetch LLM call logs only
    logs_stmt = (
        select(SourceLog)
        .where(SourceLog.source_id == source_id)
        .where(SourceLog.event_type == "llm_call")
        .order_by(SourceLog.created_at.desc())
        .limit(limit)
    )
    logs_result = await db.execute(logs_stmt)
    logs = logs_result.scalars().all()

    return logs


@router.get("/{source_id}/llm-stats")
async def get_source_llm_stats(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get aggregated LLM call statistics for a source.
    Returns total tokens, call count, average duration, and error rate.
    """
    # Verify source exists and belongs to user
    source_stmt = select(Source).where(Source.id == source_id)
    if not is_shared_mode():
        source_stmt = source_stmt.where(Source.user_id == current_user.id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Fetch all LLM call logs
    logs_stmt = (
        select(SourceLog)
        .where(SourceLog.source_id == source_id)
        .where(SourceLog.event_type == "llm_call")
    )
    logs_result = await db.execute(logs_stmt)
    logs = logs_result.scalars().all()

    if not logs:
        return {
            "total_calls": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "average_duration_ms": 0,
            "error_count": 0,
            "error_rate": 0.0,
            "by_lens": {},
        }

    # Aggregate stats
    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_duration = 0
    error_count = 0
    by_lens = {}

    for log in logs:
        extra = log.extra_data or {}
        total_tokens += extra.get("total_tokens", 0)
        prompt_tokens += extra.get("prompt_tokens", 0)
        completion_tokens += extra.get("completion_tokens", 0)
        total_duration += extra.get("duration_ms", 0)

        if log.status == "failed":
            error_count += 1

        # Group by lens
        lens = log.lens_key or "unknown"
        if lens not in by_lens:
            by_lens[lens] = {
                "count": 0,
                "tokens": 0,
                "errors": 0,
            }
        by_lens[lens]["count"] += 1
        by_lens[lens]["tokens"] += extra.get("total_tokens", 0)
        if log.status == "failed":
            by_lens[lens]["errors"] += 1

    return {
        "total_calls": len(logs),
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "average_duration_ms": int(total_duration / len(logs)) if logs else 0,
        "error_count": error_count,
        "error_rate": error_count / len(logs) if logs else 0.0,
        "by_lens": by_lens,
    }
    
    return logs
