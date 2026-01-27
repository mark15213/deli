from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.api import deps
from app.models.models import User, Source
from app.schemas.source_schemas import SourceCreate, SourceResponse
from app.schemas.detect_schemas import DetectRequest, DetectResponse
from app.services.source_detector import source_detector

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("/", response_model=List[SourceResponse])
def get_sources(
    current_user: User = Depends(deps.get_mock_user),
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve current user's sources.
    """
    stmt = select(Source).where(Source.user_id == current_user.id).offset(skip).limit(limit)
    sources = db.scalars(stmt).all()
    return sources

@router.post("/detect", response_model=DetectResponse)
def detect_source_type(
    detect_in: DetectRequest,
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Analyze a URL or text to detect source type and metadata.
    """
    return source_detector.detect(detect_in.input, check_connectivity=detect_in.check_connectivity)

@router.post("/", response_model=SourceResponse)
def create_source(
    *,
    db: Session = Depends(deps.get_db),
    source_in: SourceCreate,
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Create new source.
    """
    source = Source(
        user_id=current_user.id,
        name=source_in.name,
        type=source_in.type.value, # Store as string enum value
        connection_config=source_in.connection_config,
        ingestion_rules=source_in.ingestion_rules,
        status="ACTIVE"
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source

@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    *,
    db: Session = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Get source by ID.
    """
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    source = db.scalars(stmt).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    *,
    db: Session = Depends(deps.get_db),
    source_id: UUID,
    source_in: SourceCreate, # Can be Partial update schema in future
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Update source.
    """
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    source = db.scalars(stmt).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    source.name = source_in.name
    # source.type = source_in.type # Type usually doesn't change?
    source.connection_config = source_in.connection_config
    source.ingestion_rules = source_in.ingestion_rules
    
    db.add(source)
    db.commit()
    db.refresh(source)
    return source

@router.delete("/{source_id}")
def delete_source(
    *,
    db: Session = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Delete source.
    """
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    source = db.scalars(stmt).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    db.delete(source)
    db.commit()
    return {"ok": True}

@router.post("/{source_id}/sync")
def sync_source(
    *,
    db: Session = Depends(deps.get_db),
    source_id: UUID,
    current_user: User = Depends(deps.get_mock_user),
) -> Any:
    """
    Trigger source sync manually.
    """
    # This would trigger a Celery task or background job
    # For now just return mock
    return {"status": "sync_started", "job_id": "mock-job-id"}
