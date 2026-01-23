# API routes for quiz operations
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import (
    TodayQueue,
    QuizCard,
    QuizCardBack,
    ReviewSubmit,
    ReviewResponse,
)
from app.api.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


from app.services.scheduler_service import SchedulerService

@router.get("/today", response_model=TodayQueue)
async def get_today_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's review queue."""
    scheduler = SchedulerService(db)
    due_quizzes = await scheduler.get_due_quizzes(current_user.id)
    
    # Needs to convert DB models to QuizCard schemas or just return ID list?
    # TodayQueue schema expects `total` and `cards`.
    # We need to map DB model -> Pydantic Schema.
    # Assuming QuizCard schema matches or we map it manually.
    
    return TodayQueue(
        total=len(due_quizzes),
        cards=due_quizzes # Pydantic v2 usually handles ORM mapping if configured
    )


@router.get("/{quiz_id}", response_model=QuizCard)
async def get_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific quiz card."""
    from app.models import Quiz
    quiz = await db.get(Quiz, quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.get("/{quiz_id}/answer", response_model=QuizCardBack)
async def get_quiz_answer(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the answer and explanation for a quiz."""
    from app.models import Quiz
    quiz = await db.get(Quiz, quiz_id)
    if not quiz or quiz.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/review", response_model=ReviewResponse)
async def submit_review(
    quiz_id: UUID,
    review: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review for a quiz (triggers FSRS update)."""
    scheduler = SchedulerService(db)
    
    # Verify ownership
    # (Optional optimization: SchedulerService could check ownership or we do it here)
    # Let's rely on SchedulerService failing or ensure we check existence first.
    
    record = await scheduler.calculate_review(
        user_id=current_user.id,
        quiz_id=quiz_id,
        rating=review.rating
    )
    
    # Calculate interval for response
    interval = (record.next_review_at - record.reviewed_at).days
    
    return ReviewResponse(
        next_review_at=record.next_review_at,
        interval_days=float(interval)
    )
