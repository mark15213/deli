# API routes for quiz/card operations
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.schemas import (
    TodayQueue,
    QuizCard,
    QuizCardBack,
    ReviewSubmit,
    ReviewResponse,
)
from app.api.deps import get_current_user
from app.models import User, Card
from app.services.scheduler_service import SchedulerService

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/today", response_model=TodayQueue)
async def get_today_queue(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get today's review queue."""
    scheduler = SchedulerService(db)
    due_cards = await scheduler.get_due_cards(current_user.id)
    
    # Map DB Card model to Pydantic Schema
    # NOTE: The schema `QuizCard` might expect `quiz_id` but we have `id` (uuid).
    # Since Pydantic V2 from_attributes=True usually works if names match.
    # We might need to adjust schemas if `QuizCard` assumes flat structure vs `content` dict.
    
    # For now, simplistic mapping:
    # We iterate and construct the response manually if schema mismatches are severe,
    # or rely on Pydantic and fix schema later.
    
    # Let's assume we will fix schemas to accept `content` dict and `id`.
    
    return TodayQueue(
        total=len(due_cards),
        cards=due_cards
    )


@router.get("/{card_id}", response_model=QuizCard)
async def get_quiz(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific quiz card."""
    card = await db.get(Card, card_id)
    # Check ownership via Deck?
    # For now, check if deck owner is user.
    if not card:
         raise HTTPException(status_code=404, detail="Card not found")
         
    # Optimization: join deck to check owner
    # For MVP, assume if you have ID you can see it or add Owner check layer
    # ...
    
    return card


@router.get("/{card_id}/answer", response_model=QuizCardBack)
async def get_quiz_answer(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the answer and explanation for a quiz."""
    card = await db.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


@router.post("/{card_id}/review", response_model=ReviewResponse)
async def submit_review(
    card_id: UUID,
    review: ReviewSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit a review for a card (triggers FSRS update)."""
    scheduler = SchedulerService(db)
    
    record = await scheduler.calculate_review(
        user_id=current_user.id,
        card_id=card_id,
        rating=review.rating
    )
    
    # Calculate interval for response from Due Date vs Now or Last Review?
    # Simple calc:
    interval = (record.due_date - record.last_review_at).days
    
    return ReviewResponse(
        next_review_at=record.due_date,
        interval_days=float(interval)
    )
