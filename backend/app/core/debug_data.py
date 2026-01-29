# Debug data utilities - now mostly handled by seed_data.py
# This file is kept for any additional debug-specific utilities

import logging

from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def reseed_debug_sources(db: AsyncSession):
    """
    Placeholder for backward compatibility.
    Source seeding is now handled by seed_data.reset_seed_data()
    """
    # All source seeding is now done in seed_data.py
    # This function is kept for backward compatibility with main.py
    logger.info("Debug sources will be seeded as part of main seed data...")
    pass
