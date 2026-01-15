# API routes for inbox management
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import InboxItem, InboxAction

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/pending", response_model=list[InboxItem])
async def get_pending_items(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """Get pending items in inbox."""
    # TODO: Implement inbox retrieval
    return []


@router.post("/{quiz_id}/approve")
async def approve_item(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Approve an inbox item."""
    # TODO: Implement approval logic
    return {"status": "approved", "quiz_id": str(quiz_id)}


@router.post("/{quiz_id}/reject")
async def reject_item(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Reject an inbox item."""
    # TODO: Implement rejection logic
    return {"status": "rejected", "quiz_id": str(quiz_id)}


@router.put("/{quiz_id}")
async def update_item(
    quiz_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Edit an inbox item."""
    # TODO: Implement edit logic
    raise HTTPException(status_code=501, detail="Not implemented")
