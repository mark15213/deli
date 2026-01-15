# API routes for statistics
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas import DashboardStats

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard statistics."""
    # TODO: Implement stats retrieval
    return DashboardStats(
        today_reviewed=0,
        today_remaining=0,
        streak_days=0,
        total_mastered=0,
    )
