from sqlalchemy import Float, Integer, DateTime, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class ProgressStatusEnum(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    MASTERED = "mastered"


class UserCardProgress(Base):
    __tablename__ = "user_card_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", name="uq_user_card"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    card_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("knowledge_cards.id"), nullable=False, index=True)
    status: Mapped[ProgressStatusEnum] = mapped_column(SQLEnum(ProgressStatusEnum), default=ProgressStatusEnum.NEW)
    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    weight: Mapped[float] = mapped_column(Float, default=1.0, index=True)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="card_progress")
    card: Mapped["KnowledgeCard"] = relationship(back_populates="user_progress")
