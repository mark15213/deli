# Study API routes - Queue management and FSRS review
from uuid import UUID
from typing import List, Optional
from datetime import datetime, timezone

import logging
from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import (
    User, Deck, Card, CardStatus, DeckSubscription, 
    StudyProgress, FSRSState, ReviewLog, card_decks, SourceMaterial
)

from pydantic import BaseModel, Field
from enum import Enum


# --- Schemas ---

class Rating(int, Enum):
    AGAIN = 1  # Forgot
    HARD = 2
    GOOD = 3
    EASY = 4


class StudyCard(BaseModel):
    id: UUID
    type: str
    question: str
    answer: Optional[str] = None
    options: Optional[List[str]] = None
    explanation: Optional[str] = None
    explanation: Optional[str] = None
    images: Optional[List[str]] = None  # For reading notes
    tags: List[str] = []
    source_title: Optional[str] = None
    deck_ids: List[UUID] = []
    deck_titles: List[str] = []
    # Batch info for series notes (paper reading notes)
    batch_id: Optional[UUID] = None
    batch_index: Optional[int] = None
    batch_total: Optional[int] = None

    class Config:
        from_attributes = True


class PaperStudyGroup(BaseModel):
    """A group of study cards from the same paper/source."""
    source_id: UUID
    source_title: str
    source_url: Optional[str] = None
    source_type: Optional[str] = None
    summary: Optional[str] = None  # TL;DR from rich_data
    card_count: int
    cards: List[StudyCard] = []


class ReviewSubmit(BaseModel):
    rating: Rating


class ReviewResponse(BaseModel):
    card_id: UUID
    next_review_at: datetime
    interval_days: float
    new_state: str


class StudyStats(BaseModel):
    today_reviewed: int
    today_remaining: int
    streak_days: int
    total_mastered: int
    total_cards: int


# --- FSRS Parameters (simplified) ---
# ... (FSRS logic unchanged) ...

def calculate_next_review(rating: Rating, progress: StudyProgress) -> tuple[float, float, float, FSRSState, datetime]:
    """
    Simplified FSRS calculation.
    Returns: (new_stability, new_difficulty, scheduled_days, new_state, due_date)
    """
    now = datetime.now(timezone.utc)
    
    # Default parameters
    stability = progress.stability if progress.stability > 0 else 1.0
    difficulty = progress.difficulty if progress.difficulty > 0 else 5.0
    
    # Adjust based on rating
    if rating == Rating.AGAIN:
        # Failed - reset to learning
        new_stability = max(0.1, stability * 0.5)
        new_difficulty = min(10, difficulty + 1)
        scheduled_days = 0.0  # Review again soon (minutes)
        new_state = FSRSState.RELEARNING
    elif rating == Rating.HARD:
        new_stability = stability * 1.2
        new_difficulty = min(10, difficulty + 0.5)
        scheduled_days = max(1, stability * 1.2)
        new_state = FSRSState.REVIEW
    elif rating == Rating.GOOD:
        new_stability = stability * 2.5
        new_difficulty = difficulty
        scheduled_days = stability * 2.5
        new_state = FSRSState.REVIEW
    else:  # EASY
        new_stability = stability * 4.0
        new_difficulty = max(1, difficulty - 0.5)
        scheduled_days = stability * 4.0
        new_state = FSRSState.REVIEW
    
    from datetime import timedelta
    due_date = now + timedelta(days=scheduled_days)
    
    return new_stability, new_difficulty, scheduled_days, new_state, due_date


# --- Router ---

router = APIRouter(prefix="/study", tags=["study"])


