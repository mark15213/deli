# Ingestion Service for syncing content from Notion
import logging
from datetime import datetime
from typing import List, Dict, Any
from uuid import UUID

from notion_client import AsyncClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import OAuthConnection, Source, SourceMaterial, User

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

    async def sync_source(self, source: Source, connection: OAuthConnection) -> List[Dict[str, Any]]:
        """
        Sync content based on a Source using the provided OAuth connection.
        Returns a list of processed chunks.
        """
        try:
            # 1. Initialize Notion Client
            token = connection.access_token
            notion = AsyncClient(auth=token)

            # 2. Fetch pages
            pages = await self._fetch_pages(notion, source)
            
            processed_chunks = []
            
            for page in pages:
                # 3. Check tags/status logic is handled in fetch or here
                # If source has filters, apply them.
                if not self._should_process_page(page, source):
                    continue
                
                # 4. Fetch page content
                page_id = page["id"]
                blocks = await self._fetch_page_content(notion, page_id)
                
                # 5. Extract text
                text_content = self._extract_text_from_blocks(blocks)
                
                if not text_content.strip():
                    continue
                
                # 5.5 Update/Create SourceMaterial
                source_mat = await self._get_or_create_source_material(
                    source, page_id, page, text_content
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
                            "user_id": str(source.user_id),
                            "synced_at": datetime.utcnow().isoformat()
                        }
                    })

            # Update last synced time
            source.last_synced_at = datetime.utcnow()
            await self.db.commit()
            
            return processed_chunks

        except Exception as e:
            logger.error(f"Error syncing source {source.id}: {str(e)}")
            raise e

    async def _get_or_create_source_material(self, source: Source, page_id: str, page_data: dict, content: str) -> SourceMaterial:
        """Track the source page in DB."""
        # Simple content hash
        import hashlib
        content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
        
        stmt = select(SourceMaterial).where(
            SourceMaterial.user_id == source.user_id,
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
            existing.source_id = source.id
            return existing
        else:
            new_source = SourceMaterial(
                user_id=source.user_id,
                source_id=source.id,
                external_id=page_id,
                external_url=url,
                title=title,
                content_hash=content_hash,
            )
            self.db.add(new_source)
            await self.db.flush() # get ID
            return new_source

    async def _fetch_pages(self, notion: AsyncClient, source: Source) -> List[dict]:
        """Fetch pages from Notion based on source."""
        
        # Check if source designates a specific database
        # e.g. connection_config = {"database_id": "xyz"}
        db_id = source.connection_config.get("database_id") if source.connection_config else None
        
        if source.type == "NOTION_KB" and db_id:
             return await self._query_database(notion, db_id, source.last_synced_at)
        
        # Fallback to search
        return await self._search_recent(notion, source.last_synced_at)

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

    def _should_process_page(self, page: dict, source: Source) -> bool:
        """Check if page matches filter config."""
        
        filters = source.ingestion_rules.get("filter", {}) if source.ingestion_rules else {}
        required_tags = filters.get("tags", [])
        
        # If ingestion_rules is just flat {"tags": ...} support that too
        if not required_tags and source.ingestion_rules:
             required_tags = source.ingestion_rules.get("tags", [])
        
        if not required_tags:
            # Default behavior
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

