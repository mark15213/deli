"""
Paper API — run an operator on a paper source on-demand.

This replaces the old `/run-lens` endpoint with an operator-based approach
that uses the same operators registered in the pipeline system.
"""

from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models import User, Source, SourceMaterial
from app.operators.base import RunContext
from app.operators.registry import get_operator

router = APIRouter(prefix="/paper", tags=["paper"])


@router.post("/run-operator", response_model=Dict[str, Any])
async def run_operator(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    source_id: UUID = Body(..., embed=True),
    operator_key: str = Body(..., embed=True),
) -> Any:
    """
    Run a specific operator on a paper source.
    """
    # 1. Fetch Source
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()

    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    # 2. Fetch SourceMaterial
    stmt_mat = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
    res_mat = await db.execute(stmt_mat)
    material = res_mat.scalars().first()

    if not material:
        raise HTTPException(status_code=400, detail="No source material found — process the source first")

    # 3. Get operator
    try:
        operator = get_operator(operator_key)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Operator '{operator_key}' not found")

    # 4. Build context
    context = RunContext(
        db=db,
        source_id=str(source.id),
        user_id=str(current_user.id),
        source_material_id=str(material.id),
    )

    # 5. Build inputs from raw_snippet or stored text
    text_content = material.raw_snippet or ""
    if not text_content:
        raise HTTPException(status_code=400, detail="No text content available for this source")

    inputs = {"text": text_content}

    # 6. Run
    result = await operator.execute(inputs, context)
    await db.commit()

    return {"operator_key": operator_key, "result": result}
