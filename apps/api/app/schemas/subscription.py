from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.models.subscription import FrequencyEnum


class SubscriptionCreate(BaseModel):
    title: str = Field(max_length=255)
    url: str = Field(max_length=500)
    frequency: FrequencyEnum


class SubscriptionUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    url: str | None = Field(None, max_length=500)
    frequency: FrequencyEnum | None = None
    is_active: bool | None = None


class SubscriptionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    url: str
    frequency: FrequencyEnum
    is_active: bool
    last_fetched_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
