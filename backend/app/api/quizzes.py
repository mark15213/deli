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


@router.get("/today", response_model=TodayQueue)
async def get_today_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's review queue."""
    # TODO: Implement FSRS queue retrieval
    return TodayQueue(total=0, cards=[])


@router.get("/{quiz_id}", response_model=QuizCard)
async def get_quiz(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific quiz card."""
    # TODO: Implement quiz retrieval
    raise HTTPException(status_code=404, detail="Quiz not found")


@router.get("/{quiz_id}/answer", response_model=QuizCardBack)
async def get_quiz_answer(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the answer and explanation for a quiz."""
    # TODO: Implement answer retrieval
    raise HTTPException(status_code=404, detail="Quiz not found")


@router.post("/{quiz_id}/review", response_model=ReviewResponse)
async def submit_review(
    quiz_id: UUID,
    review: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review for a quiz (triggers FSRS update)."""
    # TODO: Implement FSRS review submission
    from datetime import datetime, timedelta
    return ReviewResponse(
        next_review_at=datetime.utcnow() + timedelta(days=1),
        interval_days=1.0
    )
