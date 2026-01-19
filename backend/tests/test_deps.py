# Tests for Authentication Middleware
from uuid import uuid4
import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.models import User
from app.core.security import create_access_token


@pytest.fixture
def app_with_auth_check():
    """Create a temporary app to test dependency injection."""
    app = FastAPI()
    
    @app.get("/protected")
    async def protected_route(user: User = Depends(get_current_user)):
        return {"id": str(user.id), "email": user.email}
        
    return app


@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_session: AsyncSession, test_user: User):
    """Test standard valid token flow."""
    # Create valid token
    token = create_access_token(subject=str(test_user.id))
    
    # Mock dependency execution context? 
    # Actually, simpler to test via API call structure or direct function call
    # But direct function call requires mocking Depends logic which is hard.
    # We will use the app fixture approach with TestClient but we need overrides.
    pass


# We can test the dependency function directly by mocking verify_token and DB
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_get_current_user_direct(db_session: AsyncSession, test_user: User):
    """Test get_current_user logic directly."""
    token = create_access_token(subject=str(test_user.id))
    
    # Run dependency
    user = await get_current_user(token=token, db=db_session)
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(db_session: AsyncSession):
    from fastapi import HTTPException
    
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token="invalid_token", db=db_session)
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    # TODO: Create expired token and verify
    pass


@pytest.mark.asyncio
async def test_protected_routes_require_auth(client):
    """Test that actual API endpoints require authentication."""
    # Quizzes
    response = await client.get("/api/v1/quizzes/today")
    assert response.status_code == 401
    
    # Inbox
    response = await client.get("/api/v1/inbox/pending")
    assert response.status_code == 401
    
    # Stats
    response = await client.get("/api/v1/stats/dashboard")
    assert response.status_code == 401
