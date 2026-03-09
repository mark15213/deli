from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ContentFormatEnum(str, enum.Enum):
    MARKDOWN = "markdown"
    HTML = "html"


class SnapshotStatusEnum(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    ARCHIVED = "archived"


class Snapshot(Base):
    __tablename__ = "snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("subscriptions.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    content_format: Mapped[ContentFormatEnum] = mapped_column(SQLEnum(ContentFormatEnum), default=ContentFormatEnum.MARKDOWN)
    images: Mapped[dict | None] = mapped_column(JSON)
    metadata: Mapped[dict | None] = mapped_column(JSON)
    status: Mapped[SnapshotStatusEnum] = mapped_column(SQLEnum(SnapshotStatusEnum), default=SnapshotStatusEnum.PENDING, index=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="snapshots")
    subscription: Mapped["Subscription | None"] = relationship(back_populates="snapshots")
    knowledge_cards: Mapped[list["KnowledgeCard"]] = relationship(back_populates="snapshot")
