# API routes for sync operations
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, NotionConnection
from app.workers.tasks import sync_notion_content

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/trigger")
async def trigger_sync(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually trigger sync for all Notion connections of the current user.
    """
    # 1. Fetch user's connections
    stmt = select(NotionConnection).where(NotionConnection.user_id == current_user.id)
    result = await db.execute(stmt)
    connections = result.scalars().all()
    
    if not connections:
        raise HTTPException(status_code=404, detail="No Notion connections found")
    
    # 2. Trigger Celery tasks
    task_ids = []
    for conn in connections:
        # Use delay() for async execution via Celery
        task = sync_notion_content.delay(str(conn.id))
        task_ids.append(str(task.id))
        
    return {
        "status": "triggered",
        "connections_count": len(connections),
        "task_ids": task_ids
    }


@router.get("/status")
async def get_sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get status of Notion connections (last synced time)."""
    stmt = select(NotionConnection).where(NotionConnection.user_id == current_user.id)
    result = await db.execute(stmt)
    connections = result.scalars().all()
    
    return [
        {
            "connection_id": str(conn.id),
            "workspace_name": conn.workspace_name,
            "last_synced_at": conn.last_synced_at
        }
        for conn in connections
    ]
