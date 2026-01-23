# Celery Tasks
import asyncio
from uuid import UUID

from asgiref.sync import async_to_sync

from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.services.ingestion_service import IngestionService
from app.services.generator_service import GeneratorService
from app.models import NotionConnection
from app.models import Quiz, QuizStatus, QuizType


@celery_app.task
def sync_notion_content(connection_id: str):
    """
    Celery task to sync content from a specific Notion connection.
    Wraps async logic in sync task.
    """
    async_to_sync(run_sync_logic)(connection_id)


async def run_sync_logic(connection_id: str):
    """Async implementation of sync logic."""
    async with async_session_maker() as session:
        # 1. Get Connection
        connection = await session.get(NotionConnection, UUID(connection_id))
        if not connection:
            return

        # 2. Run Ingestion
        ingestion = IngestionService(session)
        chunks = await ingestion.sync_connection(connection)
        
        # 3. Process Chunks --> Generate Pending Quizzes
        generator = GeneratorService(session)
        
        for chunk in chunks:
            # Generate quizzes for each chunk (F1.5 core)
            # Metadata: user_id, page_id, page_title already in chunk source/metadata
            
            source_meta = {
                "user_id": str(connection.user_id),
                "page_id": chunk["source"]["page_id"],
                "page_title": chunk["source"]["page_title"]
            }
            
            await generator.generate_quizzes_from_chunk(chunk["text"], source_meta)
        
        # Note: GeneratorService commits internally, but session management here ensures cleanliness.
        # Ideally we commit once per task or chunk. GeneratorService does commit.
