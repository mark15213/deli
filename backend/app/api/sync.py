# API routes for sync operations
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Source
from app.workers.tasks import sync_notion_content

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger sync for all Sources of the current user.
    """
    import asyncio
    import logging
    logger = logging.getLogger(__name__)

    # 1. Fetch user's sources
    stmt = select(Source).where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    if not sources:
        return {"status": "no_source", "message": "No source configuration found."}
    
    # 2. Trigger async tasks
    triggered_count = 0
    for source in sources:
        # We only have sync implementation for Notion for now, assuming logic inside handles checks
        # But for safety, let's just trigger it.
        # Create asyncio task
        asyncio.create_task(sync_notion_content(str(source.id)))
        logger.info(f"[SYNC] Triggered background sync for source {source.id}")
        triggered_count += 1
        
    return {
        "status": "triggered",
        "sources_count": len(sources),
        "triggered_tasks": triggered_count
    }


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get status of sources."""
    stmt = select(Source).where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    return [
        {
            "source_id": str(src.id),
            "source_type": src.type,
            "name": src.name,
            "last_synced_at": src.last_synced_at,
            "status": src.status
        }
        for src in sources
    ]
