from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from app.models.snapshot import ContentFormatEnum, SnapshotStatusEnum


class SnapshotCreate(BaseModel):
    title: str = Field(max_length=500)
    url: str = Field(max_length=1000)
    summary: str | None = None
    content: str | None = None
    content_format: ContentFormatEnum = ContentFormatEnum.MARKDOWN
    images: dict | None = None
    metadata: dict | None = None
    subscription_id: uuid.UUID | None = None


class SnapshotUpdate(BaseModel):
    title: str | None = Field(None, max_length=500)
    summary: str | None = None
    content: str | None = None
    content_format: ContentFormatEnum | None = None
    images: dict | None = None
    metadata: dict | None = None
    status: SnapshotStatusEnum | None = None


class SnapshotResponse(BaseModel):
    id: uuid.UUID
    subscription_id: uuid.UUID | None
    user_id: uuid.UUID
    title: str
    url: str
    summary: str | None
    content: str | None
    content_format: ContentFormatEnum
    images: dict | None
    metadata: dict | None
    status: SnapshotStatusEnum
    added_at: datetime
    processed_at: datetime | None

    class Config:
        from_attributes = True
