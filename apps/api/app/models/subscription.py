from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import uuid
import enum
from app.database import Base


class FrequencyEnum(str, enum.Enum):
    DAILY = "Daily"
    WEEKLY = "Weekly"
    MANUAL = "Manual"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    frequency: Mapped[FrequencyEnum] = mapped_column(SQLEnum(FrequencyEnum), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_fetched_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    snapshots: Mapped[list["Snapshot"]] = relationship(back_populates="subscription", cascade="all, delete-orphan")
