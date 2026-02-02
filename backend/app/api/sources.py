import uuid
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api import deps
from app.models.models import User, Source
from app.schemas.source_schemas import SourceCreate, SourceResponse
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
    """
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.user_id == current_user.id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    return sources

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
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id, Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    source_in: SourceCreate, # Can be Partial update schema in future
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update source.
    """
    stmt = select(Source).options(selectinload(Source.source_materials)).where(Source.id == source_id, Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    source.name = source_in.name
    # source.type = source_in.type # Type usually doesn't change?
    source.connection_config = source_in.connection_config
    source.ingestion_rules = source_in.ingestion_rules
    
    db.add(source)
    await db.commit()
    # Re-fetch or refresh, but since we already have it loaded with options, a refresh might be needed if triggers changed things. 
    # But usually just returning the object is fine if we updated fields. 
    # However, to be safe against lazy loading triggers:
    await db.refresh(source) 
    # Note: simple refresh might clear relationships? 
    # Better to re-fetch if we want to be safe or rely on the previous load being sufficient if we didn't touch relationships.
    # Actually, let's re-fetch to be consistent.
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
) -> Any:
    """
    Delete source.
    """
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    await db.delete(source)
    await db.commit()
    return {"ok": True}

@router.post("/{source_id}/sync")
async def sync_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Trigger source sync manually.
    """
    # This would trigger a Celery task or background job
    # For now just return mock
    return {"status": "sync_started", "job_id": "mock-job-id"}


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
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
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
    source_stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
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
