# Ingestion Service for syncing content from Notion
import logging
from datetime import datetime
from typing import List, Dict, Any

from notion_client import AsyncClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NotionConnection, User
from app.core.security import decrypt_token

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for syncing and processing Notion content."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""],
        )

    async def sync_connection(self, connection: NotionConnection) -> List[Dict[str, Any]]:
        """
        Sync content from a Notion connection.
        Returns a list of processed chunks ready for quiz generation.
        """
        try:
            # 1. Initialize Notion Client
            token = decrypt_token(connection.access_token_encrypted)
            notion = AsyncClient(auth=token)

            # 2. Fetch pages to process
            # For MVP, we search for pages with specific criteria or use selected databases
            # Here we assume we fetch recent pages from selected databases if configured,
            # or just recently edited pages if no specific DB is selected.
            
            pages = await self._fetch_updated_pages(notion, connection)
            
            processed_chunks = []
            
            for page in pages:
                # 3. Check tags/status logic (PRD D-04)
                if not self._should_process_page(page):
                    continue
                
                # 4. Fetch page content (blocks)
                page_id = page["id"]
                blocks = await self._fetch_page_content(notion, page_id)
                
                # 5. Extract text from blocks
                text_content = self._extract_text_from_blocks(blocks)
                
                if not text_content.strip():
                    continue

                # 6. Chunk content
                chunks = self.text_splitter.split_text(text_content)
                
                # 7. Prepare metadata for each chunk
                for i, chunk in enumerate(chunks):
                    processed_chunks.append({
                        "text": chunk,
                        "source": {
                            "page_id": page_id,
                            "page_title": self._extract_title(page),
                            "chunk_index": i
                        },
                        "metadata": {
                            "user_id": str(connection.user_id),
                            "synced_at": datetime.utcnow().isoformat()
                        }
                    })

            # Update last synced time
            connection.last_synced_at = datetime.utcnow()
            await self.db.commit()
            
            return processed_chunks

        except Exception as e:
            logger.error(f"Error syncing connection {connection.id}: {str(e)}")
            raise e

    async def _fetch_updated_pages(self, notion: AsyncClient, connection: NotionConnection) -> List[dict]:
        """Fetch pages updated since last sync."""
        # Using search endpoint for simplicity in MVP to find recently edited pages
        # In production, Query Database endpoint per selected DB is better
        
        query = {
            "filter": {
                "property": "object",
                "value": "page"
            },
            "sort": {
                "direction": "descending",
                "timestamp": "last_edited_time"
            }
        }
        
        # If we have a last_synced_at, we could ideally filter by it, 
        # but Notion Search API doesn't support generic > timestamp filter effectively 
        # without iterating. We'll fetch top 100 and filter in memory for MVP.
        
        response = await notion.search(**query)
        results = response.get("results", [])
        
        if connection.last_synced_at:
            # Filter by last_edited_time > last_synced_at
            filtered = []
            for page in results:
                last_edited = datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00"))
                # basic comparison (ignoring tz strictness for MVP snippet)
                if last_edited.replace(tzinfo=None) > connection.last_synced_at.replace(tzinfo=None):
                    filtered.append(page)
            return filtered
            
        return results

    def _should_process_page(self, page: dict) -> bool:
        """
        Check if page meets criteria (e.g. has #MakeQuiz tag).
        Notion properties are dynamic, checking generic keys.
        """
        # MVP: Look for a "Tags" or "Status" property
        props = page.get("properties", {})
        
        for key, prop in props.items():
            # Check Multi-select tags
            if prop["type"] == "multi_select":
                for option in prop["multi_select"]:
                    if option["name"].lower() == "makequiz":
                        return True
                        
            # Check Checkbox
            if prop["type"] == "checkbox" and prop["checkbox"]:
                if key.lower() == "make quiz":
                    return True
        
        # If no specific tag found, for MVP debug/demo we might allow all 
        # or require at least one specific tag. Let's strictly require #MakeQuiz for now as per PRD.
        
        # NOTE: For development friendliness, if no requirements are strictly set in connection,
        # maybe return True? PRD says "D-04 Tag Trigger: Only when...".
        # Let's enforce it to reduce noise.
        return False

    async def _fetch_page_content(self, notion: AsyncClient, page_id: str) -> List[dict]:
        """Fetch all blocks of a page (non-recursive for MVP)."""
        blocks = []
        has_more = True
        start_cursor = None
        
        while has_more:
            response = await notion.blocks.children.list(
                block_id=page_id,
                start_cursor=start_cursor
            )
            blocks.extend(response.get("results", []))
            has_more = response.get("has_more", False)
            start_cursor = response.get("next_cursor")
            
        return blocks

    def _extract_text_from_blocks(self, blocks: List[dict]) -> str:
        """Extract plain text from Notion blocks."""
        text_parts = []
        
        for block in blocks:
            b_type = block.get("type")
            if not b_type or b_type not in block:
                continue
            
            content = block[b_type]
            rich_text = content.get("rich_text", [])
            
            # Simple text extraction
            plain_text = "".join([t.get("plain_text", "") for t in rich_text])
            
            if plain_text:
                text_parts.append(plain_text)
                
            # Handle specific block types (like code, headers)
            # Code blocks are implicitly handled by rich_text usually but 'caption' might exist
            
        return "\n\n".join(text_parts)

    def _extract_title(self, page: dict) -> str:
        """Extract page title."""
        props = page.get("properties", {})
        for prop in props.values():
            if prop["type"] == "title":
                return "".join([t.get("plain_text", "") for t in prop["title"]])
        return "Untitled"
