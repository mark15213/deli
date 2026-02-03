from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token, get_password_hash, verify_password
from app.services.auth_service import AuthService
from app.services.notion_service import NotionService
from app.models import Source, OAuthConnection, User
from app.schemas import Token, RefreshTokenRequest, UserCreate, UserLogin, UserResponse
from app.api.deps import get_current_user

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/notion/login")
async def notion_login():
    """Redirect to Notion OAuth page."""
    auth_url = NotionService.get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/notion/callback", response_model=Token)
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

    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=str(user.id),
        email=user.email,
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh an expired access token using a valid refresh token.
    """
    payload = verify_token(request.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    # Check if it is actually a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")
        
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token subject")
    
    # Issue new access token
    # We can also issue a new refresh token if we want rotation, 
    # but for now let's just rotate access token and keep refresh token until it expires
    access_token = create_access_token(subject=user_id)
    
    return Token(
        access_token=access_token,
        refresh_token=request.refresh_token, # Return same refresh token
        token_type="bearer",
        user_id=user_id
    )


@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user with invite code."""
    # Validate invite code
    VALID_INVITE_CODE = "5566"
    if user_in.invite_code != VALID_INVITE_CODE:
        raise HTTPException(
            status_code=400,
            detail="Invalid invite code",
        )
    
    # Check existing user
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user = User(
        id=uuid.uuid4(),
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        username=user_in.email.split("@")[0], # Default username
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    stmt = select(User).where(User.email == user_in.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not user.hashed_password or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=str(user.id),
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_user),
):
    """Get current user."""
    return current_user
