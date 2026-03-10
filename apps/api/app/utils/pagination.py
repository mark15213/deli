from math import ceil
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(query, session: AsyncSession, page: int = 1, limit: int = 20):
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await session.scalar(count_query)

    # Calculate pagination
    pages = ceil(total / limit) if total > 0 else 0
    offset = (page - 1) * limit

    # Get items
    items_query = query.limit(limit).offset(offset)
    result = await session.execute(items_query)
    items = result.scalars().all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages,
    }
