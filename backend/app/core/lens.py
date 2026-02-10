from typing import Any, Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class SourceData(BaseModel):
    """
    Stateless wrapper for raw content to be processed by a Lens.
    """
    id: str  # Can be SourceMaterial.id or Source.id
    text: Optional[str] = None
    base64_data: Optional[str] = None
    mime_type: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    images: Optional[List[bytes]] = None # For multimodal lenses

class Lens(BaseModel):
    """
    Configuration object defining how to process a Source.
    """
    key: str # Unique identifier e.g. "default_summary", "profiler"
    name: str # Display name
    description: str
    system_prompt: str
    user_prompt_template: str # Jinja2 style or f-string template expecting {text}
    output_schema: Optional[Dict[str, Any]] = None # JSON Schema if structured output is needed
    parameters: Dict[str, Any] = Field(default_factory=dict)

class Artifact(BaseModel):
    """
    The result of applying a Lens to a Source.
    """
    lens_key: str
    source_id: str
    content: Any # String or Dict depending on output_schema
    created_at: float
    usage: Optional[Dict[str, int]] = None # Token usage
