# Tests for Generator Service
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.generator_service import GeneratorService, QuizList, QuizOutput
from app.models import Quiz, QuizType

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
    user = User(id=user_id, email="test_gen@example.com", preferences={})
    db_session.add(user)
    await db_session.commit()
    
    # Mock LLM Client
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_quiz_list)
    
    service = GeneratorService(db_session)
    service.client = mock_client
    
    source_meta = {
        "user_id": str(user_id),
        "page_id": "page_123",
        "page_title": "Test Page"
    }
    
    quizzes = await service.generate_quizzes_from_chunk("Some text content", source_meta)
    
    assert len(quizzes) == 1
    assert quizzes[0].question == "What is Python?"
    assert quizzes[0].answer == "A language"
    assert quizzes[0].source_page_title == "Test Page"
    
    # Verify DB persistence
    from sqlalchemy import select
    stmt = select(Quiz).where(Quiz.question == "What is Python?")
    result = await db_session.execute(stmt)
    db_quiz = result.scalar_one()
    assert db_quiz.id == quizzes[0].id

@pytest.mark.asyncio
async def test_llm_failure_handling(db_session):
    """Test graceful handling of LLM errors."""
    
    mock_client = MagicMock()
    mock_client.chat.completions.create = AsyncMock(side_effect=Exception("OpenAI Limit"))
    
    service = GeneratorService(db_session)
    service.client = mock_client
    
    source_meta = {"user_id": str(uuid4())}
    quizzes = await service.generate_quizzes_from_chunk("Text", source_meta)
    
    assert len(quizzes) == 0
