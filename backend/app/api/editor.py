"""
Editor API — CRUD for paper editing, annotations, image uploads, and sharing.
"""
import secrets
import uuid
import os
import logging
from pathlib import Path
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.models import User, Source, SourceEdit, SourceAnnotation, ShareLink

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/editor", tags=["editor"])


# --- Schemas ---

class EditorContentResponse(BaseModel):
    source_id: UUID
    source_title: str
    source_url: Optional[str] = None
    content: dict  # Tiptap JSON
    plain_text: Optional[str] = None
    updated_at: Optional[str] = None


class EditorSaveRequest(BaseModel):
    content: dict  # Tiptap JSON
    plain_text: Optional[str] = None


class AnnotationCreate(BaseModel):
    type: str  # 'highlight' or 'comment'
    color: Optional[str] = None
    anchor: dict  # {from, to}
    body: Optional[str] = None


class AnnotationUpdate(BaseModel):
    type: Optional[str] = None
    color: Optional[str] = None
    anchor: Optional[dict] = None
    body: Optional[str] = None
    resolved: Optional[bool] = None


class AnnotationResponse(BaseModel):
    id: UUID
    type: str
    color: Optional[str] = None
    anchor: dict
    body: Optional[str] = None
    resolved: bool
    created_at: str
    updated_at: str


class ShareLinkResponse(BaseModel):
    token: str
    url: str
    include_annotations: bool
    is_active: bool
    view_count: int


class SharedContentResponse(BaseModel):
    source_title: str
    source_url: Optional[str] = None
    content: dict
    annotations: List[AnnotationResponse] = []
    view_count: int


class ImageUploadResponse(BaseModel):
    url: str
    filename: str


# --- Editor Content Endpoints ---

