"""
Pydantic schemas for Pipeline CRUD and Operator listing APIs.
"""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# OpRef / Step / Edge sub-schemas (mirrors engine models)
# ---------------------------------------------------------------------------

class OpRefSchema(BaseModel):
    id: str
    operator_key: str
    config_overrides: dict[str, Any] = Field(default_factory=dict)


class StepSchema(BaseModel):
    key: str
    label: str = ""
    operators: list[OpRefSchema] = []
    position: dict[str, float] = Field(default_factory=lambda: {"x": 0, "y": 0})


class EdgeSchema(BaseModel):
    id: str
    source_op: str
    source_port: str
    target_op: str
    target_port: str


class PipelineDefinitionSchema(BaseModel):
    """Full DAG definition stored in PipelineTemplate.definition."""
    steps: list[StepSchema] = []
    edges: list[EdgeSchema] = []


# ---------------------------------------------------------------------------
# Pipeline Template CRUD
# ---------------------------------------------------------------------------

class PipelineTemplateCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str = ""
    definition: PipelineDefinitionSchema = Field(default_factory=PipelineDefinitionSchema)


class PipelineTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    definition: Optional[PipelineDefinitionSchema] = None


class PipelineTemplateResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    name: str
    description: str
    is_system: bool
    definition: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Operator manifest (read-only, from registry)
# ---------------------------------------------------------------------------

class PortSchema(BaseModel):
    key: str
    type: str
    description: str = ""
    required: bool = True


class OperatorManifest(BaseModel):
    key: str
    name: str
    kind: str  # "llm" | "tool"
    description: str = ""
    input_ports: list[PortSchema] = []
    output_ports: list[PortSchema] = []


# ---------------------------------------------------------------------------
# Pipeline execution request / response
# ---------------------------------------------------------------------------

class PipelineRunRequest(BaseModel):
    """Trigger pipeline execution for a source."""
    source_id: UUID
    initial_inputs: dict[str, Any] = Field(default_factory=dict)


class PipelineRunResponse(BaseModel):
    status: str
    message: str
    op_outputs: Optional[dict[str, Any]] = None
