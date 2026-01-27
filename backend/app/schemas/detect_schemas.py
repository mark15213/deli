from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from .source_schemas import SourceType

class DetectRequest(BaseModel):
    input: str
    check_connectivity: bool = True

class PreviewMetadata(BaseModel):
    title: str = "Unknown Source"
    description: Optional[str] = None
    icon_url: Optional[str] = None
    author: Optional[str] = None
    url: Optional[str] = None
    image: Optional[str] = None # og:image or similar

class SuggestedConfig(BaseModel):
    fetch_mode: str = "SNAPSHOT" # SNAPSHOT vs MONITOR
    recurrence: str = "ONCE"     # ONCE, HOURLY, DAILY, etc
    tags: List[str] = []
    
class FormSchema(BaseModel):
    allow_frequency_setting: bool = False
    allow_depth_setting: bool = False
    default_tags: List[str] = []

class DetectResponse(BaseModel):
    status: str = "success"
    detected_type: SourceType
    metadata: PreviewMetadata
    suggested_config: Dict[str, Any]
    form_schema: Optional[FormSchema] = None
