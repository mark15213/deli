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
    # 1. Fetch user's sources
    stmt = select(Source).where(Source.user_id == current_user.id)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    if not sources:
        return {"status": "no_source", "message": "No source configuration found."}
    
    # 2. Trigger Celery tasks
    task_ids = []
    for source in sources:
        # Use delay() for async execution via Celery
        task = sync_notion_content.delay(str(source.id))
        task_ids.append(str(task.id))
        
    return {
        "status": "triggered",
        "sources_count": len(sources),
        "task_ids": task_ids
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
