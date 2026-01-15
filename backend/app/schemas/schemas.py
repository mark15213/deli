# Pydantic schemas for API validation
from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr


# --- Enums ---
class QuizType(str, Enum):
    MCQ = "mcq"
    TRUE_FALSE = "true_false"
    CLOZE = "cloze"
    CODE_OUTPUT = "code_output"
    SPOT_BUG = "spot_bug"
    REORDER = "reorder"
    FLASHCARD = "flashcard"


class Rating(int, Enum):
    AGAIN = 1  # Forgot
    HARD = 2
    GOOD = 3
    EASY = 4


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# --- Quiz Schemas ---
class QuizSource(BaseModel):
    page_id: str | None = None
    block_id: str | None = None
    page_title: str | None = None
    deep_link: str | None = None


class QuizBase(BaseModel):
    type: QuizType
    question: str
    options: list[str] | None = None
    answer: str
    explanation: str | None = None
    tags: list[str] = Field(default_factory=list)
    difficulty: str | None = None


class QuizCreate(QuizBase):
    source: QuizSource | None = None


class QuizResponse(QuizBase):
    id: UUID
    source: QuizSource | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class QuizCard(BaseModel):
    """Quiz card for review UI."""
    id: UUID
    type: QuizType
    question: str
    options: list[str] | None = None
    tags: list[str] = []
    source_title: str | None = None


class QuizCardBack(BaseModel):
    """Back of quiz card with answer and explanation."""
    answer: str
    explanation: str | None = None
    deep_link: str | None = None


# --- Review Schemas ---
class ReviewSubmit(BaseModel):
    quiz_id: UUID
    rating: Rating


class ReviewResponse(BaseModel):
    next_review_at: datetime
    interval_days: float


# --- Today's Queue ---
class TodayQueue(BaseModel):
    total: int
    cards: list[QuizCard]


# --- Stats ---
class DashboardStats(BaseModel):
    today_reviewed: int
    today_remaining: int
    streak_days: int
    total_mastered: int


# --- Inbox ---
class InboxItem(BaseModel):
    id: UUID
    quiz: QuizResponse
    created_at: datetime

    class Config:
        from_attributes = True


class InboxAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
