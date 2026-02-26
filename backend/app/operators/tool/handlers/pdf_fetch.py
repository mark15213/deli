"""pdf_fetch handler — downloads a PDF and extracts text."""

from __future__ import annotations

import logging
from typing import Any

import fitz  # PyMuPDF
import requests

from app.operators.base import RunContext

logger = logging.getLogger(__name__)


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    url = inputs["url"]

    # Normalise arxiv abs → pdf
    if "arxiv.org" in url:
        url = url.replace("/abs/", "/pdf/")
        if not url.endswith(".pdf"):
            url += ".pdf"

    logger.info("Downloading PDF from %s", url)
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    pdf_bytes = response.content

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text_parts = [page.get_text() for page in doc]
    doc.close()

    text = "\n".join(text_parts)
    logger.info("Extracted %d chars from PDF (%d pages)", len(text), len(text_parts))

    return {"text": text, "pdf_bytes": pdf_bytes}
