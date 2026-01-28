# Generic Card API routes (CRUD)
from uuid import UUID
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models import User, Card

router = APIRouter(prefix="/cards", tags=["cards"])

@router.delete("/{card_id}")
async def delete_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Delete a card by ID.
    User must be the owner.
    """
    stmt = select(Card).where(Card.id == card_id, Card.owner_id == current_user.id)
    result = await db.execute(stmt)
    card = result.scalar_one_or_none()

    if not card:
        raise HTTPException(status_code=404, detail="Card not found")

    await db.delete(card)
    await db.commit()

    return {"status": "deleted", "card_id": str(card_id)}
