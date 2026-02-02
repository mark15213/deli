# Base classes for subscription system
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
from datetime import datetime


class SyncFrequency(str, Enum):
    """Sync frequency options for subscription sources."""
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class BaseSubscriptionConfig(BaseModel):
    """
    Base configuration for all subscription types.
    Subclasses add type-specific fields.
    """
    sync_frequency: SyncFrequency = Field(
        default=SyncFrequency.DAILY,
        description="How often to check for new content"
    )
    enabled: bool = Field(
        default=True,
        description="Whether this subscription is active"
    )
    last_cursor: Optional[str] = Field(
        default=None,
        description="Cursor for incremental sync (e.g., last seen ID, timestamp)"
    )
    last_synced_at: Optional[datetime] = Field(
        default=None,
        description="Last successful sync timestamp"
    )
    
    class Config:
        use_enum_values = True


class FetchedItem(BaseModel):
    """
    Represents a single item fetched from a subscription source.
    This will be converted to a Snapshot Source for processing.
    """
    external_id: str = Field(description="Unique identifier from the source")
    title: str = Field(description="Title of the content")
    url: str = Field(description="URL to the full content")
    published_at: Optional[datetime] = Field(
        default=None,
        description="When the content was published"
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional metadata (author, tags, etc.)"
    )


class BaseFetcher(ABC):
    """
    Abstract base class for subscription content fetchers.
    Each subscription type implements its own fetcher.
    """
    
    @abstractmethod
    async def fetch_new_items(
        self, 
        config: BaseSubscriptionConfig,
        connection_config: dict,
        since_cursor: Optional[str] = None
    ) -> Tuple[List[FetchedItem], Optional[str]]:
        """
        Fetch new items from the subscription source.
        
        Args:
            config: The subscription-specific configuration
            connection_config: Connection details (URL, auth, etc.)
            since_cursor: Optional cursor for incremental sync
            
        Returns:
            Tuple of (list of fetched items, new cursor for next sync)
        """
        pass
    
    @abstractmethod
    def get_snapshot_source_type(self) -> str:
        """
        Returns the SourceType that fetched items should be created as.
        E.g., RSS items might become WEB_ARTICLE snapshots.
        """
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """Human-readable name for this fetcher type."""
        pass
