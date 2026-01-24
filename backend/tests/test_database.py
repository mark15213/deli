# Tests for database connection and migrations
import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Card, OAuthConnection, ReviewLog, CardStatus, Deck


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
            settings={"theme": "dark"},
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "crud_test@example.com"
        assert user.settings == {"theme": "dark"}
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_create_oauth_connection(self, db_session: AsyncSession, test_user: User):
        """Test creating an OAuth connection."""
        import uuid
        
        connection = OAuthConnection(
            id=uuid.uuid4(),
            user_id=test_user.id,
            provider="notion",
            provider_user_id="ws_123",
            access_token="token_here"
        )
        db_session.add(connection)
        await db_session.commit()
        await db_session.refresh(connection)
        
        assert connection.id is not None
        assert connection.user_id == test_user.id
        assert connection.provider == "notion"

    @pytest.mark.asyncio
    async def test_create_card(self, db_session: AsyncSession, test_user: User):
        """Test creating a card."""
        import uuid
        
        # Need a Deck first
        deck = Deck(id=uuid.uuid4(), owner_id=test_user.id, title="Test Deck")
        db_session.add(deck)
        await db_session.commit()
        
        card = Card(
            id=uuid.uuid4(),
            deck_id=deck.id,
            type="mcq",
            content={"question": "Q", "answer": "A"},
            status=CardStatus.PENDING,
            tags=["demo"]
        )
        db_session.add(card)
        await db_session.commit()
        await db_session.refresh(card)
        
        assert card.id is not None
        assert card.type == "mcq"
        assert card.status == CardStatus.PENDING
        assert card.tags == ["demo"]

    @pytest.mark.asyncio
    async def test_create_review_log(self, db_session: AsyncSession, test_user: User):
        """Test creating a review record."""
        import uuid
        from datetime import datetime, timedelta
        
        # Create deck and card
        deck = Deck(id=uuid.uuid4(), owner_id=test_user.id, title="Test Deck")
        db_session.add(deck)
        card = Card(
            id=uuid.uuid4(),
            deck_id=deck.id,
            type="flashcard",
            content={"question": "Q"},
            status=CardStatus.ACTIVE,
        )
        db_session.add(card)
        await db_session.commit()
        
        # Create review log
        log = ReviewLog(
            id=uuid.uuid4(),
            card_id=card.id,
            user_id=test_user.id,
            grade=3,  # Good
            state_before="new",
            stability_before=0.0,
            reviewed_at=datetime.utcnow()
        )
        db_session.add(log)
        await db_session.commit()
        await db_session.refresh(log)
        
        assert log.id is not None
        assert log.grade == 3
        # Enum check might return enum member
        assert log.state_before.value == "new" or log.state_before == "new"

    @pytest.mark.asyncio
    async def test_user_cascade_delete(self, db_session: AsyncSession):
        """Test that deleting a user cascades to related records."""
        import uuid
        
        # Create user
        user = User(
            id=uuid.uuid4(),
            email="cascade_test@example.com",
        )
        db_session.add(user)
        # Create deck
        deck = Deck(id=uuid.uuid4(), owner_id=user.id, title="Test Deck")
        db_session.add(deck)
        await db_session.commit()
        
        deck_id = deck.id
        
        # Delete user
        await db_session.delete(user)
        await db_session.commit()
        
        # Verify deck is also deleted (cascade)
        from sqlalchemy import select
        result = await db_session.execute(select(Deck).where(Deck.id == deck_id))
        assert result.scalar_one_or_none() is None
