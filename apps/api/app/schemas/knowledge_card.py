from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.models.knowledge_card import CardTypeEnum


class KnowledgeCardCreate(BaseModel):
    knowledge_base_id: uuid.UUID
    snapshot_id: uuid.UUID | None = None
    card_type: CardTypeEnum
    question: str
    answer: str | None = None
    explanation: str | None = None
    options: list[str] | None = None
    correct_answer: int | list[int] | None = None
    topic: str | None = Field(None, max_length=100)


class KnowledgeCardUpdate(BaseModel):
    question: str | None = None
    answer: str | None = None
    explanation: str | None = None
    options: list[str] | None = None
    correct_answer: int | list[int] | None = None
    topic: str | None = Field(None, max_length=100)


class KnowledgeCardResponse(BaseModel):
    id: uuid.UUID
    knowledge_base_id: uuid.UUID
    snapshot_id: uuid.UUID | None
    card_type: CardTypeEnum
    question: str
    answer: str | None
    explanation: str | None
    options: list[str] | None
    correct_answer: int | list[int] | None
    topic: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CardReviewSubmit(BaseModel):
    is_correct: bool
    time_spent: int | None = None  # seconds
