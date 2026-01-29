from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models import User, Source, SourceMaterial
from app.core.lens import SourceData, Artifact
from app.lenses.registry import get_lens_by_key, Lens
from app.services.runner_service import RunnerService

router = APIRouter(prefix="/paper", tags=["paper"])

@router.post("/run-lens", response_model=Dict[str, Any])
async def run_lens(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    source_id: UUID = Body(..., embed=True),
    lens_key: str = Body(..., embed=True),
) -> Any:
    """
    Run a specific lens on a paper source.
    """
    # 1. Fetch Source
    stmt = select(Source).where(Source.id == source_id, Source.user_id == current_user.id)
    result = await db.execute(stmt)
    source = result.scalar_one_or_none()
    
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
        
    # 2. Fetch SourceMaterial to get content
    stmt_mat = select(SourceMaterial).where(SourceMaterial.source_id == source.id)
    res_mat = await db.execute(stmt_mat)
    material = res_mat.scalars().first()
    
    # Needs content. If material exists use its rich_data raw content or re-fetch?
    # SourceData expects 'text'.
    # In RunnerService.process_new_source we didn't save 'text' to DB except maybe 'raw_snippet' or implicit.
    # We should probably have saved the full text in SourceMaterial or somewhere? 
    # For now, let's re-fetch or use what we have. 
    # WAIT, `process_new_source` in `runner_service` creates `SourceMaterial` but doesn't populate `raw_snippet` with full text necessarily (schema says `raw_snippet` is Text).
    
    runner = RunnerService(db)
    
    # If we have stored text in raw_snippet, use it
    text_content = ""
    if material and material.raw_snippet:
        text_content = material.raw_snippet
    else:
        # Fallback to re-fetch
        text_content = await runner._fetch_source_text(source)
        
    if not text_content:
         raise HTTPException(status_code=400, detail="Could not retrieve source content")
         
    source_data = SourceData(
        id=str(source.id),
        text=text_content,
        metadata={"title": source.name}
    )
    
    # 3. Get Lens
    try:
        lens = get_lens_by_key(lens_key)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Lens '{lens_key}' not found")
        
    # 4. Run
    artifact = await runner.run_lens(source_data, lens)
    
    # 5. Persist?
    # Optionally save to rich_data['artifacts'] list?
    # For now iterate on rich_data schema
    if material:
        if material.rich_data is None:
            material.rich_data = {}
        
        # Clone and update
        new_data = dict(material.rich_data)
        # Maybe store under a 'lenses' key
        if "lenses" not in new_data:
            new_data["lenses"] = {}
        
        new_data["lenses"][lens_key] = artifact.content
        material.rich_data = new_data
        await db.commit()
    
    return artifact.model_dump()
