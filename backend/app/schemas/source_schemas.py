from enum import Enum
from typing import List, Optional, Union, Dict, Literal, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# --- Enums ---

class SourceCategory(str, Enum):
    """Source category: one-shot snapshot or periodic subscription."""
    SNAPSHOT = 'SNAPSHOT'
    SUBSCRIPTION = 'SUBSCRIPTION'


class SourceType(str, Enum):
    """
    Source types organized by category.
    
    Snapshot types (one-time parse):
    - ARXIV_PAPER: Academic papers from arXiv
    - WEB_ARTICLE: Generic web articles/blog posts
    - TWEET_THREAD: Twitter/X thread
    - GITHUB_REPO: GitHub repository analysis
    - MANUAL_NOTE: User-entered note
    - PDF_DOCUMENT: Uploaded PDF file
    
    Subscription types (periodic sync):
    - RSS_FEED: RSS/Atom feeds
    - HF_DAILY_PAPERS: HuggingFace Daily Papers
    - AUTHOR_BLOG: Author blog monitoring
    """
    # Snapshot Types
    ARXIV_PAPER = 'ARXIV_PAPER'
    WEB_ARTICLE = 'WEB_ARTICLE'
    TWEET_THREAD = 'TWEET_THREAD'
    GITHUB_REPO = 'GITHUB_REPO'
    MANUAL_NOTE = 'MANUAL_NOTE'
    PDF_DOCUMENT = 'PDF_DOCUMENT'
    
    # Subscription Types
    RSS_FEED = 'RSS_FEED'
    HF_DAILY_PAPERS = 'HF_DAILY_PAPERS'
    AUTHOR_BLOG = 'AUTHOR_BLOG'
    
    # Legacy (for backwards compatibility, map to new types)
    X_SOCIAL = 'X_SOCIAL'  # -> TWEET_THREAD
    NOTION_KB = 'NOTION_KB'  # -> keep for Notion integration
    WEB_RSS = 'WEB_RSS'  # -> RSS_FEED


# Helper to determine category from type
SUBSCRIPTION_TYPES = {
    SourceType.RSS_FEED,
    SourceType.HF_DAILY_PAPERS,
    SourceType.AUTHOR_BLOG,
}


def get_category_for_type(source_type: SourceType) -> SourceCategory:
    """Determine the category for a source type."""
    if source_type in SUBSCRIPTION_TYPES:
        return SourceCategory.SUBSCRIPTION
    return SourceCategory.SNAPSHOT


# --- Connection Configs ---

class ArxivConnectionConfig(BaseModel):
    """Connection config for arXiv papers."""
    url: str
    arxiv_id: Optional[str] = None


class WebArticleConnectionConfig(BaseModel):
    """Connection config for web articles."""
    url: str


class GithubConnectionConfig(BaseModel):
    """Connection config for GitHub repos."""
    repo_url: str
    branch: str = "main"
    access_token: Optional[str] = None


class RSSConnectionConfig(BaseModel):
    """Connection config for RSS feeds."""
    url: str


class TweetConnectionConfig(BaseModel):
    """Connection config for tweets/threads."""
    url: str
    tweet_id: Optional[str] = None


# Union type for Connection Config
ConnectionConfig = Union[
    ArxivConnectionConfig,
    WebArticleConnectionConfig,
    GithubConnectionConfig,
    RSSConnectionConfig,
    TweetConnectionConfig,
    Dict[str, Any],  # Fallback for flexibility
]


# --- Source Schemas ---

class SourceCreate(BaseModel):
    """Schema for creating a new source."""
    name: str
    type: SourceType
    connection_config: Dict[str, Any]
    ingestion_rules: Dict[str, Any] = Field(default_factory=dict)
    
    # Subscription-specific (optional, only for subscription types)
    subscription_config: Optional[Dict[str, Any]] = None


class SourceUpdate(BaseModel):
    """Schema for updating a source."""
    name: Optional[str] = None
    ingestion_rules: Optional[Dict[str, Any]] = None
    subscription_config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class SourceMaterialResponse(BaseModel):
    """Response schema for source materials."""
    id: UUID
    title: Optional[str]
    rich_data: Dict[str, Any]
    external_url: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SourceResponse(BaseModel):
    """Response schema for sources."""
    id: UUID
    name: str
    type: SourceType
    category: SourceCategory
    connection_config: Dict[str, Any]
    ingestion_rules: Dict[str, Any]
    subscription_config: Optional[Dict[str, Any]] = None
    status: str
    last_synced_at: Optional[datetime]
    next_sync_at: Optional[datetime] = None
    source_materials: List[SourceMaterialResponse] = []
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# --- Subscription Form Schema ---

class SubscriptionFormField(BaseModel):
    """Schema for a single form field."""
    key: str
    label: str
    type: Literal["text", "number", "select", "multiselect", "toggle", "textarea"]
    required: bool = False
    default: Optional[Any] = None
    options: Optional[List[Dict[str, str]]] = None
    description: Optional[str] = None
    min: Optional[int] = None
    max: Optional[int] = None


class SubscriptionFormSchema(BaseModel):
    """Schema for subscription configuration form."""
    source_type: str
    fields: List[SubscriptionFormField]
