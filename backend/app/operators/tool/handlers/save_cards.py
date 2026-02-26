"""save_cards handler — persists card items to the database."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.models.models import Card, CardStatus
from app.operators.base import RunContext

logger = logging.getLogger(__name__)


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    items = inputs["items"]
    card_type = inputs["card_type"]
    batch_id = uuid.uuid4()

    cards = []
    for idx, item in enumerate(items):
        card = Card(
            id=uuid.uuid4(),
            owner_id=uuid.UUID(context.user_id),
            source_material_id=uuid.UUID(context.source_material_id),
            type=card_type,
            content=item if isinstance(item, dict) else {"question": "", "answer": str(item)},
            status=CardStatus.PENDING,
            batch_id=batch_id,
            batch_index=idx,
        )
        cards.append(card)

    context.db.add_all(cards)
    await context.db.commit()

    logger.info("Saved %d cards (type=%s, batch=%s)", len(cards), card_type, batch_id)
    return {"batch_id": str(batch_id), "count": str(len(cards))}
