# API routes for authentication
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
import httpx

from app.core.config import get_settings
from app.core.security import create_access_token, encrypt_token

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/notion/login")
async def notion_login():
    """Redirect to Notion OAuth page."""
    auth_url = (
        f"https://api.notion.com/v1/oauth/authorize"
        f"?client_id={settings.notion_client_id}"
        f"&response_type=code"
        f"&owner=user"
        f"&redirect_uri={settings.notion_redirect_uri}"
    )
    return RedirectResponse(url=auth_url)


@router.get("/notion/callback")
async def notion_callback(
    code: str = Query(..., description="Authorization code from Notion"),
    state: str = Query(None),
):
    """Handle Notion OAuth callback."""
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/oauth/token",
            auth=(settings.notion_client_id, settings.notion_client_secret),
            json={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.notion_redirect_uri,
            },
        )
    
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_data = response.json()
    access_token = token_data.get("access_token")
    workspace_id = token_data.get("workspace_id")
    
    # TODO: 
    # 1. Create or update user in database
    # 2. Store encrypted Notion token
    # 3. Return JWT token to client
    
    # For now, return a placeholder response
    jwt_token = create_access_token(subject="user_id_placeholder")
    
    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "workspace_id": workspace_id,
    }


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired JWT token."""
    # TODO: Implement token refresh logic
    raise HTTPException(status_code=501, detail="Not implemented")
