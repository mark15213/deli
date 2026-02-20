"""
Pipeline CRUD + Operator listing API.

Endpoints:
  GET    /pipelines            — list user + system templates
  POST   /pipelines            — create custom template
  GET    /pipelines/:id        — get one template
  PUT    /pipelines/:id        — update custom template
  DELETE /pipelines/:id        — delete custom template
  POST   /pipelines/:id/clone  — clone a system/user template
  GET    /operators            — list all registered operators
"""
import uuid as uuid_module
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.api import deps
from app.api.deps import is_shared_mode
from app.models.models import User, PipelineTemplate
from app.schemas.pipeline_schemas import (
    PipelineTemplateCreate,
    PipelineTemplateUpdate,
    PipelineTemplateResponse,
    OperatorManifest,
)

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


# ───────────────────────────── Templates ─────────────────────────────


@router.get("", response_model=List[PipelineTemplateResponse])
async def list_pipelines(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Return all system templates + user's custom templates."""
    stmt = select(PipelineTemplate).where(
        or_(
            PipelineTemplate.is_system == True,  # noqa: E712
            PipelineTemplate.user_id == current_user.id,
        )
    ).order_by(PipelineTemplate.is_system.desc(), PipelineTemplate.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=PipelineTemplateResponse, status_code=201)
async def create_pipeline(
    *,
    db: AsyncSession = Depends(deps.get_db),
    body: PipelineTemplateCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a custom pipeline template."""
    template = PipelineTemplate(
        id=uuid_module.uuid4(),
        user_id=current_user.id,
        name=body.name,
        description=body.description,
        is_system=False,
        definition=body.definition.model_dump(),
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.get("/{template_id}", response_model=PipelineTemplateResponse)
async def get_pipeline(
    template_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get a single pipeline template (system or owned by user)."""
    stmt = select(PipelineTemplate).where(PipelineTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Pipeline template not found")
    if not template.is_system and template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return template


@router.put("/{template_id}", response_model=PipelineTemplateResponse)
async def update_pipeline(
    template_id: UUID,
    body: PipelineTemplateUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Update a custom pipeline template (system templates are read-only)."""
    stmt = select(PipelineTemplate).where(PipelineTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Pipeline template not found")
    if template.is_system:
        raise HTTPException(status_code=403, detail="Cannot modify system templates")
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if body.name is not None:
        template.name = body.name
    if body.description is not None:
        template.description = body.description
    if body.definition is not None:
        template.definition = body.definition.model_dump()

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/{template_id}")
async def delete_pipeline(
    template_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Delete a custom pipeline template."""
    stmt = select(PipelineTemplate).where(PipelineTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Pipeline template not found")
    if template.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system templates")
    if template.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(template)
    await db.commit()
    return {"ok": True}


@router.post("/{template_id}/clone", response_model=PipelineTemplateResponse, status_code=201)
async def clone_pipeline(
    template_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Clone a system or user template into the current user's custom templates."""
    stmt = select(PipelineTemplate).where(PipelineTemplate.id == template_id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Pipeline template not found")

    clone = PipelineTemplate(
        id=uuid_module.uuid4(),
        user_id=current_user.id,
        name=f"{source.name} (Copy)",
        description=source.description,
        is_system=False,
        definition=source.definition,
    )
    db.add(clone)
    await db.commit()
    await db.refresh(clone)
    return clone


# ───────────────────────────── Operators ─────────────────────────────


@router.get("/operators/list", response_model=List[OperatorManifest])
async def list_operators(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Return manifests for all registered operators (for the node palette)."""
    from app.operators.registry import get_all_manifests
    return get_all_manifests()
