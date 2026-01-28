# Deck API routes
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Deck, Card, CardStatus, DeckSubscription, StudyProgress, FSRSState, card_decks

from pydantic import BaseModel, Field


# --- Schemas ---

class DeckCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: bool = False
    cover_image_url: Optional[str] = None


class DeckUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    cover_image_url: Optional[str] = None


class DeckResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    is_public: bool
    cover_image_url: Optional[str]
    card_count: int = 0
    mastery_percent: float = 0.0
    is_subscribed: bool = False
    last_review_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CardInDeck(BaseModel):
    id: UUID
    type: str
    question: str
    status: str
    tags: List[str] = []
    created_at: datetime

    class Config:
        from_attributes = True


class DeckDetail(DeckResponse):
    cards: List[CardInDeck] = []


# --- Router ---

router = APIRouter(prefix="/decks", tags=["decks"])

@router.get("", response_model=List[DeckResponse])
async def list_decks(
    subscribed_only: bool = Query(False, description="Only return subscribed decks"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all decks owned by or subscribed to by current user."""
    
    # Subquery for card count using M2M table
    card_count_subq = (
        select(
            card_decks.c.deck_id, 
            func.count(card_decks.c.card_id).label("card_count")
        )
        .join(Card, card_decks.c.card_id == Card.id)
        .where(Card.status == CardStatus.ACTIVE)
        .group_by(card_decks.c.deck_id)
        .subquery()
    )
    
    # Mastery subquery complex with M2M - simplified/disabled for now
    # ...
    
    # Main query
    stmt = (
        select(Deck)
        .where(Deck.owner_id == current_user.id)
        .options(selectinload(Deck.subscribers))
    )
    
    result = await db.execute(stmt)
    decks = result.scalars().all()
    
    # ... (subscriptions logic same) ...
    # Get subscribed deck IDs
    sub_stmt = select(DeckSubscription.deck_id).where(
        DeckSubscription.user_id == current_user.id
    )
    sub_result = await db.execute(sub_stmt)
    subscribed_ids = set(row[0] for row in sub_result.fetchall())
    
    # Get card counts
    count_stmt = select(card_count_subq)
    count_result = await db.execute(count_stmt)
    card_counts = {row.deck_id: row.card_count for row in count_result.fetchall()}
    
    # Build response
    response = []
    for deck in decks:
        is_subscribed = deck.id in subscribed_ids
        
        if subscribed_only and not is_subscribed:
            continue
            
        response.append(DeckResponse(
            id=deck.id,
            title=deck.title,
            description=deck.description,
            is_public=deck.is_public,
            cover_image_url=deck.cover_image_url,
            card_count=card_counts.get(deck.id, 0),
            mastery_percent=0.0,
            is_subscribed=is_subscribed,
            last_review_at=None,
            created_at=deck.created_at,
        ))
    
    return response


@router.post("", response_model=DeckResponse)
async def create_deck(
    deck_in: DeckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new deck."""
    deck = Deck(
        owner_id=current_user.id,
        title=deck_in.title,
        description=deck_in.description,
        is_public=deck_in.is_public,
        cover_image_url=deck_in.cover_image_url,
    )
    db.add(deck)
    await db.commit()
    await db.refresh(deck)
    
    return DeckResponse(
        id=deck.id,
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        cover_image_url=deck.cover_image_url,
        card_count=0,
        mastery_percent=0.0,
        is_subscribed=False,
        last_review_at=None,
        created_at=deck.created_at,
    )


@router.get("/{deck_id}", response_model=DeckDetail)
async def get_deck(
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get deck details with cards."""
    stmt = (
        select(Deck)
        .where(Deck.id == deck_id)
        .options(selectinload(Deck.cards))
    )
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Check access
    if deck.owner_id != current_user.id and not deck.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check subscription
    sub_stmt = select(DeckSubscription).where(
        DeckSubscription.user_id == current_user.id,
        DeckSubscription.deck_id == deck_id,
    )
    sub_result = await db.execute(sub_stmt)
    is_subscribed = sub_result.scalar_one_or_none() is not None
    
    # Build cards list
    cards = [
        CardInDeck(
            id=card.id,
            type=card.type,
            question=card.content.get("question", "") if card.content else "",
            status=card.status.value,
            tags=card.tags or [],
            created_at=card.created_at,
        )
        for card in deck.cards
    ]
    
    return DeckDetail(
        id=deck.id,
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        cover_image_url=deck.cover_image_url,
        card_count=len([c for c in deck.cards if c.status == CardStatus.ACTIVE]),
        mastery_percent=0.0,
        is_subscribed=is_subscribed,
        last_review_at=None,
        created_at=deck.created_at,
        cards=cards,
    )


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: UUID,
    deck_in: DeckUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a deck."""
    stmt = select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    update_data = deck_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deck, field, value)
    
    await db.commit()
    await db.refresh(deck)
    
    return DeckResponse(
        id=deck.id,
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        cover_image_url=deck.cover_image_url,
        card_count=0,
        mastery_percent=0.0,
        is_subscribed=False,
        last_review_at=None,
        created_at=deck.created_at,
    )


@router.delete("/{deck_id}")
async def delete_deck(
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a deck."""
    stmt = select(Deck).where(Deck.id == deck_id, Deck.owner_id == current_user.id)
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    await db.delete(deck)
    await db.commit()
    
    return {"status": "deleted", "deck_id": str(deck_id)}


@router.post("/{deck_id}/subscribe")
async def subscribe_to_deck(
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Subscribe to a deck for daily study."""
    # Check deck exists
    stmt = select(Deck).where(Deck.id == deck_id)
    result = await db.execute(stmt)
    deck = result.scalar_one_or_none()
    
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    
    # Check access
    if deck.owner_id != current_user.id and not deck.is_public:
        raise HTTPException(status_code=403, detail="Cannot subscribe to private deck")
    
    # Check if already subscribed
    sub_stmt = select(DeckSubscription).where(
        DeckSubscription.user_id == current_user.id,
        DeckSubscription.deck_id == deck_id,
    )
    sub_result = await db.execute(sub_stmt)
    existing = sub_result.scalar_one_or_none()
    
    if existing:
        return {"status": "already_subscribed", "deck_id": str(deck_id)}
    
    # Create subscription
    subscription = DeckSubscription(
        user_id=current_user.id,
        deck_id=deck_id,
    )
    db.add(subscription)
    await db.commit()
    
    return {"status": "subscribed", "deck_id": str(deck_id)}


@router.delete("/{deck_id}/subscribe")
async def unsubscribe_from_deck(
    deck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Unsubscribe from a deck."""
    stmt = select(DeckSubscription).where(
        DeckSubscription.user_id == current_user.id,
        DeckSubscription.deck_id == deck_id,
    )
    result = await db.execute(stmt)
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    await db.delete(subscription)
    await db.commit()
    
    return {"status": "unsubscribed", "deck_id": str(deck_id)}
