from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.services.auth_service import AuthService
from app.services.notion_service import NotionService
from app.models import SyncConfig, OAuthConnection

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
    
    # Check/Create Default Sync Config
    # Check if we have a sync config for this user's notion connection
    # Since OAuthConnection is established, we can default a SyncConfig to import from the workspace
    # or just leave it empty.
    # To facilitate "Magic", let's create a default "Import All" config if none exists.
    
    stmt = select(SyncConfig).where(
        SyncConfig.user_id == user.id,
        SyncConfig.source_type == "notion_database"
    )
    result = await db.execute(stmt)
    existing_config = result.scalar_one_or_none()
    
    if not existing_config:
        # Find the connection to get workspace info (if needed)
        # For now, just create a default config
        default_config = SyncConfig(
            id=uuid.uuid4(),
            user_id=user.id,
            source_type="notion_database",
            external_id="", # Empty implies "Search everything available" or we need to ask user to select DB
            filter_config={"tags": ["MakeQuiz"]},
            status="active"
        )
        db.add(default_config)
        await db.commit()

    # Create JWT Access Token
    access_token = create_access_token(subject=str(user.id))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id),
        "email": user.email,
    }


@router.post("/refresh")
async def refresh_token():
    """Refresh an expired JWT token."""
    # TODO: Implement token refresh logic
    raise HTTPException(status_code=501, detail="Not implemented")
