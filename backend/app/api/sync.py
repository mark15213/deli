# API routes for sync operations
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, SyncConfig
from app.workers.tasks import sync_notion_content

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger sync for all SyncConfigs of the current user.
    """
    # 1. Fetch user's sync configs
    stmt = select(SyncConfig).where(SyncConfig.user_id == current_user.id)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    
    if not configs:
        # Fallback? Maybe return warning or try to create default?
        return {"status": "no_config", "message": "No sync configuration found."}
    
    # 2. Trigger Celery tasks
    task_ids = []
    for config in configs:
        # Use delay() for async execution via Celery
        task = sync_notion_content.delay(str(config.id))
        task_ids.append(str(task.id))
        
    return {
        "status": "triggered",
        "configs_count": len(configs),
        "task_ids": task_ids
    }


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get status of sync configs."""
    stmt = select(SyncConfig).where(SyncConfig.user_id == current_user.id)
    result = await db.execute(stmt)
    configs = result.scalars().all()
    
    return [
        {
            "config_id": str(conf.id),
            "source_type": conf.source_type,
            "last_synced_at": conf.last_synced_at,
            "status": conf.status
        }
        for conf in configs
    ]
