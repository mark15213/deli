# API routes for inbox management
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.schemas import InboxItem
from app.api.deps import get_current_user
from app.models import User, Card, CardStatus, Deck

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/pending", response_model=List[InboxItem])
async def get_pending_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending items in inbox."""
    # Logic: Find cards with Status=PENDING owned by user (via Deck)
    stmt = (
        select(Card)
        .join(Card.deck)
        .where(
            Deck.owner_id == current_user.id,
            Card.status == CardStatus.PENDING
        )
        .offset(skip)
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    # Need to map Card to InboxItem schema
    return cards


@router.post("/{card_id}/approve")
async def approve_item(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve an inbox item."""
    stmt = (
        select(Card)
        .join(Card.deck)
        .where(
            Card.id == card_id,
            Deck.owner_id == current_user.id
        )
    )
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
    stmt = (
        select(Card)
        .join(Card.deck)
        .where(
            Card.id == card_id,
            Deck.owner_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
        
    card.status = CardStatus.REJECTED
    await db.commit()
    
    return {"status": "rejected", "card_id": str(card_id)}


@router.put("/{card_id}")
async def update_item(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edit an inbox item."""
    # TODO: Implement edit logic
    raise HTTPException(status_code=501, detail="Not implemented")
