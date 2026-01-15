# SQLAlchemy models for the application
import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class QuizType(str, PyEnum):
    """Quiz question types."""
    MCQ = "mcq"              # Multiple choice
    TRUE_FALSE = "true_false"
    CLOZE = "cloze"          # Fill in the blank
    CODE_OUTPUT = "code_output"
    SPOT_BUG = "spot_bug"
    REORDER = "reorder"
    FLASHCARD = "flashcard"


class QuizStatus(str, PyEnum):
    """Quiz lifecycle status."""
    PENDING = "pending"      # In inbox, awaiting review
    APPROVED = "approved"    # Ready for review
    REJECTED = "rejected"    # Discarded


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    notion_connections: Mapped[list["NotionConnection"]] = relationship(back_populates="user")
    quizzes: Mapped[list["Quiz"]] = relationship(back_populates="user")
    review_records: Mapped[list["ReviewRecord"]] = relationship(back_populates="user")


class NotionConnection(Base):
    """Notion OAuth connection."""
    __tablename__ = "notion_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    access_token_encrypted: Mapped[str] = mapped_column(Text)
    workspace_id: Mapped[str] = mapped_column(String(255), nullable=True)
    workspace_name: Mapped[str] = mapped_column(String(255), nullable=True)
    selected_databases: Mapped[dict] = mapped_column(JSON, default=dict)
    last_synced_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="notion_connections")


class Quiz(Base):
    """Quiz question model."""
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # Quiz content
    type: Mapped[QuizType] = mapped_column(Enum(QuizType))
    question: Mapped[str] = mapped_column(Text)
    options: Mapped[dict] = mapped_column(JSON, nullable=True)  # For MCQ type
    answer: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Source metadata for deep linking
    source_page_id: Mapped[str] = mapped_column(String(255), nullable=True)
    source_block_id: Mapped[str] = mapped_column(String(255), nullable=True)
    source_page_title: Mapped[str] = mapped_column(String(500), nullable=True)
    source_deep_link: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Metadata
    tags: Mapped[list] = mapped_column(JSON, default=list)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[QuizStatus] = mapped_column(Enum(QuizStatus), default=QuizStatus.PENDING)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="quizzes")
    review_records: Mapped[list["ReviewRecord"]] = relationship(back_populates="quiz")


class ReviewRecord(Base):
    """Spaced repetition review record."""
    __tablename__ = "review_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quizzes.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    
    # FSRS algorithm state
    rating: Mapped[int] = mapped_column()  # 1=Again, 2=Hard, 3=Good, 4=Easy
    fsrs_state: Mapped[dict] = mapped_column(JSON, default=dict)  # stability, difficulty, etc.
    
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    next_review_at: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Relationships
    quiz: Mapped["Quiz"] = relationship(back_populates="review_records")
    user: Mapped["User"] = relationship(back_populates="review_records")
