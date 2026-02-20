"""optimize_images handler — resize/compress images for LLM multimodal input."""

from __future__ import annotations

import io
import logging
from typing import Any

from PIL import Image

from app.operators.base import RunContext

logger = logging.getLogger(__name__)

MAX_DIM = 1024


async def handle(inputs: dict[str, Any], context: RunContext) -> dict[str, Any]:
    raw_images: list[bytes] = inputs["images"]
    optimised: list[bytes] = []

    for img_bytes in raw_images:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")

            w, h = img.size
            if w > MAX_DIM or h > MAX_DIM:
                ratio = min(MAX_DIM / w, MAX_DIM / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)

            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            optimised.append(buf.getvalue())
        except Exception:
            logger.warning("Failed to optimise image, skipping", exc_info=True)

    logger.info("Optimised %d / %d images", len(optimised), len(raw_images))
    return {"images": optimised}
