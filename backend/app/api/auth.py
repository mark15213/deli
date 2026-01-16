from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.services.notion_service import NotionService

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/notion/login")
async def notion_login():
    """Redirect to Notion OAuth page."""
    auth_url = NotionService.get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/notion/callback")
async def notion_callback(
    code: str = Query(..., description="Authorization code from Notion"),
    db: AsyncSession = Depends(get_db),
):
    """Handle Notion OAuth callback."""
    # Authenticate via Notion and get/create User
    user = await AuthService.authenticate_notion_user(db, code)
    
    # Create JWT Access Token
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "email": user.email,
    }


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired JWT token."""
    # TODO: Implement token refresh logic
    raise HTTPException(status_code=501, detail="Not implemented")
