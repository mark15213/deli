# SQLAlchemy models for the application
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum, JSON, Integer, Float, Boolean, UniqueConstraint, Index, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

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
    
    # FSRS global settings and daily limits
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    oauth_connections: Mapped[List["OAuthConnection"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sync_configs: Mapped[List["SyncConfig"]] = relationship(back_populates="user", cascade="all, delete-orphan")
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


class SyncConfig(Base):
    """Configuration for syncing external data."""
    __tablename__ = "sync_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    source_type: Mapped[str] = mapped_column(String(50))  # 'notion_database'
    external_id: Mapped[str] = mapped_column(String(255)) # Notion Database ID
    filter_config: Mapped[dict] = mapped_column(JSONB, default=dict)
    
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="sync_configs")
    source_materials: Mapped[List["SourceMaterial"]] = relationship(back_populates="config")


class SourceMaterial(Base):
    """Tracked external content source (e.g. specific Notion page)."""
    __tablename__ = "source_materials"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    config_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("sync_configs.id", ondelete="SET NULL"), nullable=True)
    
    external_id: Mapped[str] = mapped_column(String(255)) # Notion Page ID
    external_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    raw_snippet: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('user_id', 'external_id', name='uq_source_user_extid'),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="source_materials")
    config: Mapped["SyncConfig"] = relationship(back_populates="source_materials")
    cards: Mapped[List["Card"]] = relationship(back_populates="source_material")


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
    cards: Mapped[List["Card"]] = relationship(back_populates="deck", cascade="all, delete-orphan")
    subscribers: Mapped[List["DeckSubscription"]] = relationship(back_populates="deck", cascade="all, delete-orphan")


class Card(Base):
    """Flashcard content."""
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deck_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decks.id", ondelete="CASCADE"), index=True)
    source_material_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("source_materials.id", ondelete="SET NULL"), nullable=True)
    
    type: Mapped[str] = mapped_column(String(30)) # 'mcq', 'cloze', 'code'
    content: Mapped[dict] = mapped_column(JSONB) # Q/A, options, etc
    
    # 1536 dim vector for OpenAI embeddings
    embedding = mapped_column(Vector(1536))
    
    status: Mapped[CardStatus] = mapped_column(Enum(CardStatus), default=CardStatus.PENDING)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    deck: Mapped["Deck"] = relationship(back_populates="cards")
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
