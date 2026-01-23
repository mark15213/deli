# Pytest configuration and fixtures
import sys
from unittest.mock import MagicMock

# MOCK FSRS LIBRARY GLOBALLY (Since user skipped installation)
mock_fsrs = MagicMock()
mock_fsrs.FSRS = MagicMock
mock_fsrs.Card = MagicMock

# Mock Rating Enum
rating_mock = MagicMock()
rating_mock.Again = 1
rating_mock.Hard = 2
rating_mock.Good = 3
rating_mock.Easy = 4
# Make Rating(x) return the mock value itself to simulate Enum behavior sort of
# Actually, the service does Rating(rating).
# If Rating is Enum, Rating(3) -> Rating.Good.
# We need to mock the CALL to the Rating class.
def rating_side_effect(val):
    if val == 1: return rating_mock.Again
    if val == 2: return rating_mock.Hard
    if val == 3: return rating_mock.Good
    if val == 4: return rating_mock.Easy
    return val
rating_mock.side_effect = rating_side_effect
mock_fsrs.Rating = rating_mock

# Mock State Enum
state_mock = MagicMock()
state_mock.New = 0
state_mock.Learning = 1
state_mock.Review = 2
state_mock.Relearning = 3
mock_fsrs.State = state_mock

sys.modules["fsrs"] = mock_fsrs

import asyncio
from typing import AsyncGenerator, Generator
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.config import get_settings
from app.core.security import create_access_token
from app.models import User, NotionConnection, Quiz, ReviewRecord


# Test database URL (use separate test database)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/deli_test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional database session for tests."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client."""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        preferences={},
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Provide authenticated headers with JWT token."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def authenticated_client(
    client: AsyncClient,
    auth_headers: dict,
) -> AsyncClient:
    """Provide an authenticated async HTTP test client."""
    client.headers.update(auth_headers)
    return client
