# API routes for card bookmarks (Clip/Gulp feature)
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Card, CardBookmark, SourceMaterial


# --- Schemas ---

class BookmarkResponse(BaseModel):
    id: UUID
    card_id: UUID
    card_type: str
    card_question: str
    card_answer: Optional[str] = None
    source_title: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    note: Optional[str] = None


# --- Router ---

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.post("/{card_id}", response_model=BookmarkResponse, status_code=201)
async def bookmark_card(
    card_id: UUID,
    body: BookmarkCreate = BookmarkCreate(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bookmark (clip) a card for Gulp mode."""
    # Verify card exists
    card = await db.get(Card, card_id, options=[
        selectinload(Card.source_material).selectinload(SourceMaterial.source)
    ])
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Check if already bookmarked
    existing_stmt = select(CardBookmark).where(
        CardBookmark.user_id == current_user.id,
        CardBookmark.card_id == card_id,
    )
    existing = (await db.execute(existing_stmt)).scalar_one_or_none()
    if existing:
        # Update note if provided, otherwise return existing
        if body.note is not None:
            existing.note = body.note
            await db.commit()
        return _bookmark_to_response(existing, card)

    # Create bookmark
    bookmark = CardBookmark(
        user_id=current_user.id,
        card_id=card_id,
        note=body.note,
    )
    db.add(bookmark)
    await db.commit()
    await db.refresh(bookmark)

    return _bookmark_to_response(bookmark, card)


@router.delete("/{card_id}", status_code=204)
async def unbookmark_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove bookmark from a card."""
    stmt = delete(CardBookmark).where(
        CardBookmark.user_id == current_user.id,
        CardBookmark.card_id == card_id,
    )
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")


@router.get("", response_model=List[BookmarkResponse])
async def get_bookmarks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all bookmarked cards for the current user."""
    stmt = (
        select(CardBookmark)
        .where(CardBookmark.user_id == current_user.id)
        .options(
            selectinload(CardBookmark.card)
            .selectinload(Card.source_material)
            .selectinload(SourceMaterial.source)
        )
        .order_by(CardBookmark.created_at.desc())
    )
    result = await db.execute(stmt)
    bookmarks = result.scalars().all()

    return [
        _bookmark_to_response(b, b.card)
        for b in bookmarks
    ]


@router.get("/check/{card_id}")
async def check_bookmark(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if a card is bookmarked."""
    stmt = select(CardBookmark.id).where(
        CardBookmark.user_id == current_user.id,
        CardBookmark.card_id == card_id,
    )
    result = (await db.execute(stmt)).scalar_one_or_none()
    return {"bookmarked": result is not None}


def _bookmark_to_response(bookmark: CardBookmark, card: Card) -> BookmarkResponse:
    """Helper to build BookmarkResponse from model instances."""
    source_title = None
    if card.source_material and card.source_material.source:
        source_title = card.source_material.source.name

    return BookmarkResponse(
        id=bookmark.id,
        card_id=card.id,
        card_type=card.type,
        card_question=card.content.get("question", "") if card.content else "",
        card_answer=card.content.get("answer") if card.content else None,
        source_title=source_title,
        note=bookmark.note,
        created_at=bookmark.created_at,
    )
