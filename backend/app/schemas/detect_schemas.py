from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from .source_schemas import SourceType, SourceCategory


class DetectRequest(BaseModel):
    """Request to detect the type of a source from user input."""
    input: str
    check_connectivity: bool = True


class PreviewMetadata(BaseModel):
    """Metadata extracted from the source for preview."""
    title: str = "Unknown Source"
    description: Optional[str] = None
    icon_url: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None  # og:image or similar


class SubscriptionPreviewItem(BaseModel):
    """Preview item for subscription sources."""
    title: str
    url: str
    date: Optional[str] = None


class SubscriptionHints(BaseModel):
    """
    Additional hints for subscription sources.
    Helps the user understand what they're subscribing to.
    """
    suggested_frequency: str = "DAILY"
    estimated_items_per_day: Optional[int] = None
    preview_items: List[SubscriptionPreviewItem] = Field(default_factory=list)
    form_schema: Optional[Dict[str, Any]] = None  # JSON Schema for config form


class FormSchema(BaseModel):
    """Schema hints for the frontend form."""
    allow_frequency_setting: bool = False
    allow_depth_setting: bool = False
    default_tags: List[str] = Field(default_factory=list)


class DetectResponse(BaseModel):
    """Response from source detection."""
    status: str = "success"
    detected_type: SourceType
    category: SourceCategory  # NEW: SNAPSHOT or SUBSCRIPTION
    metadata: PreviewMetadata
    suggested_config: Dict[str, Any] = Field(default_factory=dict)
    form_schema: Optional[FormSchema] = None
    
    # Subscription-specific hints (only present for subscription types)
    subscription_hints: Optional[SubscriptionHints] = None
