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
from app.models import Source, OAuthConnection

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
    
    # Check/Create Default Source
    # Check if we have a source for this user's notion connection
    
    stmt = select(Source).where(
        Source.user_id == user.id,
        Source.type == "NOTION_KB"
    )
    result = await db.execute(stmt)
    existing_source = result.scalar_one_or_none()
    
    if not existing_source:
        # Create a default source for the workspace
        default_source = Source(
            id=uuid.uuid4(),
            user_id=user.id,
            name="Notion Connection",
            type="NOTION_KB",
            connection_config={}, # Config is largely in OAuthConnection for now, or could duplicate relevant bits
            ingestion_rules={"tags": ["MakeQuiz"]},
            status="ACTIVE"
        )
        db.add(default_source)
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
