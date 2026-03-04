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

from app.models.models import Card, CardStatus, SourceMaterial, Source, SourceEdit

import logging
logger = logging.getLogger(__name__)


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

        # Table detection: | col1 | col2 | with |---|---| separator
        if line.strip().startswith("|") and line.strip().endswith("|"):
            # Collect all table lines
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1

            if len(table_lines) >= 2:
                # Check for separator row (|---|---|)
                sep_idx = None
                for idx, tl in enumerate(table_lines):
                    cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                    if all(re.match(r'^:?-{1,}:?$', c) for c in cells):
                        sep_idx = idx
                        break

                table_rows = []
                for idx, tl in enumerate(table_lines):
                    if idx == sep_idx:
                        continue  # Skip separator row
                    cells = [c.strip() for c in tl.strip().strip("|").split("|")]
                    # Rows before separator (or first row if no separator) are header rows
                    is_header = sep_idx is not None and idx < sep_idx
                    cell_type = "tableHeader" if is_header else "tableCell"
                    row_cells = []
                    for cell_text in cells:
                        row_cells.append({
                            "type": cell_type,
                            "content": [{
                                "type": "paragraph",
                                "content": _parse_inline(cell_text),
                            }],
                        })
                    table_rows.append({
                        "type": "tableRow",
                        "content": row_cells,
                    })

                if table_rows:
                    nodes.append({
                        "type": "table",
                        "content": table_rows,
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



async def sync_tiptap_to_cards(db: AsyncSession, source_id: UUID, user_id: UUID, tiptap_json: dict) -> None:
    """
    Reverse process: take edited Tiptap JSON, split by 'Heading 2' (sections), 
    and update the corresponding `reading_note` cards for this source.
    """
    # 1. Find source_material linked to this source
    sm_stmt = select(SourceMaterial).where(SourceMaterial.source_id == source_id)
    sm_result = await db.execute(sm_stmt)
    source_material = sm_result.scalar_one_or_none()
    
    if not source_material:
        logger.warning(f"No source material found for source {source_id}, cannot sync cards.")
        return
        
    # 2. Extract sections from Tiptap JSON
    # A section is defined by a Heading 2, and everything under it until the next H1/H2 (or horizontal rule)
    content_nodes = tiptap_json.get("content", [])
    logger.info(f"sync_tiptap_to_cards: Parsing Tiptap JSON with {len(content_nodes)} nodes")
    
    sections = []
    current_section = None

    
    def _extract_images_from_node(node: dict) -> list:
        """Recursively find all image src URLs within a node tree."""
        imgs = []
        if node.get("type") == "image":
            src = node.get("attrs", {}).get("src")
            if src:
                imgs.append(src)
        for child in node.get("content", []):
            imgs.extend(_extract_images_from_node(child))
        return imgs

    for node in content_nodes:
        if node.get("type") == "heading" and node.get("attrs", {}).get("level") == 2:
            # Commit previous section
            if current_section:
                sections.append(current_section)
                
            # Start new section
            # Extract text from heading node
            heading_text = ""
            for child in node.get("content", []):
                if child.get("type") == "text":
                    heading_text += child.get("text", "")
                    
            current_section = {
                "question": heading_text,
                "answer_nodes": [],
                "images": []
            }
        elif node.get("type") == "horizontalRule" or (node.get("type") == "heading" and node.get("attrs", {}).get("level") == 1):
            pass # Ignore H1 and HR for reading notes bodies
        elif current_section is not None:
            # It's part of the current section's body
            # Extract images from this node (including nested ones)
            found_images = _extract_images_from_node(node)
            if found_images:
                current_section["images"].extend(found_images)
                logger.info(f"sync_tiptap_to_cards: Found {len(found_images)} image(s) in node type={node.get('type')}")
            
            # Also keep the node as an answer node (unless it's purely an image)
            if node.get("type") != "image":
                current_section["answer_nodes"].append(node)
                
    # Don't forget the last section
    if current_section:
        sections.append(current_section)
        
    logger.info(f"sync_tiptap_to_cards: Extracted {len(sections)} H2 sections")
        
    if not sections:
        logger.warning(f"No H2 sections found in editor output for source {source_id}. Skipping sync.")
        return


    # Convert answer nodes back to pseudo-markdown or plain text for the 'answer' field
    # For now, we'll serialize the JSON back to a rudimentary text representation, or just store the json text.
    # The frontend Study page NoteCard expects markdown. Let's do a basic conversion.
    
    
    # 3. Fetch existing `reading_note` cards
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
    existing_cards = cards_result.scalars().all()
    
    batch_id = existing_cards[0].batch_id if existing_cards else None
    
    # 4. Map and update or insert/delete
    logger.info(f"sync_tiptap_to_cards: Found {len(existing_cards)} existing cards")
    for idx, section in enumerate(sections):
        # Build markdown string from answer_nodes
        md_answer = json_to_markdown(section["answer_nodes"])
        
        logger.info(f"sync_tiptap_to_cards: Section {idx} - '{section['question']}' - has {len(section['images'])} images")
        
        new_content = {
            "question": section["question"],
            "answer": md_answer,
            "images": section["images"],
            "title": section["question"] # fallback
        }

        
        if idx < len(existing_cards):
            # Update existing card
            card = existing_cards[idx]
            
            # Merge content
            existing_content = dict(card.content)
            existing_content.update(new_content)
            
            # Reassign dictionary for SQLAlchemy JSONB mutation detection
            card.content = existing_content
            db.add(card) # ensure it gets tracked
            logger.info(f"sync_tiptap_to_cards: Updated existing card {card.id}")
        else:
            # Insert new card (user added a new H2 section in the editor)

            new_card = Card(
                owner_id=user_id,
                source_material_id=source_material.id,
                type="reading_note",
                content=new_content,
                status=CardStatus.ACTIVE,
                batch_id=batch_id,
                batch_index=idx,
                tags=["reading_note", "editor_added"]
            )
            db.add(new_card)
            
    # If there are fewer sections than cards (user deleted sections)
    if len(sections) < len(existing_cards):
        for idx in range(len(sections), len(existing_cards)):
            card_to_archive = existing_cards[idx]
            if card_to_archive.status != CardStatus.ARCHIVED:
                card_to_archive.status = CardStatus.ARCHIVED
                db.add(card_to_archive)

def json_to_markdown(nodes: list) -> str:
    """Basic helper to turn Tiptap nodes back into a readable markdown string for NoteCards."""
    md = ""
    for node in nodes:
        node_type = node.get("type", "")
        if node_type == "paragraph":
            for child in node.get("content", []):
                md += _mark_text(child)
            md += "\n\n"
        elif node_type == "heading":
            level = node.get("attrs", {}).get("level", 1)
            md += f"{'#' * level} "
            for child in node.get("content", []):
                md += _mark_text(child)
            md += "\n\n"
        elif node_type == "bulletList":
            for item in node.get("content", []):
                md += "- "
                for p in item.get("content", []):
                    for child in p.get("content", []):
                        md += _mark_text(child)
                md += "\n"
            md += "\n"
        elif node_type == "orderedList":
            for i, item in enumerate(node.get("content", [])):
                md += f"{i+1}. "
                for p in item.get("content", []):
                    for child in p.get("content", []):
                        md += _mark_text(child)
                md += "\n"
            md += "\n"
        elif node_type == "blockquote":
            md += "> "
            for p in node.get("content", []):
                for child in p.get("content", []):
                    md += _mark_text(child)
            md += "\n\n"
        elif node_type == "math_display":
            for child in node.get("content", []):
                md += f"$${child.get('text', '')}$$\n\n"
        # Skipping tables for simple text sync, but they could be added
    return md.strip()

def _mark_text(child: dict) -> str:
    text = child.get("text", "")
    if not text and child.get("type") == "math_inline":
        sub = child.get("content", [])
        return f"${sub[0].get('text', '')}$" if sub else ""
        
    marks = child.get("marks", [])
    for mark in marks:
        if mark.get("type") == "bold":
            text = f"**{text}**"
        elif mark.get("type") == "italic":
            text = f"*{text}*"
        elif mark.get("type") == "code":
            text = f"`{text}`"
        elif mark.get("type") == "link":
            href = mark.get("attrs", {}).get("href", "")
            text = f"[{text}]({href})"
    return text
