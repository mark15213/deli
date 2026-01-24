# Ingestion Service for syncing content from Notion
import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from notion_client import AsyncClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import OAuthConnection, SyncConfig, SourceMaterial, User
# from app.core.security import decrypt_token # We decided to store plain token for now

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

    async def sync_config(self, config: SyncConfig, connection: OAuthConnection) -> List[Dict[str, Any]]:
        """
        Sync content based on a SyncConfig using the provided OAuth connection.
        Returns a list of processed chunks.
        """
        try:
            # 1. Initialize Notion Client
            # token = decrypt_token(connection.access_token)
            token = connection.access_token
            notion = AsyncClient(auth=token)

            # 2. Fetch pages
            pages = await self._fetch_pages(notion, config)
            
            processed_chunks = []
            
            for page in pages:
                # 3. Check tags/status logic is handled in fetch or here
                # If config has filters, apply them.
                if not self._should_process_page(page, config):
                    continue
                
                # 4. Fetch page content
                page_id = page["id"]
                blocks = await self._fetch_page_content(notion, page_id)
                
                # 5. Extract text
                text_content = self._extract_text_from_blocks(blocks)
                
                if not text_content.strip():
                    continue
                
                # 5.5 Update/Create SourceMaterial
                # Check hash to see if changed (Implement hash later, or just overwrite for now)
                
                source_mat = await self._get_or_create_source_material(
                    config, page_id, page, text_content
                )

                # 6. Chunk content
                chunks = self.text_splitter.split_text(text_content)
                
                # 7. Prepare metadata
                for i, chunk in enumerate(chunks):
                    processed_chunks.append({
                        "text": chunk,
                        "source": {
                            "page_id": page_id,
                            "page_title": self._extract_title(page),
                            "source_material_id": str(source_mat.id),
                            "chunk_index": i
                        },
                        "metadata": {
                            "user_id": str(config.user_id),
                            "synced_at": datetime.utcnow().isoformat()
                        }
                    })

            # Update last synced time
            config.last_synced_at = datetime.utcnow()
            await self.db.commit()
            
            return processed_chunks

        except Exception as e:
            logger.error(f"Error syncing config {config.id}: {str(e)}")
            raise e

    async def _get_or_create_source_material(self, config: SyncConfig, page_id: str, page_data: dict, content: str) -> SourceMaterial:
        """Track the source page in DB."""
        # Simple content hash
        import hashlib
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        stmt = select(SourceMaterial).where(
            SourceMaterial.user_id == config.user_id,
            SourceMaterial.external_id == page_id
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        title = self._extract_title(page_data)
        url = page_data.get("url")
        
        if existing:
            existing.content_hash = content_hash
            existing.title = title
            existing.external_url = url
            # existing.raw_snippet = content[:200]
            existing.config_id = config.id
            return existing
        else:
            new_source = SourceMaterial(
                user_id=config.user_id,
                config_id=config.id,
                external_id=page_id,
                external_url=url,
                title=title,
                content_hash=content_hash,
                # raw_snippet=content[:200]
            )
            self.db.add(new_source)
            await self.db.flush() # get ID
            return new_source

    async def _fetch_pages(self, notion: AsyncClient, config: SyncConfig) -> List[dict]:
        """Fetch pages from Notion based on config."""
        # If config designates a specific database, query it.
        # Else search.
        
        # For now, simplistic implementation:
        # Use Search if external_id is not set or logic implies 'all'
        # But SyncConfig has `source_type` and `external_id`.
        
        if config.source_type == "notion_database" and config.external_id:
             return await self._query_database(notion, config.external_id, config.last_synced_at)
        
        # Fallback to search (e.g. if source_type='workspace')
        return await self._search_recent(notion, config.last_synced_at)

    async def _query_database(self, notion: AsyncClient, db_id: str, last_synced: datetime) -> List[dict]:
        query = {
            "database_id": db_id,
            "sorts": [
                {
                    "timestamp": "last_edited_time",
                    "direction": "descending"
                }
            ]
        }
        # Filter by time if possible
        if last_synced:
            query["filter"] = {
                "timestamp": "last_edited_time",
                "last_edited_time": {
                    "after": last_synced.isoformat()
                }
            }
            
        response = await notion.databases.query(**query)
        return response.get("results", [])

    async def _search_recent(self, notion: AsyncClient, last_synced: datetime) -> List[dict]:
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
        
        response = await notion.search(**query)
        results = response.get("results", [])
        
        if last_synced:
             filtered = []
             for page in results:
                last_edited_str = page.get("last_edited_time")
                if last_edited_str:
                    try:
                        last_edited = datetime.fromisoformat(last_edited_str.replace("Z", "+00:00"))
                        if last_edited.replace(tzinfo=None) > last_synced.replace(tzinfo=None):
                            filtered.append(page)
                    except:
                        pass
             return filtered
        return results

    def _should_process_page(self, page: dict, config: SyncConfig) -> bool:
        """Check if page matches filter config."""
        # Check explicit filters in SyncConfig
        # e.g. {"tags": ["MakeQuiz"]}
        
        filters = config.filter_config or {}
        required_tags = filters.get("tags", [])
        
        if not required_tags:
            # Default behavior if no filters: maybe require #MakeQuiz?
            # Or assume explicit selection implies processing.
            # Let's default to check for "MakeQuiz" if nothing specified to prevent spam, 
            # unless it's a specific DB sync where we might want everything.
            # Per PRD: "Only when a page is tagged with #MakeQuiz"
            required_tags = ["MakeQuiz"]
            
        props = page.get("properties", {})
        
        found_match = False
        
        for key, prop in props.items():
            if prop["type"] == "multi_select":
                for option in prop["multi_select"]:
                    if option["name"] in required_tags: # Case sensitive?
                        found_match = True
            elif prop["type"] == "checkbox":
                 if prop["checkbox"] and key in required_tags:
                     found_match = True
                     
        return found_match

    async def _fetch_page_content(self, notion: AsyncClient, page_id: str) -> List[dict]:
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
        text_parts = []
        for block in blocks:
            b_type = block.get("type")
            if not b_type or b_type not in block:
                continue
            content = block[b_type]
            rich_text = content.get("rich_text", [])
            plain_text = "".join([t.get("plain_text", "") for t in rich_text])
            if plain_text:
                text_parts.append(plain_text)
        return "\n\n".join(text_parts)

    def _extract_title(self, page: dict) -> str:
        props = page.get("properties", {})
        for prop in props.values():
            if prop["type"] == "title":
                return "".join([t.get("plain_text", "") for t in prop["title"]])
        return "Untitled"
