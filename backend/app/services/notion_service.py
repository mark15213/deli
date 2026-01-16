# Notion API Service
from typing import Optional
import httpx
from fastapi import HTTPException

from app.core.config import get_settings

settings = get_settings()


class NotionService:
    """Service for interacting with Notion API."""
    
    BASE_URL = "https://api.notion.com/v1"
    
    @staticmethod
    def get_auth_url(state: str = None) -> str:
        """Generate Notion OAuth authorization URL."""
        base = "https://api.notion.com/v1/oauth/authorize"
        params = f"?client_id={settings.notion_client_id}&response_type=code&owner=user&redirect_uri={settings.notion_redirect_uri}"
        if state:
            params += f"&state={state}"
        return base + params

    @staticmethod
    async def exchange_code_for_token(code: str) -> dict:
        """Exchange authorization code for access token."""
        auth = (settings.notion_client_id, settings.notion_client_secret)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{NotionService.BASE_URL}/oauth/token",
                    auth=auth,
                    json={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": settings.notion_redirect_uri,
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get("error", "Unknown error")
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Notion OAuth failed: {error_detail}"
                    )
                
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Network error connecting to Notion: {str(e)}"
                )