@router.get("/{source_id}", response_model=EditorContentResponse)
async def get_editor_content(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get editor content for a source.
    On first access, auto-initialize from reading_note cards.
    """
    # Check source exists
    source_stmt = select(Source).where(Source.id == source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Look for existing edit
    edit_stmt = select(SourceEdit).where(
        SourceEdit.source_id == source_id,
        SourceEdit.user_id == current_user.id,
    )
    edit_result = await db.execute(edit_stmt)
    source_edit = edit_result.scalar_one_or_none()

    if not source_edit:
        # First time: initialize from reading_note cards
        from app.services.tiptap_converter import build_tiptap_document
        tiptap_doc = await build_tiptap_document(db, source_id, current_user.id)

        source_edit = SourceEdit(
            source_id=source_id,
            user_id=current_user.id,
            content=tiptap_doc,
        )
        db.add(source_edit)
        await db.flush()

    source_url = (source.connection_config or {}).get("url") if source.connection_config else None

    return EditorContentResponse(
        source_id=source_id,
        source_title=source.name,
        source_url=source_url,
        content=source_edit.content,
        plain_text=source_edit.plain_text,
        updated_at=source_edit.updated_at.isoformat() if source_edit.updated_at else None,
    )


@router.put("/{source_id}", response_model=EditorContentResponse)
async def save_editor_content(
    source_id: UUID,
    body: EditorSaveRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Save edited content."""
    # Check source exists
    source_stmt = select(Source).where(Source.id == source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Get or create edit
    edit_stmt = select(SourceEdit).where(
        SourceEdit.source_id == source_id,
        SourceEdit.user_id == current_user.id,
    )
    edit_result = await db.execute(edit_stmt)
    source_edit = edit_result.scalar_one_or_none()

    if not source_edit:
        source_edit = SourceEdit(
            source_id=source_id,
            user_id=current_user.id,
            content=body.content,
            plain_text=body.plain_text,
        )
        db.add(source_edit)
    else:
        source_edit.content = body.content
        source_edit.plain_text = body.plain_text

    await db.flush()

    # Sync editor content back to reading note cards
    from app.services.tiptap_converter import sync_tiptap_to_cards
    try:
        await sync_tiptap_to_cards(db, source_id, current_user.id, body.content)
        await db.commit() # Commit all changes including editor content and synced cards
    except Exception as e:
        logger.error(f"Failed to sync tiptap to cards for source {source_id}: {e}")
        await db.rollback() # Rollback on error

    source_url = (source.connection_config or {}).get("url") if source.connection_config else None


    return EditorContentResponse(
        source_id=source_id,
        source_title=source.name,
        source_url=source_url,
        content=source_edit.content,
        plain_text=source_edit.plain_text,
        updated_at=source_edit.updated_at.isoformat() if source_edit.updated_at else None,
    )


# --- Image Upload Endpoints ---

@router.post("/{source_id}/images", response_model=ImageUploadResponse)
async def upload_image(
    source_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload an image for the editor."""
    # Validate source exists
    source_stmt = select(Source).where(Source.id == source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Validate file type
    allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not allowed")

    # Create directory
    settings = get_settings()
    img_dir = Path(settings.storage_dir) / "images" / "editor" / str(source_id)
    img_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    ext = Path(file.filename or "image.jpg").suffix or ".jpg"
    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    filepath = img_dir / filename

    # Save file
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # Return URL path
    url = f"/static/images/editor/{source_id}/{filename}"

    return ImageUploadResponse(url=url, filename=filename)


@router.delete("/{source_id}/images/{filename}")
async def delete_image(
    source_id: UUID,
    filename: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an uploaded image."""
    settings = get_settings()
    filepath = Path(settings.storage_dir) / "images" / "editor" / str(source_id) / filename

    if filepath.exists():
        os.remove(filepath)
        return {"status": "deleted", "filename": filename}
    else:
        raise HTTPException(status_code=404, detail="Image not found")


# --- Annotation Endpoints ---

@router.get("/{source_id}/annotations", response_model=List[AnnotationResponse])
async def get_annotations(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all annotations for a source edit."""
    # Get source edit
    edit_stmt = select(SourceEdit).where(
        SourceEdit.source_id == source_id,
        SourceEdit.user_id == current_user.id,
    )
    edit_result = await db.execute(edit_stmt)
    source_edit = edit_result.scalar_one_or_none()

    if not source_edit:
        return []

    # Get annotations
    ann_stmt = select(SourceAnnotation).where(
        SourceAnnotation.source_edit_id == source_edit.id,
    ).order_by(SourceAnnotation.created_at.asc())
    ann_result = await db.execute(ann_stmt)
    annotations = ann_result.scalars().all()

    return [
        AnnotationResponse(
            id=a.id,
            type=a.type,
            color=a.color,
            anchor=a.anchor,
            body=a.body,
            resolved=a.resolved,
            created_at=a.created_at.isoformat(),
            updated_at=a.updated_at.isoformat(),
        )
        for a in annotations
    ]


@router.post("/{source_id}/annotations", response_model=AnnotationResponse)
async def create_annotation(
    source_id: UUID,
    body: AnnotationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new annotation."""
    # Get or create source edit
    edit_stmt = select(SourceEdit).where(
        SourceEdit.source_id == source_id,
        SourceEdit.user_id == current_user.id,
    )
    edit_result = await db.execute(edit_stmt)
    source_edit = edit_result.scalar_one_or_none()

    if not source_edit:
        raise HTTPException(status_code=404, detail="No editor content found. Open the editor first.")

    annotation = SourceAnnotation(
        source_edit_id=source_edit.id,
        user_id=current_user.id,
        type=body.type,
        color=body.color,
        anchor=body.anchor,
        body=body.body,
    )
    db.add(annotation)
    await db.flush()

    return AnnotationResponse(
        id=annotation.id,
        type=annotation.type,
        color=annotation.color,
        anchor=annotation.anchor,
        body=annotation.body,
        resolved=annotation.resolved,
        created_at=annotation.created_at.isoformat(),
        updated_at=annotation.updated_at.isoformat(),
    )


@router.put("/{source_id}/annotations/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    source_id: UUID,
    annotation_id: UUID,
    body: AnnotationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an annotation."""
    ann_stmt = select(SourceAnnotation).where(
        SourceAnnotation.id == annotation_id,
        SourceAnnotation.user_id == current_user.id,
    )
    ann_result = await db.execute(ann_stmt)
    annotation = ann_result.scalar_one_or_none()

    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    if body.type is not None:
        annotation.type = body.type
    if body.color is not None:
        annotation.color = body.color
    if body.anchor is not None:
        annotation.anchor = body.anchor
    if body.body is not None:
        annotation.body = body.body
    if body.resolved is not None:
        annotation.resolved = body.resolved

    await db.flush()

    return AnnotationResponse(
        id=annotation.id,
        type=annotation.type,
        color=annotation.color,
        anchor=annotation.anchor,
        body=annotation.body,
        resolved=annotation.resolved,
        created_at=annotation.created_at.isoformat(),
        updated_at=annotation.updated_at.isoformat(),
    )


@router.delete("/{source_id}/annotations/{annotation_id}")
async def delete_annotation(
    source_id: UUID,
    annotation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an annotation."""
    ann_stmt = select(SourceAnnotation).where(
        SourceAnnotation.id == annotation_id,
        SourceAnnotation.user_id == current_user.id,
    )
    ann_result = await db.execute(ann_stmt)
    annotation = ann_result.scalar_one_or_none()

    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    await db.delete(annotation)
    return {"status": "deleted"}


# --- Share Link Endpoints ---

@router.post("/{source_id}/share", response_model=ShareLinkResponse)
async def create_share_link(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a public share link for the edited paper."""
    # Check source exists
    source_stmt = select(Source).where(Source.id == source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Check if active share link already exists
    existing_stmt = select(ShareLink).where(
        ShareLink.source_id == source_id,
        ShareLink.user_id == current_user.id,
        ShareLink.is_active == True,
    )
    existing_result = await db.execute(existing_stmt)
    existing = existing_result.scalar_one_or_none()

    if existing:
        # Return existing link
        settings = get_settings()
        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
        return ShareLinkResponse(
            token=existing.token,
            url=f"{frontend_url}/shared/{existing.token}",
            include_annotations=existing.include_annotations,
            is_active=existing.is_active,
            view_count=existing.view_count,
        )

    # Generate new token
    token = secrets.token_urlsafe(16)[:22]  # URL-safe, ~22 chars

    share_link = ShareLink(
        source_id=source_id,
        user_id=current_user.id,
        token=token,
    )
    db.add(share_link)
    await db.flush()

    frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:3000")
    return ShareLinkResponse(
        token=token,
        url=f"{frontend_url}/shared/{token}",
        include_annotations=share_link.include_annotations,
        is_active=share_link.is_active,
        view_count=share_link.view_count,
    )


@router.delete("/{source_id}/share")
async def revoke_share_link(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Revoke (deactivate) share link."""
    stmt = select(ShareLink).where(
        ShareLink.source_id == source_id,
        ShareLink.user_id == current_user.id,
        ShareLink.is_active == True,
    )
    result = await db.execute(stmt)
    share_link = result.scalar_one_or_none()

    if not share_link:
        raise HTTPException(status_code=404, detail="No active share link found")

    share_link.is_active = False
    return {"status": "revoked"}


# --- Public Shared Content (No Auth) ---

shared_router = APIRouter(prefix="/shared", tags=["shared"])


@shared_router.get("/{token}", response_model=SharedContentResponse)
async def get_shared_content(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Public endpoint — get shared paper content by token.
    No authentication required.
    """
    # Find share link
    link_stmt = select(ShareLink).where(
        ShareLink.token == token,
        ShareLink.is_active == True,
    )
    link_result = await db.execute(link_stmt)
    share_link = link_result.scalar_one_or_none()

    if not share_link:
        raise HTTPException(status_code=404, detail="Share link not found or expired")

    # Increment view count
    share_link.view_count += 1

    # Get source
    source_stmt = select(Source).where(Source.id == share_link.source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # Get editor content
    edit_stmt = select(SourceEdit).where(
        SourceEdit.source_id == share_link.source_id,
        SourceEdit.user_id == share_link.user_id,
    )
    edit_result = await db.execute(edit_stmt)
    source_edit = edit_result.scalar_one_or_none()

    if not source_edit:
        raise HTTPException(status_code=404, detail="No editor content found")

    # Get annotations if included
    annotations = []
    if share_link.include_annotations:
        ann_stmt = select(SourceAnnotation).where(
            SourceAnnotation.source_edit_id == source_edit.id,
        ).order_by(SourceAnnotation.created_at.asc())
        ann_result = await db.execute(ann_stmt)
        db_annotations = ann_result.scalars().all()

        annotations = [
            AnnotationResponse(
                id=a.id,
                type=a.type,
                color=a.color,
                anchor=a.anchor,
                body=a.body,
                resolved=a.resolved,
                created_at=a.created_at.isoformat(),
                updated_at=a.updated_at.isoformat(),
            )
            for a in db_annotations
        ]

    source_url = (source.connection_config or {}).get("url") if source.connection_config else None

    return SharedContentResponse(
        source_title=source.name,
        source_url=source_url,
        content=source_edit.content,
        annotations=annotations,
        view_count=share_link.view_count,
    )
