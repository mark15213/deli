# Background Sync Scheduler
# Runs in background and triggers sync for subscription sources at their configured sync hour

import asyncio
import logging
from datetime import datetime, timezone, date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.models.models import Source

logger = logging.getLogger(__name__)

# Global flag to stop scheduler
_scheduler_running = False

async def check_and_sync_subscriptions():
    """Check for subscription sources that need to sync and trigger them."""
    current_hour = datetime.now().hour
    today = date.today()
    
    logger.info(f"[SCHEDULER] Checking subscriptions at hour {current_hour}")
    
    try:
        async with async_session_maker() as db:
            # Get all subscription sources that are ACTIVE
            stmt = select(Source).where(
                Source.category == "SUBSCRIPTION",
                Source.status == "ACTIVE"
            )
            result = await db.execute(stmt)
            sources = result.scalars().all()
            
            for source in sources:
                try:
                    await maybe_sync_source(db, source, current_hour, today)
                except Exception as e:
                    logger.error(f"[SCHEDULER] Error checking source {source.id}: {e}")
                    
    except Exception as e:
        logger.error(f"[SCHEDULER] Error in subscription check: {e}")


async def maybe_sync_source(db: AsyncSession, source: Source, current_hour: int, today: date):
    """Check if source should sync and trigger if needed."""
    config = source.subscription_config or {}
    
    # Get sync hour from config, default 20 (8 PM)
    sync_hour = config.get("sync_hour", 20)
    enabled = config.get("enabled", True)
    
    if not enabled:
        return
    
    if current_hour != sync_hour:
        return
    
    # Check if already synced today
    if source.last_synced_at:
        last_sync_date = source.last_synced_at.date()
        if last_sync_date >= today:
            logger.debug(f"[SCHEDULER] Source {source.name} already synced today")
            return
    
    # Trigger sync
    logger.info(f"[SCHEDULER] Triggering auto-sync for: {source.name}")
    
    # Import here to avoid circular imports
    from app.api.sources import sync_source_internal
    
    try:
        await sync_source_internal(db, source)
        logger.info(f"[SCHEDULER] Auto-sync completed for: {source.name}")
    except Exception as e:
        logger.error(f"[SCHEDULER] Auto-sync failed for {source.name}: {e}")


async def run_scheduler():
    """Main scheduler loop - checks every 5 minutes."""
    global _scheduler_running
    _scheduler_running = True
    
    logger.info("[SCHEDULER] Starting subscription sync scheduler")
    
    while _scheduler_running:
        try:
            await check_and_sync_subscriptions()
        except Exception as e:
            logger.error(f"[SCHEDULER] Scheduler error: {e}")
        
        # Wait 5 minutes before next check
        await asyncio.sleep(300)
    
    logger.info("[SCHEDULER] Scheduler stopped")


def stop_scheduler():
    """Stop the scheduler loop."""
    global _scheduler_running
    _scheduler_running = False


async def start_scheduler_task():
    """Start scheduler as background task."""
    asyncio.create_task(run_scheduler())
