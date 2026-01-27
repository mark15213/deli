# Celery Tasks
import asyncio
from uuid import UUID

from asgiref.sync import async_to_sync
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.services.ingestion_service import IngestionService
from app.services.generator_service import GeneratorService
from app.models import Source, OAuthConnection
from app.models import Card, CardStatus


@celery_app.task
def sync_notion_content(source_id: str):
    """
    Celery task to sync content based on a Source.
    Wraps async logic in sync task.
    """
    async_to_sync(run_sync_logic)(source_id)


async def run_sync_logic(source_id: str):
    """Async implementation of sync logic."""
    async with async_session_maker() as session:
        # 1. Get Source
        source = await session.get(Source, UUID(source_id))
        if not source:
            return

        # 2. Find Linked OAuthConnection
        # Simplistic assumption: User has 1 notion connection.
        stmt = select(OAuthConnection).where(
            OAuthConnection.user_id == source.user_id,
            OAuthConnection.provider == "notion"
        )
        result = await session.execute(stmt)
        connection = result.scalar_one_or_none()
        
        if not connection:
            # Need connection to sync
            return

        # 3. Run Ingestion
        ingestion = IngestionService(session)
        # Returns chunks with source_material metadata
        chunks = await ingestion.sync_source(source, connection)
        
        # 4. Process Chunks --> Generate Pending Cards
        generator = GeneratorService(session)
        
        for chunk in chunks:
            # Generate cards for each chunk
            # source_metadata needs to align with what GeneratorService expects
            
            source_meta = {
                "user_id": str(source.user_id),
                "source_material_id": chunk["source"]["source_material_id"],
                "chunk_index": chunk["source"]["chunk_index"]
            }
            
            await generator.generate_quizzes_from_chunk(chunk["text"], source_meta)
