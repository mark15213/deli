from enum import Enum
from typing import List, Optional, Union, Dict, Literal, Any
from pydantic import BaseModel, Field

# --- Enums ---
class SourceType(str, Enum):
    X_SOCIAL = 'X_SOCIAL'
    NOTION_KB = 'NOTION_KB'
    ARXIV_PAPER = 'ARXIV_PAPER'
    GITHUB_REPO = 'GITHUB_REPO'
    WEB_RSS = 'WEB_RSS'

# --- Connection Configs ---

class XConnectionConfig(BaseModel):
    target_username: str
    auth_mode: Literal["API_KEY", "OAUTH_USER"] = "API_KEY"
    api_token: str  # Encrypted in DB

class NotionConnectionConfig(BaseModel):
    workspace_id: str
    integration_token: str
    target_database_id: Optional[str] = None

class ArxivConnectionConfig(BaseModel):
    base_url: str = "http://export.arxiv.org/api/query"
    category_filter: List[str] = ["cs.AI", "cs.LG"]

class GithubConnectionConfig(BaseModel):
    repo_url: str
    branch: str = "main"
    access_token: Optional[str] = None

class RssConnectionConfig(BaseModel):
    url: str
    type: Literal["RSS", "SITEMAP", "SINGLE_PAGE"] = "RSS"

# Union type for Connection Config
ConnectionConfig = Union[
    XConnectionConfig,
    NotionConnectionConfig,
    ArxivConnectionConfig,
    GithubConnectionConfig,
    RssConnectionConfig
]

# --- Ingestion Rules ---

class XIngestionRules(BaseModel):
    scope: Literal["USER_FEED", "BOOKMARKS", "SEARCH_KEYWORD"] = "USER_FEED"
    include_replies: bool = False
    min_likes_threshold: int = 50
    fetch_frequency: Literal["HOURLY", "DAILY", "WEEKLY"] = "HOURLY"
    grouping_strategy: Literal["THREAD", "SINGLE"] = "THREAD"
    ai_instruction: Optional[str] = "Extract core insights and ignore casual banter."

class NotionIngestionRules(BaseModel):
    sync_mode: Literal["INCREMENTAL", "FULL"] = "INCREMENTAL"
    property_map: Dict[str, str] = {"title": "Name", "tags": "Category", "content": "Body"}
    import_nested_pages: bool = True
    ignore_status: List[str] = ["Draft", "Archived"]
    generate_flashcards: bool = True

class ArxivIngestionRules(BaseModel):
    search_query: str
    parsing_depth: Literal["FULL_TEXT", "ABSTRACT_ONLY"] = "FULL_TEXT"
    translate_to: Optional[str] = None
    math_handling: Literal["LATEX", "OCR"] = "LATEX"
    output_format: Dict[str, Union[str, int]] = {"summary_length": "LONG", "key_takeaways_count": 5}

class GithubIngestionRules(BaseModel):
    file_extensions: List[str] = [".md", ".py", ".ts", ".ipynb"]
    ignore_paths: List[str] = ["tests", "docs", "node_modules", "dist"]
    max_file_size_kb: int = 100
    focus_on: Literal["ARCHITECTURE", "CODE_DETAILS"] = "ARCHITECTURE"
    readme_priority: Literal["HIGHEST", "NORMAL"] = "HIGHEST"

class RssIngestionRules(BaseModel):
    content_selector: Optional[str] = "article.post-content"
    exclude_keywords: List[str] = ["hiring", "news"]
    clean_mode: Literal["READABILITY", "RAW"] = "READABILITY"
    auto_tagging: bool = True

# Union type for Ingestion Rules
IngestionRules = Union[
    XIngestionRules,
    NotionIngestionRules,
    ArxivIngestionRules,
    GithubIngestionRules,
    RssIngestionRules
]

# --- Source Schema ---
from uuid import UUID
from datetime import datetime

class SourceCreate(BaseModel):
    name: str
    type: SourceType
    connection_config: Dict[str, Any] # Loose typing for API input, validated by Logic
    ingestion_rules: Dict[str, Any]

class SourceResponse(BaseModel):
    id: UUID
    name: str
    type: SourceType
    ingestion_rules: Dict[str, Any] # connection_config usually sensitive, maybe masked
    status: str
    last_synced_at: Optional[datetime]
    
    class Config:
        from_attributes = True
