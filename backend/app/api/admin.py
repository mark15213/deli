# Admin routes for maintenance
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user, require_admin
from app.models import User, Source, SourceLog

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/reset-stuck-sources")
async def reset_stuck_sources(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Reset sources stuck in 'PROCESSING' state to 'FAILED'.
    Useful for cleaning up after a crash.
    """
    stmt = select(Source).where(Source.status == "PROCESSING")
    result = await db.execute(stmt)
    sources = result.scalars().all()
    
    reset_count = 0
    for s in sources:
        s.status = "FAILED"
        s.error_log = "Reset by admin API: stuck in processing."
        
        # Log event
        log = SourceLog(
            source_id=s.id,
            event_type="error",
            status="failed",
            message="Manually reset from stuck state via Admin API."
        )
        db.add(log)
        reset_count += 1
        
    await db.commit()
    
    return {
        "status": "success",
        "reset_count": reset_count,
        "message": f"Reset {reset_count} stuck sources."
    }
