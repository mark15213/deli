from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class KnowledgeBaseCreate(BaseModel):
    title: str = Field(max_length=255)
    description: str | None = None
    icon: str = Field(default="Database", max_length=50)
    color: str = Field(default="blue", max_length=50)
    is_subscribed: bool = True


class KnowledgeBaseUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    icon: str | None = Field(None, max_length=50)
    color: str | None = Field(None, max_length=50)
    is_subscribed: bool | None = None


class KnowledgeBaseResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    icon: str
    color: str
    is_subscribed: bool
    card_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
