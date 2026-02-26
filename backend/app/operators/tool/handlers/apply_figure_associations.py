"""apply_figure_associations handler — updates reading note cards with figure images."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.models.models import Card
from app.operators.base import RunContext

logger = logging.getLogger(__name__)


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    associations = inputs.get("associations", [])
    saved_paths = inputs.get("saved_paths", [])

    if not associations or not saved_paths:
        logger.info("No associations or saved_paths provided, nothing to apply")
        return {"updated_count": "0"}

    # Parse associations list from LLM output
    assoc_list = associations
    if isinstance(associations, dict) and "associations" in associations:
        assoc_list = associations["associations"]

    # Fetch reading note cards for this source
    stmt = (
        select(Card)
        .where(
            Card.source_material_id == UUID(context.source_material_id),
            Card.type == "reading_note",
        )
        .order_by(Card.batch_index)
    )
    result = await context.db.execute(stmt)
    reading_note_cards = result.scalars().all()

    if not reading_note_cards:
        logger.warning("No reading note cards found for source_material %s", context.source_material_id)
        return {"updated_count": "0"}

    cards_updated = 0
    for assoc in assoc_list:
        section_index = assoc.get("section_index")
        figure_indices = assoc.get("figure_indices", [])

        if not section_index or not figure_indices:
            continue

        # Find the card matching this section index
        matching_card = None
        for card in reading_note_cards:
            if card.batch_index == section_index:
                matching_card = card
                break

        if not matching_card:
            logger.debug("No card found for section_index %d", section_index)
            continue

        # Get image paths for these figure indices
        image_paths = []
        for fig_idx in figure_indices:
            if 0 <= fig_idx < len(saved_paths):
                image_paths.append(saved_paths[fig_idx])

        if image_paths:
            new_content = dict(matching_card.content)
            new_content["images"] = image_paths
            matching_card.content = new_content
            cards_updated += 1
            logger.debug(
                "Added %d images to card %s (section %d)",
                len(image_paths), matching_card.id, section_index,
            )

    await context.db.commit()
    logger.info(
        "Updated %d reading note cards with figure associations for source_material %s",
        cards_updated, context.source_material_id,
    )
    return {"updated_count": str(cards_updated)}
