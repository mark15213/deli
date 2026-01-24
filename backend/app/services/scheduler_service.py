# FSRS Scheduler Service
from datetime import datetime, timezone
from typing import List
from uuid import UUID
import uuid

from fsrs import FSRS, Card as FSRSCard, Rating, State as FSRSStateEnum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models import StudyProgress, ReviewLog, Card, FSRSState, CardStatus

class SchedulerService:
    """Service for managing FSRS scheduling logic."""
    
    # Mapping FSRS ints to our string Enums
    FSRS_INT_TO_STATE = {
         0: FSRSState.NEW,
         1: FSRSState.LEARNING,
         2: FSRSState.REVIEW,
         3: FSRSState.RELEARNING
    }

    FSRS_STATE_TO_INT = {
        FSRSState.NEW: 0,
        FSRSState.LEARNING: 1,
        FSRSState.REVIEW: 2,
        FSRSState.RELEARNING: 3
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fsrs = FSRS()

    async def get_due_cards(self, user_id: UUID, limit: int = 50) -> List[Card]:
        """Get cards due for review."""
        now = datetime.now(timezone.utc)
        
        # 1. Fetch cards with StudyProgress where due_date <= now
        # Also need to fetch New cards (state='new' or no progress) if configured to mix new/review.
        
        # Simple Logic: 
        # Join Card and StudyProgress.
        # Condition: 
        # - User ID matches
        # - Card Status is ACTIVE (if we only want active cards)
        # - (Progress.due_date <= now OR Progress IS NULL)
        
        stmt = (
            select(Card)
            .outerjoin(StudyProgress, and_(
                StudyProgress.card_id == Card.id,
                StudyProgress.user_id == user_id
            ))
            .join(Card.deck) # Ensure deck ownership or subscription if needed? Cards don't store owner, Decks do.
            # Assuming user owns the deck or we check deck subscription (omitted for MVP simplicity)
            .where(
                 # Card.status == CardStatus.ACTIVE,  # Or check deck owner
                 # For now, let's look for StudyProgress explicitly owned by user
                 # This implies we only serve cards that are already "started" or we query generic cards.
                 # Let's query StudyProgress capable cards.
                 True
            )
            # This query is tricky without explicit ownership on Card. 
            # Cards belong to Decks. Decks belong to Users. 
            # But StudyProgress effectively "instantiates" the card for the user.
            # If we want NEW cards, we need to find cards in decks the user subscribes to/owns that have NO progress.
        )
        
        # Improved Approach: Query StudyProgress directly for reviews
        sp_stmt = (
             select(StudyProgress)
             .where(
                 StudyProgress.user_id == user_id,
                 StudyProgress.due_date <= now
             )
             .limit(limit)
        )
        result = await self.db.execute(sp_stmt)
        progress_items = result.scalars().all()
        
        cards = []
        for p in progress_items:
            # Load card
            # This is N+1, but efficiently handled by async driver often or we can eager load
            card_res = await self.db.execute(select(Card).where(Card.id == p.card_id))
            card = card_res.scalar_one()
            cards.append(card)
            
        return cards

    async def calculate_review(self, user_id: UUID, card_id: UUID, rating: int) -> StudyProgress:
        """
        Process a review, calculate next schedule using FSRS, update StudyProgress and log ReviewLog.
        Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        """
        now = datetime.now(timezone.utc)
        
        # 1. Get current progress
        stmt = select(StudyProgress).where(
            StudyProgress.user_id == user_id,
            StudyProgress.card_id == card_id
        )
        result = await self.db.execute(stmt)
        progress = result.scalar_one_or_none()
        
        fsrs_card = FSRSCard()
        
        if progress:
            fsrs_card.stability = progress.stability
            fsrs_card.difficulty = progress.difficulty
            fsrs_card.elapsed_days = progress.elapsed_days
            fsrs_card.scheduled_days = progress.scheduled_days
            # fsrs_card.reps = ... (add to model if needed)
            # fsrs_card.lapses = ...
            fsrs_card.state = FSRSStateEnum(self.FSRS_STATE_TO_INT.get(progress.state, 0))
            # Need last_review for accurate calc?
            if progress.last_review_at:
                fsrs_card.last_review = progress.last_review_at
        else:
             # Initialize new progress container
             progress = StudyProgress(
                 id=uuid.uuid4(),
                 user_id=user_id,
                 card_id=card_id
             )
             self.db.add(progress)

        # 2. Capture state before
        state_before_int = fsrs_card.state.value
        stability_before = fsrs_card.stability
        difficulty_before = fsrs_card.difficulty

        # 3. Calculate new state
        fsrs_rating = Rating(rating)
        scheduling_cards = self.fsrs.repeat(fsrs_card, now)
        new_card = scheduling_cards[fsrs_rating].card
        
        # 4. Update Progress
        progress.stability = new_card.stability
        progress.difficulty = new_card.difficulty
        progress.elapsed_days = new_card.elapsed_days
        progress.scheduled_days = new_card.scheduled_days
        progress.state = self.FSRS_INT_TO_STATE.get(new_card.state.value, FSRSState.NEW)
        progress.due_date = new_card.due
        progress.last_review_at = now
        
        # 5. Log Review
        log = ReviewLog(
            user_id=user_id,
            card_id=card_id,
            grade=rating,
            state_before=self.FSRS_INT_TO_STATE.get(state_before_int, FSRSState.NEW),
            stability_before=stability_before,
            difficulty_before=difficulty_before,
            reviewed_at=now
        )
        self.db.add(log)
        
        await self.db.commit()
        return progress
