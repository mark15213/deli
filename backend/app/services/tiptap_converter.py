"""
Tiptap converter — builds a Tiptap ProseMirror JSON document
from a source's reading_note cards.
"""
import re
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Card, CardStatus, SourceMaterial, Source


def _md_to_tiptap_nodes(markdown: str, images: Optional[List[str]] = None) -> list:
    """
    Convert a Markdown string into a list of Tiptap JSON nodes.
    Handles: headings (##), paragraphs, bold, italic, code, bullet lists, images.
    """
    nodes: list = []
    lines = markdown.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i]

        # Skip empty lines
        if not line.strip():
            i += 1
            continue

        # Heading detection (## heading)
        heading_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if heading_match:
            level = len(heading_match.group(1))
            text = heading_match.group(2).strip()
            nodes.append({
                "type": "heading",
                "attrs": {"level": level},
                "content": _parse_inline(text),
            })
            i += 1
            continue

        # Bullet list (- item or * item)
        if re.match(r'^[\-\*]\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^[\-\*]\s+', lines[i]):
                item_text = re.sub(r'^[\-\*]\s+', '', lines[i])
                list_items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": _parse_inline(item_text),
                    }],
                })
                i += 1
            nodes.append({
                "type": "bulletList",
                "content": list_items,
            })
            continue

        # Numbered list (1. item)
        if re.match(r'^\d+\.\s+', line):
            list_items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                item_text = re.sub(r'^\d+\.\s+', '', lines[i])
                list_items.append({
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": _parse_inline(item_text),
                    }],
                })
                i += 1
            nodes.append({
                "type": "orderedList",
                "content": list_items,
            })
            continue

        # Blockquote (> text)
        if line.startswith("> "):
            quote_text = line[2:].strip()
            nodes.append({
                "type": "blockquote",
                "content": [{
                    "type": "paragraph",
                    "content": _parse_inline(quote_text),
                }],
            })
            i += 1
            continue

        # Regular paragraph
        nodes.append({
            "type": "paragraph",
            "content": _parse_inline(line),
        })
        i += 1

    # Append images at the end
    if images:
        for img_url in images:
            if img_url and isinstance(img_url, str) and img_url.strip():
                nodes.append({
                    "type": "image",
                    "attrs": {
                        "src": img_url,
                        "alt": "",
                        "title": None,
                    },
                })

    return nodes


def _parse_inline(text: str) -> list:
    """Parse inline markdown (bold, italic, code, links, math) into Tiptap marks and inline nodes."""
    if not text:
        return [{"type": "text", "text": " "}]

    result = []
    # Process inline patterns: **bold**, *italic*, `code`, [text](url), $$blockmath$$, $inlinemath$
    pattern = re.compile(
        r'(\*\*(.+?)\*\*)'          # bold
        r'|(\*(.+?)\*)'             # italic
        r'|(`(.+?)`)'               # inline code
        r'|(\[(.+?)\]\((.+?)\))'    # link
        r'|(\$\$(.*?)\$\$)'         # block math (often appears inline in parsed strings)
        r'|(\$(.*?)\$)'             # inline math
    )

    last_end = 0
    for match in pattern.finditer(text):
        # Add text before this match
        if match.start() > last_end:
            result.append({"type": "text", "text": text[last_end:match.start()]})

        if match.group(2):  # bold
            result.append({
                "type": "text",
                "text": match.group(2),
                "marks": [{"type": "bold"}],
            })
        elif match.group(4):  # italic
            result.append({
                "type": "text",
                "text": match.group(4),
                "marks": [{"type": "italic"}],
            })
        elif match.group(6):  # code
            result.append({
                "type": "text",
                "text": match.group(6),
                "marks": [{"type": "code"}],
            })
        elif match.group(8):  # link
            result.append({
                "type": "text",
                "text": match.group(8),
                "marks": [{"type": "link", "attrs": {"href": match.group(9), "target": "_blank"}}],
            })
        elif match.group(10):  # block math
            result.append({
                "type": "math_display",
                "content": [{"type": "text", "text": match.group(11)}],
            })
        elif match.group(12):  # inline math
            result.append({
                "type": "math_inline",
                "content": [{"type": "text", "text": match.group(13)}],
            })

        last_end = match.end()

    # Add remaining text
    if last_end < len(text):
        result.append({"type": "text", "text": text[last_end:]})

    if not result:
        result.append({"type": "text", "text": text})

    return result


async def build_tiptap_document(
    db: AsyncSession,
    source_id: UUID,
    user_id: UUID,
) -> dict:
    """
    Build an initial Tiptap JSON document from a source's reading_note cards.
    Cards are ordered by batch_index.

    Returns a Tiptap-compatible ProseMirror JSON document:
    {
        "type": "doc",
        "content": [ ... nodes ... ]
    }
    """
    # Find the source and its source_material
    source_stmt = select(Source).where(Source.id == source_id)
    source_result = await db.execute(source_stmt)
    source = source_result.scalar_one_or_none()

    if not source:
        return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Source not found."}]}]}

    # Find source_material linked to this source
    sm_stmt = select(SourceMaterial).where(SourceMaterial.source_id == source_id)
    sm_result = await db.execute(sm_stmt)
    source_material = sm_result.scalar_one_or_none()

    if not source_material:
        return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "No content available."}]}]}

    # Get all reading_note cards for this source_material, ordered by batch_index
    cards_stmt = (
        select(Card)
        .where(
            Card.source_material_id == source_material.id,
            Card.type == "reading_note",
            Card.status.in_([CardStatus.ACTIVE, CardStatus.PENDING]),
        )
        .order_by(
            Card.batch_index.asc().nullsfirst(),
            Card.created_at.asc(),
        )
    )
    cards_result = await db.execute(cards_stmt)
    cards = cards_result.scalars().all()

    if not cards:
        return {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "No reading notes found for this paper. Start writing!"}]}]}

    # Build document nodes
    doc_nodes: list = []

    # Add paper title as H1
    doc_nodes.append({
        "type": "heading",
        "attrs": {"level": 1},
        "content": [{"type": "text", "text": source.name}],
    })

    # Add each reading_note card as a section
    for card in cards:
        content = card.content or {}
        question = content.get("question") or content.get("title", "")
        answer = content.get("answer") or content.get("content", "")
        images = content.get("images") or []

        # Section heading (H2)
        if question:
            doc_nodes.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": _parse_inline(question),
            })

        # Section body
        if answer:
            body_nodes = _md_to_tiptap_nodes(answer, images)
            doc_nodes.extend(body_nodes)
        elif images:
            # No text, just images
            for img_url in images:
                if img_url and isinstance(img_url, str) and img_url.strip():
                    doc_nodes.append({
                        "type": "image",
                        "attrs": {"src": img_url, "alt": "", "title": None},
                    })

        # Add a separator between sections
        doc_nodes.append({"type": "horizontalRule"})

    # Remove trailing horizontal rule
    if doc_nodes and doc_nodes[-1].get("type") == "horizontalRule":
        doc_nodes.pop()

    return {
        "type": "doc",
        "content": doc_nodes,
    }
