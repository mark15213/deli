# Tests for database connection and migrations
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Quiz, NotionConnection, ReviewRecord, QuizType, QuizStatus


class TestDatabaseConnection:
    """Tests for database connection."""

    @pytest.mark.asyncio
    async def test_db_connection(self, db_session: AsyncSession):
        """Test that database connection works."""
        result = await db_session.execute(text("SELECT 1"))
        assert result.scalar() == 1


class TestModelCRUD:
    """Tests for basic CRUD operations on models."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        """Test creating a user."""
        import uuid
        
        user = User(
            id=uuid.uuid4(),
            email="crud_test@example.com",
            preferences={"theme": "dark"},
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "crud_test@example.com"
        assert user.preferences == {"theme": "dark"}
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_create_notion_connection(self, db_session: AsyncSession, test_user: User):
        """Test creating a Notion connection."""
        import uuid
        
        connection = NotionConnection(
            id=uuid.uuid4(),
            user_id=test_user.id,
            access_token_encrypted="encrypted_token_here",
            workspace_id="ws_123",
            workspace_name="Test Workspace",
            selected_databases={"db1": True},
        )
        db_session.add(connection)
        await db_session.commit()
        await db_session.refresh(connection)
        
        assert connection.id is not None
        assert connection.user_id == test_user.id
        assert connection.workspace_name == "Test Workspace"

    @pytest.mark.asyncio
    async def test_create_quiz(self, db_session: AsyncSession, test_user: User):
        """Test creating a quiz."""
        import uuid
        
        quiz = Quiz(
            id=uuid.uuid4(),
            user_id=test_user.id,
            type=QuizType.MCQ,
            question="What is Python?",
            options=["A. A snake", "B. A language", "C. A framework", "D. A database"],
            answer="B",
            explanation="Python is a programming language.",
            tags=["python", "basics"],
            status=QuizStatus.PENDING,
        )
        db_session.add(quiz)
        await db_session.commit()
        await db_session.refresh(quiz)
        
        assert quiz.id is not None
        assert quiz.type == QuizType.MCQ
        assert quiz.status == QuizStatus.PENDING

    @pytest.mark.asyncio
    async def test_create_review_record(self, db_session: AsyncSession, test_user: User):
        """Test creating a review record."""
        import uuid
        from datetime import datetime, timedelta
        
        # First create a quiz
        quiz = Quiz(
            id=uuid.uuid4(),
            user_id=test_user.id,
            type=QuizType.FLASHCARD,
            question="What is FastAPI?",
            answer="A web framework for building APIs with Python.",
            status=QuizStatus.APPROVED,
        )
        db_session.add(quiz)
        await db_session.commit()
        
        # Create review record
        review = ReviewRecord(
            id=uuid.uuid4(),
            quiz_id=quiz.id,
            user_id=test_user.id,
            rating=3,  # Good
            fsrs_state={"stability": 1.0, "difficulty": 5.0},
            next_review_at=datetime.utcnow() + timedelta(days=1),
        )
        db_session.add(review)
        await db_session.commit()
        await db_session.refresh(review)
        
        assert review.id is not None
        assert review.rating == 3
        assert review.fsrs_state["stability"] == 1.0

    @pytest.mark.asyncio
    async def test_user_cascade_delete(self, db_session: AsyncSession):
        """Test that deleting a user cascades to related records."""
        import uuid
        from datetime import datetime, timedelta
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="cascade_test@example.com",
        )
        db_session.add(user)
        await db_session.commit()
        
        # Create quiz for user
        quiz = Quiz(
            id=uuid.uuid4(),
            user_id=user.id,
            type=QuizType.MCQ,
            question="Test question",
            answer="Test answer",
        )
        db_session.add(quiz)
        await db_session.commit()
        
        # Delete user
        await db_session.delete(user)
        await db_session.commit()
        
        # Verify quiz is also deleted (cascade)
        from sqlalchemy import select
        result = await db_session.execute(select(Quiz).where(Quiz.id == quiz.id))
        assert result.scalar_one_or_none() is None
