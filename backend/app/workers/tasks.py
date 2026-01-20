# Celery Tasks
import asyncio
from uuid import UUID

from asgiref.sync import async_to_sync

from app.core.celery_app import celery_app
from app.core.database import async_session_maker
from app.services.ingestion_service import IngestionService
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
        
        # 3. Process Chunks --> Generate Pending Quizzes (Placeholder for F1.5)
        # For now, we just log or create a placeholder quiz for testing
        print(f"Synced {len(chunks)} chunks from connection {connection_id}")
        
        for chunk in chunks:
            # Placeholder: Create a dummy quiz to verify flow
            # Real implementation in F1.5 will call LLM here
            quiz = Quiz(
                user_id=connection.user_id,
                type=QuizType.MCQ,
                question=f"Placeholder Question for: {chunk['source']['page_title']}",
                options=["A", "B", "C"],
                answer="A",
                explanation=f"Generated from chunk index {chunk['source']['chunk_index']}",
                status=QuizStatus.PENDING,
                source_page_id=chunk['source']['page_id'],
                source_page_title=chunk['source']['page_title'],
            )
            session.add(quiz)
        
        await session.commit()
