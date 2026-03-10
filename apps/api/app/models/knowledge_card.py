from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class CardTypeEnum(str, enum.Enum):
    FLASHCARD = "flashcard"
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"


class KnowledgeCard(Base):
    __tablename__ = "knowledge_cards"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    knowledge_base_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_bases.id"), nullable=False, index=True)
    snapshot_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("snapshots.id"), index=True)
    card_type: Mapped[CardTypeEnum] = mapped_column(SQLEnum(CardTypeEnum), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    options: Mapped[list | None] = mapped_column(JSON)
    correct_answer: Mapped[int | list | None] = mapped_column(JSON)
    topic: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    knowledge_base: Mapped["KnowledgeBase"] = relationship(back_populates="cards")
    snapshot: Mapped["Snapshot | None"] = relationship(back_populates="knowledge_cards")
    user_progress: Mapped[list["UserCardProgress"]] = relationship(back_populates="card", cascade="all, delete-orphan")
