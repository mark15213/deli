# Subscription configuration classes for each source type
from typing import List, Optional
from pydantic import Field
from .base import BaseSubscriptionConfig


class RSSSubscriptionConfig(BaseSubscriptionConfig):
    """
    Configuration for RSS/Atom Feed subscriptions.
    """
    max_items_per_sync: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum items to fetch per sync"
    )
    title_include_keywords: List[str] = Field(
        default_factory=list,
        description="Only include items with titles containing these keywords (OR logic)"
    )
    title_exclude_keywords: List[str] = Field(
        default_factory=list,
        description="Exclude items with titles containing these keywords"
    )
    content_min_length: int = Field(
        default=100,
        ge=0,
        description="Minimum content length to include (filters out short posts)"
    )


class HFDailyPapersConfig(BaseSubscriptionConfig):
    """
    Configuration for HuggingFace Daily Papers subscription.
    """
    categories: List[str] = Field(
        default_factory=lambda: ["All"],
        description="Paper categories to include (e.g., 'NLP', 'CV', 'RL')"
    )
    min_upvotes: int = Field(
        default=0,
        ge=0,
        description="Minimum upvotes to include a paper"
    )
    include_abstracts: bool = Field(
        default=True,
        description="Whether to fetch paper abstracts"
    )
    max_papers_per_sync: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum papers to fetch per sync"
    )


class AuthorBlogConfig(BaseSubscriptionConfig):
    """
    Configuration for monitoring an author's blog for new posts.
    """
    content_selector: Optional[str] = Field(
        default="article",
        description="CSS selector for article content"
    )
    link_selector: Optional[str] = Field(
        default="a.post-link, article a, .post a",
        description="CSS selector for post links"
    )
    date_selector: Optional[str] = Field(
        default="time, .date, .published",
        description="CSS selector for post dates"
    )
    max_pages_to_crawl: int = Field(
        default=1,
        ge=1,
        le=5,
        description="How many pages to check for new posts"
    )
    url_pattern: Optional[str] = Field(
        default=None,
        description="Regex pattern to filter valid post URLs"
    )
