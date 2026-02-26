"""extract_figures handler — pulls figures from a PDF (or arxiv source)."""

from __future__ import annotations

import logging
import re
from typing import Any

from app.operators.base import RunContext
from app.services.pdf_extractor import (
    extract_figures_from_arxiv_source,
    extract_figures_from_pdf,
    get_figure_info_for_prompt,
    save_figures_to_local,
)

logger = logging.getLogger(__name__)


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    pdf_bytes: bytes = inputs["pdf_bytes"]
    url: str | None = inputs.get("url")

    figures = []

    # Try arxiv source extraction first (higher quality figures)
    if url and "arxiv.org" in url:
        arxiv_match = re.search(r"(\d{4}\.\d{4,5})", url)
        if arxiv_match:
            arxiv_id = arxiv_match.group(1)
            try:
                figures = extract_figures_from_arxiv_source(arxiv_id)
                logger.info("Extracted %d figures from arxiv source", len(figures))
            except Exception:
                logger.warning("Arxiv source extraction failed, falling back to PDF", exc_info=True)

    # Fallback to PDF extraction
    if not figures:
        figures = extract_figures_from_pdf(pdf_bytes)

    # Save to disk
    saved_paths: list[str] = []
    if figures and context.source_id:
        saved_paths = save_figures_to_local(context.source_id, figures)

    images = [fig.image_bytes for fig in figures]
    figure_info = get_figure_info_for_prompt(figures)

    return {
        "images": images,
        "figure_info": figure_info,
        "saved_paths": saved_paths,
    }
