# Tests for Auth Services
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notion_service import NotionService
from app.services.auth_service import AuthService
from app.models import User, NotionConnection


class TestNotionService:
    @pytest.mark.asyncio
    async def test_get_auth_url(self):
        url = NotionService.get_auth_url(state="test_state")
        assert "api.notion.com" in url
        assert "response_type=code" in url
        assert "state=test_state" in url

    @pytest.mark.asyncio
    async def test_exchange_code_success(self):
        mock_response = {
            "access_token": "test_token",
            "workspace_id": "ws_123",
            "workspace_name": "Test WS",
            "bot_id": "bot_123"
        }
        
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.json.return_value = mock_response
            mock_post.return_value = mock_response_obj
            
            result = await NotionService.exchange_code_for_token("valid_code")
            assert result == mock_response

    @pytest.mark.asyncio
    async def test_exchange_code_failure(self):
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 400
            mock_response_obj.json.return_value = {"error": "invalid_grant"}
            mock_post.return_value = mock_response_obj
            
            with pytest.raises(HTTPException) as exc:
                await NotionService.exchange_code_for_token("invalid_code")
            assert exc.value.status_code == 400


class TestAuthService:
    @pytest.mark.asyncio
    async def test_authenticate_new_user(self, db_session: AsyncSession):
        mock_token_data = {
            "access_token": "secret_token",
            "workspace_id": "ws_new",
            "workspace_name": "New WS",
            "owner": {"user": {"email": "new_user@example.com"}}
        }
        
        with patch.object(NotionService, "exchange_code_for_token", return_value=mock_token_data):
            user = await AuthService.authenticate_notion_user(db_session, "fake_code")
            
            assert user.email == "new_user@example.com"
            assert user.notion_connections[0].workspace_name == "New WS"
            
            # Verify encryption (should not be plain text)
            assert user.notion_connections[0].access_token_encrypted != "secret_token"
            
            # Verify DB persistence
            from sqlalchemy import select
            stmt = select(User).where(User.email == "new_user@example.com")
            result = await db_session.execute(stmt)
            db_user = result.scalar_one()
            assert db_user.id == user.id

    @pytest.mark.asyncio
    async def test_authenticate_existing_user(self, db_session: AsyncSession, test_user: User):
        mock_token_data = {
            "access_token": "updated_token",
            "workspace_id": "ws_123",
            "workspace_name": "Updated WS",
            "owner": {"user": {"email": "test@example.com"}}
        }
        
        with patch.object(NotionService, "exchange_code_for_token", return_value=mock_token_data):
            user = await AuthService.authenticate_notion_user(db_session, "fake_code")
            
            assert user.id == test_user.id
            assert user.email == "test@example.com"
            
            # Verify connection updated
            conn = user.notion_connections[0]
            assert conn.workspace_name == "Updated WS"
