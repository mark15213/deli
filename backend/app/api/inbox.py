# API routes for inbox management
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.schemas import InboxItem
from app.api.deps import get_current_user
from app.models import User, Card, CardStatus, Deck, SourceMaterial

from pydantic import BaseModel


# --- Schemas ---

class InboxCardPreview(BaseModel):
    id: UUID
    deck_ids: List[UUID] = []
    type: str
    question: str
    status: str
    
    class Config:
        from_attributes = True


class InboxSourceGroup(BaseModel):
    """Cards grouped by source material."""
    source_id: Optional[UUID]
    source_title: str
    source_url: Optional[str]
    source_type: Optional[str]
    notes_count: int = 0
    flashcards_count: int = 0
    quizzes_count: int = 0
    total_count: int = 0
    cards: List[InboxCardPreview] = []
    created_at: datetime


class BulkActionRequest(BaseModel):
    card_ids: List[UUID]


# --- Router ---

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/pending", response_model=List[InboxItem])
async def get_pending_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending items in inbox."""
    stmt = (
        select(Card)
        .where(
            Card.owner_id == current_user.id,
            Card.status == CardStatus.PENDING
        )
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    return cards


@router.get("/sources", response_model=List[InboxSourceGroup])
async def get_pending_by_source(
    status: Optional[str] = None,  # "pending", "active", "rejected", or None for all
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get items grouped by source material. Optionally filter by status."""
    
    stmt = (
        select(Card)
        .outerjoin(Card.source_material)
        .where(Card.owner_id == current_user.id)
        .options(
            selectinload(Card.source_material),
            selectinload(Card.decks)
        )
        .order_by(Card.created_at.desc())
    )
    
    # Apply status filter if provided
    if status:
        status_map = {
            "pending": CardStatus.PENDING,
            "active": CardStatus.ACTIVE,
            "rejected": CardStatus.REJECTED,
            "archived": CardStatus.ARCHIVED,
        }
        if status.lower() in status_map:
            stmt = stmt.where(Card.status == status_map[status.lower()])
    
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    # Group by source_material_id
    groups = {}
    for card in cards:
        source_id = card.source_material_id
        
        if source_id not in groups:
            source = card.source_material
            groups[source_id] = {
                "source_id": source_id,
                "source_title": source.title if source else "Unknown Source",
                "source_url": source.external_url if source else None,
                "source_type": None,  # Could derive from source.type
                "notes_count": 0,
                "flashcards_count": 0,
                "quizzes_count": 0,
                "total_count": 0,
                "cards": [],
                "created_at": card.created_at,  # Use newest card
            }
        
        # Update counts
        group = groups[source_id]
        group["total_count"] += 1
        
        if card.type == "note":
            group["notes_count"] += 1
        elif card.type == "flashcard":
            group["flashcards_count"] += 1
        elif card.type == "quiz":
            group["quizzes_count"] += 1
            
        # Add card preview (exclude rejected/archived if needed, but query handles it)
        group["cards"].append(InboxCardPreview(
            id=card.id,
            deck_ids=[d.id for d in card.decks],
            type=card.type,
            question=card.content.get("question", "") if card.content else "",
            status=card.status.value,
        ))
    
    return list(groups.values())


# --- Bulk actions ---

@router.post("/bulk/approve")
async def bulk_approve(
    request: BulkActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve multiple cards at once."""
    stmt = (
        select(Card)
        .where(
            Card.id.in_(request.card_ids),
            Card.owner_id == current_user.id,
            Card.status == CardStatus.PENDING
        )
    )
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    approved_ids = []
    for card in cards:
        card.status = CardStatus.ACTIVE
        approved_ids.append(str(card.id))
    
    await db.commit()
    
    return {
        "status": "approved",
        "count": len(approved_ids),
        "card_ids": approved_ids,
    }


@router.post("/bulk/reject")
async def bulk_reject(
    request: BulkActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject multiple cards at once."""
    stmt = (
        select(Card)
        .where(
            Card.id.in_(request.card_ids),
            Card.owner_id == current_user.id,
            Card.status == CardStatus.PENDING
        )
    )
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    rejected_ids = []
    for card in cards:
        card.status = CardStatus.REJECTED
        rejected_ids.append(str(card.id))
    
    await db.commit()
    
    return {
        "status": "rejected",
        "count": len(rejected_ids),
        "card_ids": rejected_ids,
    }


# --- Single card actions ---

@router.post("/{card_id}/approve")
async def approve_item(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve an inbox item."""
    stmt = select(Card).where(Card.id == card_id, Card.owner_id == current_user.id)
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    card.status = CardStatus.ACTIVE
    await db.commit()
    
    return {"status": "approved", "card_id": str(card_id)}


@router.post("/{card_id}/reject")
async def reject_item(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject an inbox item."""
    stmt = select(Card).where(Card.id == card_id, Card.owner_id == current_user.id)
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    card.status = CardStatus.REJECTED
    await db.commit()
    
    return {"status": "rejected", "card_id": str(card_id)}


@router.post("/{card_id}/decks/{deck_id}")
async def add_card_to_deck(
    card_id: UUID,
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a card to a deck (M2M). Sets status to ACTIVE."""
    # Verify card
    card_stmt = (
        select(Card)
        .where(Card.id == card_id, Card.owner_id == current_user.id)
        .options(selectinload(Card.decks))
    )
    card = (await db.execute(card_stmt)).scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Verify deck
    deck_stmt = select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    target_deck = (await db.execute(deck_stmt)).scalar_one_or_none()
    
    if not target_deck:
        raise HTTPException(status_code=404, detail="Target deck not found")
    
    # Add if not present
    if target_deck not in card.decks:
        card.decks.append(target_deck)
    
    # Implicit approval
    if card.status == CardStatus.PENDING:
        card.status = CardStatus.ACTIVE
        
    await db.commit()
    
    return {
        "status": "added",
        "card_id": str(card_id),
        "deck_id": str(deck_id),
    }


@router.delete("/{card_id}/decks/{deck_id}")
async def remove_card_from_deck(
    card_id: UUID,
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a card from a deck."""
    # Verify card
    card_stmt = (
        select(Card)
        .where(Card.id == card_id, Card.owner_id == current_user.id)
        .options(selectinload(Card.decks))
    )
    card = (await db.execute(card_stmt)).scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Remove if present
    deck_to_remove = next((d for d in card.decks if d.id == deck_id), None)
    if deck_to_remove:
        card.decks.remove(deck_to_remove)
        await db.commit()
        return {"status": "removed", "deck_id": str(deck_id)}
    
    raise HTTPException(status_code=404, detail="Deck not associated with card")

