# Tests for Notion Sync Worker
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.workers.tasks import run_sync_logic
from app.services.ingestion_service import IngestionService
from app.models import NotionConnection, User



# Context manager to mock async_session_maker()
class MockSessionManager:
    def __init__(self, session):
        self.session = session
    async def __aenter__(self):
        return self.session
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.mark.asyncio
async def test_ingestion_service_logic(db_session):
    """Test IngestionService core logic with mocks."""

    # Mock Notion Client
    mock_notion = AsyncMock()
    mock_notion.search.return_value = {
        "results": [
            {
                "object": "page",
                "id": "page_1",
                "last_edited_time": "2023-01-01T12:00:00Z",
                "properties": {
                    "Name": {
                        "type": "title",
                        "title": [{"plain_text": "Test Page"}]
                    },
                    "Tags": {
                        "type": "multi_select",
                        "multi_select": [{"name": "MakeQuiz"}]
                    }
                }
            }
        ]
    }
    
    mock_notion.blocks.children.list.return_value = {
        "results": [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"plain_text": "Content for quiz generation."}]
                }
            }
        ],
        "has_more": False
    }

    # Create dummy connection
    user = User(id=uuid4(), email="test@example.com", preferences={})
    db_session.add(user)
    await db_session.flush()
    
    connection = NotionConnection(
        id=uuid4(),
        user_id=user.id,
        access_token_encrypted="encrypted_token",
        workspace_id="ws_1",
        workspace_name="Test WS"
    )
    db_session.add(connection)
    await db_session.commit()

    # Run Ingestion Service
    service = IngestionService(db_session)
    
    # Patch external calls
    with patch("app.services.ingestion_service.AsyncClient", return_value=mock_notion), \
         patch("app.services.ingestion_service.decrypt_token", return_value="secret"):
        
        chunks = await service.sync_connection(connection)
        
        # Verify results
        assert len(chunks) == 1
        assert chunks[0]["text"] == "Content for quiz generation."
        assert chunks[0]["source"]["page_id"] == "page_1"
        assert chunks[0]["source"]["page_title"] == "Test Page"


@pytest.mark.asyncio
async def test_sync_task_integration(db_session):
    """Test the full sync task flow (mocking Celery execution context)."""
    
    # Create dummy connection
    user_id = uuid4()
    user = User(id=user_id, email="sync_test@example.com", preferences={})
    db_session.add(user)
    await db_session.flush()
    
    conn_id = uuid4()
    connection = NotionConnection(
        id=conn_id,
        user_id=user_id,
        access_token_encrypted="enc_token",
        workspace_id="ws_2",
    )
    db_session.add(connection)
    await db_session.commit()
    
    # Mock IngestionService.sync_connection to return dummy chunks
    mock_chunks = [{
        "text": "Chunk 1",
        "source": {"page_id": "p1", "page_title": "P1", "chunk_index": 0},
        "metadata": {}
    }]
    
    with patch("app.workers.tasks.IngestionService") as MockIngestion:
        instance = MockIngestion.return_value
        instance.sync_connection = AsyncMock(return_value=mock_chunks)
        
        # Patch async_session_maker to return our test session
        with patch("app.workers.tasks.async_session_maker") as mock_maker:
            mock_maker.return_value = MockSessionManager(db_session)
            
            # Invoke logic directly (bypassing Celery broker)
            await run_sync_logic(str(conn_id))
        
        # Verify Query created
        from sqlalchemy import select
        from app.models import Quiz
        
        stmt = select(Quiz).where(Quiz.user_id == user_id)
        result = await db_session.execute(stmt)
        quizzes = result.scalars().all()
        
        assert len(quizzes) == 1
        assert quizzes[0].source_page_title == "P1"
        assert quizzes[0].question.startswith("Placeholder Question")
