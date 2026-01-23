# FSRS Scheduler Service
from datetime import datetime, timezone
from typing import Optional, Tuple
import uuid
from uuid import UUID

from fsrs import FSRS, Card, Rating, State
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models import ReviewRecord, Quiz, QuizStatus

class SchedulerService:
    """Service for managing FSRS scheduling logic."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fsrs = FSRS()

    async def get_due_quizzes(self, user_id: UUID, limit: int = 50) -> list[Quiz]:
        """Get quizzes due for review (or new ones)."""
        now = datetime.now(timezone.utc)
        
        # 1. Fetch quizzes where next_review_at <= now, OR no review record (new)
        # Note: This query logic needs careful join since we store reviews separately.
        # Efficient approach: Join Quiz and latest ReviewRecord
        
        # For MVP, simpler logic:
        # Check all quizzes belonging to user with status APPROVED
        # Filter where related latest review record is due OR none exists
        
        # Actually simplest query:
        # Select * from Quizzes left join ReviewRecords
        # Where user_id = :uid AND status = APPROVED
        # AND (next_review_at <= :now OR next_review_at IS NULL)
        
        stmt = (
            select(Quiz)
            .outerjoin(ReviewRecord)
            .where(
                Quiz.user_id == user_id,
                Quiz.status == QuizStatus.APPROVED,
            )
            .group_by(Quiz.id)
            .having(
                # Check if most recent review is due
                # Since ReviewRecords are historical, we need a way to track current state
                # Option A: Store current state in Quiz model (denormalization) -> Best for performant queries
                # Option B: Store current state in a "CardState" model 1:1 with Quiz
                # Option C: Complex subquery.
                
                # Looking at models.py, ReviewRecord seems to be historical log (1:N).
                # But wait, looking at ReviewRecord implementation in models.py:
                #    next_review_at is stored in ReviewRecord.
                # This suggests we need to find the LATEST record.
                
                # To simplify MVP queries, we should probably add `next_review_at` to the Quiz model itself
                # or create a persistent `Card` state table.
                # WITHOUT SCHEMEMA ACHANGE: We assume we query recently reviewed or never reviewed.
                
                # Let's adjust query to reliable find due items without schema change:
                # 1. Fetch quizzes with NO review records (New)
                # 2. Fetch quizzes with review records where max(next_review_at) <= now
                
                # Actually, models.py ReviewRecord has `quiz_id`.
                # Let's try to query quizzes that do not have a review record with next_review_at > now.
                # This is "due" if no future review exists.
                True 
            )
        )
        
        # Wait, the current schema on `ReviewRecord` is a log. 
        # Querying "Latest status" from a log table is expensive.
        # But `latest_review_at` isn't on Quiz.
        
        # FOR MVP: We will fetch all APPROVED quizzes and filter in Python (bad for scale, fine for MVP demo).
        # OR: We only check `ReviewRecord` table for scheduling? 
        # But `ReviewRecord` is historical.
        
        # Let's stick to Python filtering for safety and simplicity right now.
        q_stmt = select(Quiz).where(
            Quiz.user_id == user_id, 
            Quiz.status == QuizStatus.APPROVED
        )
        result = await self.db.execute(q_stmt)
        all_quizzes = result.scalars().all()
        
        due_quizzes = []
        for quiz in all_quizzes:
            # Get latest review for this quiz
            r_stmt = (
                select(ReviewRecord)
                .where(ReviewRecord.quiz_id == quiz.id)
                .order_by(desc(ReviewRecord.reviewed_at))
                .limit(1)
            )
            r_res = await self.db.execute(r_stmt)
            latest_review = r_res.scalar_one_or_none()
            
            if not latest_review:
                # New card, it is due
                due_quizzes.append(quiz)
            elif latest_review.next_review_at.replace(tzinfo=timezone.utc) <= now:
                # Due card
                due_quizzes.append(quiz)
                
            if len(due_quizzes) >= limit:
                break
                
        return due_quizzes

    async def calculate_review(self, user_id: UUID, quiz_id: UUID, rating: int) -> ReviewRecord:
        """
        Process a review, calculate next schedule using FSRS, and save record.
        Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
        """
        # 1. Get latest review state
        stmt = (
            select(ReviewRecord)
            .where(ReviewRecord.quiz_id == quiz_id)
            .order_by(desc(ReviewRecord.reviewed_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        last_record = result.scalar_one_or_none()
        
        # Use naive UTC to match model definition
        now = datetime.utcnow()
        
        # 2. Reconstruct Card object for FSRS
        card = Card()
        if last_record and last_record.fsrs_state:
            state_dict = last_record.fsrs_state
            # Map dict back to Card object props if needed, or pass to scheduler
            # fsrs-python usually takes a Card object.
            # We need to manually hydrate it if library doesn't support dict init.
            # Assuming fsrs library usage:
            card.stability = state_dict.get("stability", card.stability)
            card.difficulty = state_dict.get("difficulty", card.difficulty)
            card.elapsed_days = state_dict.get("elapsed_days", 0)
            card.scheduled_days = state_dict.get("scheduled_days", 0)
            card.reps = state_dict.get("reps", 0)
            card.lapses = state_dict.get("lapses", 0)
            card.state = State(state_dict.get("state", State.New.value))
            # Ensure last_review is aware for FSRS calculation if required, then convert back
            if last_record.reviewed_at:
                 card.last_review = last_record.reviewed_at.replace(tzinfo=timezone.utc)
        
        # 3. Calculate new state
        # Map integer rating 1-4 to FSRS Rating Enum
        fsrs_rating = Rating(rating)
        
        # FSRS expects aware datetime usually
        scheduling_cards = self.fsrs.repeat(card, now.replace(tzinfo=timezone.utc))
        new_card = scheduling_cards[fsrs_rating].card
        
        # Convert due date back to naive UTC for DB
        next_review_naive = new_card.due.replace(tzinfo=None)
        
        # 4. Save new ReviewRecord
        new_record = ReviewRecord(
            id=uuid.uuid4(),
            user_id=user_id,
            quiz_id=quiz_id,
            rating=rating,
            reviewed_at=now,
            next_review_at=next_review_naive,
            fsrs_state={
                "stability": new_card.stability,
                "difficulty": new_card.difficulty,
                "elapsed_days": new_card.elapsed_days,
                "scheduled_days": new_card.scheduled_days,
                "reps": new_card.reps,
                "lapses": new_card.lapses,
                "state": new_card.state.value
            }
        )
        
        self.db.add(new_record)
        await self.db.commit()
        return new_record
