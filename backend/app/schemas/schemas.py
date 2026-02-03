# Pydantic schemas for API validation
from datetime import datetime
from uuid import UUID
from enum import Enum
from typing import Any, List, Optional, Dict

from pydantic import BaseModel, Field, EmailStr, model_validator


# --- Enums ---
class CardType(str, Enum):
    MCQ = "mcq"
    CLOZE = "cloze"
    CODE = "code"


class Rating(int, Enum):
    AGAIN = 1  # Forgot
    HARD = 2
    GOOD = 3
    EASY = 4


class CardStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    ARCHIVED = "archived"


# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    username: str | None = None
    avatar_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None
    user_id: str | None = None
    email: str | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# --- Card/Quiz Schemas ---

class QuizCard(BaseModel):
    """Card definition for Review UI."""
    id: UUID
    type: str # 'mcq', etc.
    question: str
    options: list[str] | None = None
    tags: list[str] = []
    
    # We might map source_title if we want, but let's keep it simple
    # content is JSONB in DB. We flatten it here.

    @model_validator(mode='before')
    @classmethod
    def flatten_card(cls, data: Any) -> Any:
        # Check if data is an ORM object (has 'content' attribute)
        if hasattr(data, "content") and isinstance(data.content, dict):
            content = data.content
            # Create a dict from the object to modify it
            return {
                "id": data.id,
                "type": data.type,
                "question": content.get("question"),
                "options": content.get("options"),
                "tags": data.tags or [],
            }
        return data

    class Config:
        from_attributes = True


class QuizCardBack(BaseModel):
    """Back of card."""
    answer: str
    explanation: str | None = None
    deep_link: str | None = None
    
    @model_validator(mode='before')
    @classmethod
    def flatten_back(cls, data: Any) -> Any:
        if hasattr(data, "content") and isinstance(data.content, dict):
            content = data.content
            # Try to get deep link from source_material if not on card?
            # data.source_material.external_url ?
            # For now just content
            return {
                "answer": content.get("answer"),
                "explanation": content.get("explanation"),
                # "deep_link": ...
            }
        return data

    class Config:
        from_attributes = True


# --- Review Schemas ---
class ReviewSubmit(BaseModel):
    # quiz_id in URL, usually not needed in body but kept for compat
    # The API endpoint takes `rating` inside `review` body.
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
# InboxItem previously wrapped QuizResponse.
# Now it should wrap Card.
# Let's reuse QuizCard for content preview? Or similar.

class InboxCard(BaseModel):
    id: UUID
    type: str
    question: str
    options: List[str] | None = None
    tags: List[str] = []
    created_at: datetime
    
    @model_validator(mode='before')
    @classmethod
    def flatten_inbox(cls, data: Any) -> Any:
        if hasattr(data, "content") and isinstance(data.content, dict):
            content = data.content
            return {
                "id": data.id,
                "type": data.type,
                "question": content.get("question"),
                "options": content.get("options"),
                "tags": data.tags or [],
                "created_at": data.created_at
            }
        return data
        
    class Config:
        from_attributes = True


class InboxItem(InboxCard):
    # Backward compat alias or just use InboxCard
    pass


class InboxAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
