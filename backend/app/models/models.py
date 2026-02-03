# SQLAlchemy models for the application
import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON, Integer, Float, Boolean, UniqueConstraint, Index, ARRAY, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB


from app.core.database import Base


class CardStatus(str, PyEnum):
    """Card lifecycle status."""
    PENDING = "pending"
    ACTIVE = "active"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class FSRSState(str, PyEnum):
    """FSRS learning stage."""
    NEW = "new"
    LEARNING = "learning"
    REVIEW = "review"
    RELEARNING = "relearning"


class User(Base):
    """User model."""
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Auth
    hashed_password: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # FSRS global settings and daily limits
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    oauth_connections: Mapped[List["OAuthConnection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sources: Mapped[List["Source"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    source_materials: Mapped[List["SourceMaterial"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    decks: Mapped[List["Deck"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    study_progress: Mapped[List["StudyProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    subscriptions: Mapped[List["DeckSubscription"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class OAuthConnection(Base):
    """OAuth connection for external providers (Notion, GitHub, etc)."""
    __tablename__ = "oauth_connections"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    provider: Mapped[str] = mapped_column(String(50))  # 'notion', 'github'
    provider_user_id: Mapped[str] = mapped_column(String(255))
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_uid'),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="oauth_connections")


class SourceMaterial(Base):
    """Tracked external content source (e.g. specific Notion page)."""
    __tablename__ = "source_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    
    external_id: Mapped[str] = mapped_column(String(255)) # Notion Page ID
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    raw_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Stores generated artifacts (Summary, Lens Suggestions, etc.)
    rich_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'external_id', name='uq_source_user_extid'),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="source_materials")
    source: Mapped["Source"] = relationship(back_populates="source_materials")
    cards: Mapped[List["Card"]] = relationship(back_populates="source_material")


# Association Tables
card_decks = Table(
    "card_decks",
    Base.metadata,
    Column("card_id", UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
    Column("deck_id", UUID(as_uuid=True), ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True),
)


class Deck(Base):
    """Collection of cards."""
    __tablename__ = "decks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    cover_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    owner: Mapped["User"] = relationship(back_populates="decks")
    cards: Mapped[List["Card"]] = relationship(secondary=card_decks, back_populates="decks")
    subscribers: Mapped[List["DeckSubscription"]] = relationship(back_populates="deck", cascade="all, delete-orphan")


class Card(Base):
    """Flashcard content."""
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    source_material_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("source_materials.id", ondelete="SET NULL"), nullable=True)
    
    type: Mapped[str] = mapped_column(String(30)) # 'mcq', 'cloze', 'code'
    content: Mapped[dict] = mapped_column(JSONB) # Q/A, options, etc
    
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.PENDING)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    # Batch grouping for series notes (e.g., paper reading notes)
    batch_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    batch_index: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    decks: Mapped[List["Deck"]] = relationship(secondary=card_decks, back_populates="cards")
    source_material: Mapped["SourceMaterial"] = relationship(back_populates="cards")
    study_progress: Mapped[List["StudyProgress"]] = relationship(back_populates="card", cascade="all, delete-orphan")


class DeckSubscription(Base):
    """User subscriptions to decks."""
    __tablename__ = "deck_subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    deck_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decks.id", ondelete="CASCADE"), primary_key=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    deck: Mapped["Deck"] = relationship(back_populates="subscribers")


class StudyProgress(Base):
    """FSRS learning progress for a card per user."""
    __tablename__ = "study_progress"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"))
    
    # FSRS Core
    stability: Mapped[float] = mapped_column(Float, default=0.0)
    difficulty: Mapped[float] = mapped_column(Float, default=0.0)
    elapsed_days: Mapped[float] = mapped_column(Float, default=0.0)
    scheduled_days: Mapped[float] = mapped_column(Float, default=0.0)
    retrievability: Mapped[float] = mapped_column(Float, default=0.0)
    
    state: Mapped[FSRSState] = mapped_column(Enum(FSRSState), default=FSRSState.NEW)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'card_id', name='uq_study_user_card'),
        Index('idx_study_queue', 'user_id', 'due_date'),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="study_progress")
    card: Mapped["Card"] = relationship(back_populates="study_progress")


class ReviewLog(Base):
    """History of reviews for a card."""
    __tablename__ = "review_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    card_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    
    grade: Mapped[int] = mapped_column(Integer) # 1-4
    
    state_before: Mapped[Optional[FSRSState]] = mapped_column(Enum(FSRSState), nullable=True)
    stability_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_before: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    review_duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # No relationships defined for simple log table to avoid overhead, 
    # but can add if needed.

class Source(Base):
    """
    Core Source entity for content ingestion.
    
    Category Types:
    - SNAPSHOT: One-time parse (papers, articles, tweets, repos)
    - SUBSCRIPTION: Periodic sync (RSS, HF Daily, author blogs)
    """
    __tablename__ = "sources"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    parent_source_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50))  # e.g. 'ARXIV_PAPER', 'RSS_FEED'
    category: Mapped[str] = mapped_column(String(20), default="SNAPSHOT")  # SNAPSHOT | SUBSCRIPTION
    
    # Connection Config (Static)
    # Stores: url, auth_token, api_keys
    connection_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Ingestion Rules (Dynamic/User Tunable)
    # Stores: lens configs, prompts
    ingestion_rules: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    # Subscription-specific config (only for SUBSCRIPTION category)
    # Stores: sync_frequency, filters, etc. - schema varies by type
    subscription_config: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Status: PENDING, PROCESSING, COMPLETED (snapshot), ACTIVE, PAUSED, ERROR
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    next_sync_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # For subscriptions
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sources")
    source_materials: Mapped[List["SourceMaterial"]] = relationship(back_populates="source")
    logs: Mapped[List["SourceLog"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    parent: Mapped[Optional["Source"]] = relationship("Source", remote_side=[id], back_populates="children", foreign_keys=[parent_source_id])
    children: Mapped[List["Source"]] = relationship("Source", back_populates="parent", foreign_keys="[Source.parent_source_id]")


class SourceLog(Base):
    """
    Logs for Source processing events (lens runs, syncs, errors).
    """
    __tablename__ = "source_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), index=True)
    
    # Event type: 'lens_started', 'lens_completed', 'lens_failed', 'sync_started', 'sync_completed', 'error'
    event_type: Mapped[str] = mapped_column(String(50))
    
    # Lens key if applicable (e.g., 'default_summary', 'reading_notes')
    lens_key: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status: 'running', 'completed', 'failed'
    status: Mapped[str] = mapped_column(String(20))
    
    # Message/details
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Duration in milliseconds
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Additional data (token usage, etc.)
    extra_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="logs")
