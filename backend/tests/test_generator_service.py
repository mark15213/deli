# Tests for Generator Service
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.generator_service import GeneratorService, QuizList, QuizOutput
from app.models import Card, SourceMaterial, SyncConfig

@pytest.fixture
def mock_quiz_list():
    return QuizList(quizzes=[
        QuizOutput(
            question="What is Python?",
            options=["A snake", "A language", "A coffee"],
            answer="A language",
            explanation="It is a programming language.",
            difficulty="Easy",
            tags=["Python", "Basics"]
        )
    ])

@pytest.mark.asyncio
async def test_generate_quizzes_from_chunk(db_session, mock_quiz_list):
    """Test generating quizzes from a text chunk."""
    
    # Create a user first to satisfy ForeignKey
    from app.models import User
    user_id = uuid4()
    user = User(id=user_id, email="test_gen@example.com", settings={})
    db_session.add(user)
    
    # Create a source material and config
    config = SyncConfig(id=uuid4(), user_id=user_id, source_type="notion_database", external_id="db_1")
    db_session.add(config)
    source = SourceMaterial(id=uuid4(), user_id=user_id, config_id=config.id, external_id="p_1")
    db_session.add(source)
    
    await db_session.commit()
    
    # Mock LLM Client
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_quiz_list)
    
    service = GeneratorService(db_session)
    service.client = mock_client
    
    source_meta = {
        "user_id": str(user_id),
        "source_material_id": str(source.id),
        "chunk_index": 0
    }
    
    cards = await service.generate_quizzes_from_chunk("Some text content", source_meta)
    
    assert len(cards) == 1
    assert cards[0].content["question"] == "What is Python?"
    assert cards[0].content["answer"] == "A language"
    # assert cards[0].source_page_title == "Test Page" # Not stored on card anymore directly
    
    # Verify DB persistence
    from sqlalchemy import select
    # JSONB query in SQLAlchemy
    # stmt = select(Card).where(Card.content['question'].astext == "What is Python?")
    # Simple workaround for test
    stmt = select(Card).where(Card.id == cards[0].id)
    result = await db_session.execute(stmt)
    db_card = result.scalar_one()
    assert db_card.deck_id is not None
    assert db_card.content["question"] == "What is Python?"

@pytest.mark.asyncio
async def test_llm_failure_handling(db_session):
    """Test graceful handling of LLM errors."""
    
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI Limit"))
    
    service = GeneratorService(db_session)
    service.client = mock_client
    
    # Needs valid source_mat_id to not crash before LLM call? 
    # The service calls LLM first, so invalid ID might not matter until DB save.
    # But UUID parsing happens early.
    
    source_meta = {
        "user_id": str(uuid4()), 
        "source_material_id": str(uuid4()),
        "chunk_index": 0
    }
    cards = await service.generate_quizzes_from_chunk("Text", source_meta)
    
    assert len(cards) == 0