@router.get("/queue", response_model=List[StudyCard])
async def get_study_queue(
    limit: int = Query(20, ge=1, le=100),
    deck_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's study queue based on subscribed decks and FSRS due dates."""
    now = datetime.now(timezone.utc)
    
    # Get subscribed deck IDs
    sub_stmt = select(DeckSubscription.deck_id).where(
        DeckSubscription.user_id == current_user.id
    )
    sub_result = await db.execute(sub_stmt)
    subscribed_deck_ids = [row[0] for row in sub_result.fetchall()]
    
    target_deck_ids = []
    
    if deck_id:
        # Check if user is subscribed to the requested deck
        if deck_id not in subscribed_deck_ids:
             # Or maybe they are the owner? Owner automatically subscribed? 
             # For now, require subscription for study
             # Actually, let's allow if they are owner too even if not subscribed explicitly (though owner is usually subscribed)
             # But strictly, subscription drives study queue.
             pass
        
        # We will filter by this deck_id, but we should make sure it's a valid ID for this user (subscribed)
        if deck_id in subscribed_deck_ids:
            target_deck_ids = [deck_id]
        else:
            # If not subscribed, return empty or error? 
            # Let's return empty to be safe, or check if they are owner. 
            pass
            
        # Simplified: Just trust the filter. If not subscribed, logic below might return nothing if we restrict to subscribed.
        # But wait, original logic was: Deck.id.in_(subscribed_deck_ids). 
        # So we just need to intersect.
        if deck_id in subscribed_deck_ids:
            target_deck_ids = [deck_id]
        else:
             return []
    else:
        target_deck_ids = subscribed_deck_ids

    if not target_deck_ids:
        return []
    
    # Get cards that are due for review
    # Include: cards with no progress (new), or cards where due_date <= now
    
    # First, get cards from decks that are ACTIVE
    # Using distinct ensures we don't get duplicates if card is in multiple subscribed decks
    # Prioritize reading_note type in the DB fetch to ensure they aren't cut off by the limit
    cards_stmt = (
        select(Card)
        .join(Card.decks)
        .where(
            Deck.id.in_(target_deck_ids),
            Card.status.in_([CardStatus.ACTIVE, CardStatus.PENDING]),
        )
        .options(
            selectinload(Card.decks),
            selectinload(Card.source_material).selectinload(SourceMaterial.source)
        )
        .order_by(
            case((Card.type == "reading_note", 0), else_=1),
            Card.created_at.desc()
        )
        .limit(limit * 5)  # Get more to filter and sort
    )
    cards_result = await db.execute(cards_stmt)
    raw_cards = cards_result.scalars().all()
    
    # Deduplicate in Python (needed because we removed .distinct() to allow complex sorting)
    all_cards = list({c.id: c for c in raw_cards}.values())
    
    # Sort cards to ensure reading notes (batches) appear in order and first
    # Also group cards by source_material_id to keep cards from the same paper together
    # 1. Primary sort: Reading notes first (0 vs 1)
    # 2. Secondary sort: Source material ID (group same source together)
    # 3. Tertiary sort: Batch ID for reading notes
    # 4. Quaternary sort: Batch Index
    all_cards = sorted(
        all_cards, 
        key=lambda c: (
            0 if c.type == "reading_note" else 1,
            str(c.source_material_id) if c.source_material_id else '',
            str(c.batch_id) if c.batch_id else '', 
            c.batch_index if c.batch_index is not None else 0
        )
    )

    logger.info(f"Study Queue Debug: Found {len(all_cards)} raw cards in decks {target_deck_ids}")

    # Get existing study progress for these cards
    card_ids = [c.id for c in all_cards]
    progress_map = {}
    
    if card_ids:
        progress_stmt = select(StudyProgress).where(
            StudyProgress.user_id == current_user.id,
            StudyProgress.card_id.in_(card_ids),
        )
        progress_result = await db.execute(progress_stmt)
        progress_map = {p.card_id: p for p in progress_result.scalars().all()}
    
    # Filter to cards that are due
    due_cards = []
    for card in all_cards:
        progress = progress_map.get(card.id)
        if progress is None:
            # New card - add to queue
            due_cards.append(card)
        elif progress.due_date <= now:
            # Due for review
            due_cards.append(card)
        
        if len(due_cards) >= limit:
            break
    # Calculate batch_total for cards with batch_id
    batch_totals = {}
    batch_ids_to_query = set(c.batch_id for c in due_cards if c.batch_id)
    if batch_ids_to_query:
        batch_count_stmt = (
            select(Card.batch_id, func.count(Card.id))
            .where(Card.batch_id.in_(batch_ids_to_query))
            .group_by(Card.batch_id)
        )
        batch_result = await db.execute(batch_count_stmt)
        batch_totals = {row[0]: row[1] for row in batch_result.fetchall()}
    
    # Build response
    return [
        StudyCard(
            id=card.id,
            type=card.type,
            question=card.content.get("question", "") if card.content else "",
            answer=card.content.get("answer") if card.content else None,
            options=card.content.get("options") if card.content else None,
            explanation=card.content.get("explanation") if card.content else None,
            images=card.content.get("images") if card.content else None,
            tags=card.tags or [],
            source_title=card.source_material.source.name if card.source_material and card.source_material.source else None,
            deck_ids=[d.id for d in card.decks],
            deck_titles=[d.title for d in card.decks],
            batch_id=card.batch_id,
            batch_index=card.batch_index,
            batch_total=batch_totals.get(card.batch_id) if card.batch_id else None,
        )
        for card in due_cards
    ]


@router.get("/papers", response_model=List[PaperStudyGroup])
async def get_study_papers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get study queue grouped by paper/source, each with TL;DR summary."""
    now = datetime.now(timezone.utc)
    
    # Get subscribed deck IDs
    sub_stmt = select(DeckSubscription.deck_id).where(
        DeckSubscription.user_id == current_user.id
    )
    sub_result = await db.execute(sub_stmt)
    subscribed_deck_ids = [row[0] for row in sub_result.fetchall()]
    
    if not subscribed_deck_ids:
        return []
    
    # Get all active/pending cards from subscribed decks with source info
    cards_stmt = (
        select(Card)
        .join(Card.decks)
        .where(
            Deck.id.in_(subscribed_deck_ids),
            Card.status.in_([CardStatus.ACTIVE, CardStatus.PENDING]),
            Card.source_material_id.isnot(None),  # Must have a source
        )
        .options(
            selectinload(Card.decks),
            selectinload(Card.source_material).selectinload(SourceMaterial.source)
        )
        .order_by(Card.created_at.desc())
        .limit(200)
    )
    cards_result = await db.execute(cards_stmt)
    raw_cards = list({c.id: c for c in cards_result.scalars().all()}.values())
    
    # Get study progress to filter to due cards
    card_ids = [c.id for c in raw_cards]
    progress_map = {}
    if card_ids:
        progress_stmt = select(StudyProgress).where(
            StudyProgress.user_id == current_user.id,
            StudyProgress.card_id.in_(card_ids),
        )
        progress_result = await db.execute(progress_stmt)
        progress_map = {p.card_id: p for p in progress_result.scalars().all()}
    
    # Filter to due cards
    due_cards = []
    for card in raw_cards:
        progress = progress_map.get(card.id)
        if progress is None or progress.due_date <= now:
            due_cards.append(card)
    
    # Calculate batch totals
    batch_totals = {}
    batch_ids_to_query = set(c.batch_id for c in due_cards if c.batch_id)
    if batch_ids_to_query:
        batch_count_stmt = (
            select(Card.batch_id, func.count(Card.id))
            .where(Card.batch_id.in_(batch_ids_to_query))
            .group_by(Card.batch_id)
        )
        batch_result = await db.execute(batch_count_stmt)
        batch_totals = {row[0]: row[1] for row in batch_result.fetchall()}
    
    # Group by source
    from collections import defaultdict
    source_groups: dict[str, dict] = {}
    
    for card in due_cards:
        sm = card.source_material
        if not sm or not sm.source:
            continue
        
        source_id = str(sm.source.id)
        if source_id not in source_groups:
            # Extract summary from rich_data
            summary = None
            if sm.rich_data and isinstance(sm.rich_data, dict):
                summary = sm.rich_data.get("summary")
            
            source_groups[source_id] = {
                "source_id": sm.source.id,
                "source_title": sm.source.name,
                "source_url": (sm.source.connection_config or {}).get("url"),
                "source_type": sm.source.type,
                "summary": summary,
                "cards": [],
            }
        
        source_groups[source_id]["cards"].append(
            StudyCard(
                id=card.id,
                type=card.type,
                question=card.content.get("question", "") if card.content else "",
                answer=card.content.get("answer") if card.content else None,
                options=card.content.get("options") if card.content else None,
                explanation=card.content.get("explanation") if card.content else None,
                images=card.content.get("images") if card.content else None,
                tags=card.tags or [],
                source_title=sm.source.name,
                deck_ids=[d.id for d in card.decks],
                deck_titles=[d.title for d in card.decks],
                batch_id=card.batch_id,
                batch_index=card.batch_index,
                batch_total=batch_totals.get(card.batch_id) if card.batch_id else None,
            )
        )
    
    # Sort cards within each group: reading notes first, then by batch_index
    result = []
    for group_data in source_groups.values():
        cards = group_data["cards"]
        cards.sort(key=lambda c: (
            0 if c.type == "reading_note" else 1,
            str(c.batch_id) if c.batch_id else '',
            c.batch_index if c.batch_index is not None else 0,
        ))
        result.append(PaperStudyGroup(
            source_id=group_data["source_id"],
            source_title=group_data["source_title"],
            source_url=group_data["source_url"],
            source_type=group_data["source_type"],
            summary=group_data["summary"],
            card_count=len(cards),
            cards=cards,
        ))
    
    # Sort groups: most cards first
    result.sort(key=lambda g: g.card_count, reverse=True)
    
    return result


@router.post("/{card_id}/review", response_model=ReviewResponse)
async def submit_review(
    card_id: UUID,
    review: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review rating for a card and update FSRS state."""
    
    # Verify card exists and user has access (via subscription to at least one deck)
    card_stmt = (
        select(Card)
        .join(Card.decks)
        .join(DeckSubscription, and_(
            DeckSubscription.deck_id == Deck.id,
            DeckSubscription.user_id == current_user.id,
        ), isouter=True)
        .where(Card.id == card_id)
        .options(selectinload(Card.decks))
    )
    # The query implies: find card by ID. 
    # But ideally we should ensure at least one deck is subscribed.
    # Logic: Fetch card, check decks.
    
    # Simpler retrieval first
    stmt = (
        select(Card)
        .where(Card.id == card_id)
        .options(selectinload(Card.decks))
    )
    card_result = await db.execute(stmt)
    card = card_result.scalar_one_or_none()
    
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    # Check subscription access
    # Get user subscriptions
    sub_stmt = select(DeckSubscription.deck_id).where(DeckSubscription.user_id == current_user.id)
    sub_result = await db.execute(sub_stmt)
    subscribed_ids = set(row[0] for row in sub_result.fetchall())
    
    # Check if any of card's decks are in subscribed_ids
    has_access = any(d.id in subscribed_ids for d in card.decks)
    # Also owner can review? Maybe.
    if not has_access and card.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get or create study progress
    progress_stmt = select(StudyProgress).where(
        StudyProgress.user_id == current_user.id,
        StudyProgress.card_id == card_id,
    )
    progress_result = await db.execute(progress_stmt)
    progress = progress_result.scalar_one_or_none()
    
    if not progress:
        # Create new progress entry
        progress = StudyProgress(
            user_id=current_user.id,
            card_id=card_id,
            stability=0.0,
            difficulty=5.0,
            state=FSRSState.NEW,
        )
        db.add(progress)
    
    # Store before state for log
    state_before = progress.state
    stability_before = progress.stability
    difficulty_before = progress.difficulty
    
    # Calculate next review
    new_stability, new_difficulty, scheduled_days, new_state, due_date = calculate_next_review(
        review.rating, progress
    )
    
    # Update progress
    progress.stability = new_stability
    progress.difficulty = new_difficulty
    progress.scheduled_days = scheduled_days
    progress.state = new_state
    progress.due_date = due_date
    progress.last_review_at = datetime.now(timezone.utc)
    
    # Create review log
    review_log = ReviewLog(
        user_id=current_user.id,
        card_id=card_id,
        grade=review.rating.value,
        state_before=state_before,
        stability_before=stability_before,
        difficulty_before=difficulty_before,
    )
    db.add(review_log)
    
    await db.commit()
    
    return ReviewResponse(
        card_id=card_id,
        next_review_at=due_date,
        interval_days=scheduled_days,
        new_state=new_state.value,
    )


@router.get("/stats", response_model=StudyStats)
async def get_study_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get study statistics for the current user."""
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Today reviewed count
    reviewed_stmt = select(func.count(ReviewLog.id)).where(
        ReviewLog.user_id == current_user.id,
        ReviewLog.reviewed_at >= today_start,
    )
    reviewed_result = await db.execute(reviewed_stmt)
    today_reviewed = reviewed_result.scalar() or 0
    
    # Today remaining (due cards)
    sub_stmt = select(DeckSubscription.deck_id).where(
        DeckSubscription.user_id == current_user.id
    )
    sub_result = await db.execute(sub_stmt)
    subscribed_deck_ids = [row[0] for row in sub_result.fetchall()]
    
    if subscribed_deck_ids:
        remaining_stmt = (
            select(func.count(Card.id))
            .join(Card.decks)
            .outerjoin(StudyProgress, and_(
                StudyProgress.card_id == Card.id,
                StudyProgress.user_id == current_user.id,
            ))
            .where(
                Deck.id.in_(subscribed_deck_ids),
                Card.status == CardStatus.ACTIVE,
                # Either no progress or due
                (StudyProgress.id == None) | (StudyProgress.due_date <= now),
            )
            .distinct()
        )
        # Note: count behavior with distinct join might need count distinct id
        # Correct way for count distinct:
        remaining_stmt = (
            select(func.count(Card.id.distinct()))
            .join(Card.decks)
            .outerjoin(StudyProgress, and_(
                StudyProgress.card_id == Card.id,
                StudyProgress.user_id == current_user.id,
            ))
            .where(
                Deck.id.in_(subscribed_deck_ids),
                Card.status.in_([CardStatus.ACTIVE, CardStatus.PENDING]),
                (StudyProgress.id == None) | (StudyProgress.due_date <= now),
            )
        )
        
        remaining_result = await db.execute(remaining_stmt)
        today_remaining = remaining_result.scalar() or 0
    else:
        today_remaining = 0
    
    # Total mastered (state = REVIEW with high stability)
    mastered_stmt = select(func.count(StudyProgress.id)).where(
        StudyProgress.user_id == current_user.id,
        StudyProgress.state == FSRSState.REVIEW,
        StudyProgress.stability >= 21,  # 3 weeks stability = mastered
    )
    mastered_result = await db.execute(mastered_stmt)
    total_mastered = mastered_result.scalar() or 0
    
    # Total cards
    total_stmt = select(func.count(StudyProgress.id)).where(
        StudyProgress.user_id == current_user.id,
    )
    total_result = await db.execute(total_stmt)
    total_cards = total_result.scalar() or 0
    
    # Streak - simplified (count consecutive days with reviews)
    # TODO: implement proper streak calculation
    streak_days = 0
    
    return StudyStats(
        today_reviewed=today_reviewed,
        today_remaining=today_remaining,
        streak_days=streak_days,
        total_mastered=total_mastered,
        total_cards=total_cards,
    )


class SkipBatchResponse(BaseModel):
    status: str
    batch_id: UUID
    cards_skipped: int


@router.post("/skip-batch/{batch_id}", response_model=SkipBatchResponse)
async def skip_batch(
    batch_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Skip all cards in a batch (mark as permanently skipped).
    Used for skipping entire paper reading note series.
    """
    # Get all cards in this batch owned by the user
    stmt = (
        select(Card)
        .where(
            Card.batch_id == batch_id,
            Card.owner_id == current_user.id,
        )
    )
    result = await db.execute(stmt)
    cards = result.scalars().all()
    
    if not cards:
        raise HTTPException(status_code=404, detail="Batch not found or no access")
    
    skipped_count = 0
    for card in cards:
        # Get or create study progress
        progress_stmt = select(StudyProgress).where(
            StudyProgress.user_id == current_user.id,
            StudyProgress.card_id == card.id,
        )
        progress_result = await db.execute(progress_stmt)
        progress = progress_result.scalar_one_or_none()
        
        if not progress:
            # Create new progress entry
            progress = StudyProgress(
                user_id=current_user.id,
                card_id=card.id,
                stability=0.0,
                difficulty=0.0,
                state=FSRSState.REVIEW,
            )
            db.add(progress)
        
        # Mark as permanently skipped by setting very far future due date
        progress.state = FSRSState.REVIEW
        progress.due_date = datetime(9999, 12, 31, tzinfo=timezone.utc)  # Far future = never show
        progress.last_review_at = datetime.now(timezone.utc)
        skipped_count += 1
    
    await db.commit()
    
    return SkipBatchResponse(
        status="skipped",
        batch_id=batch_id,
        cards_skipped=skipped_count,
    )
