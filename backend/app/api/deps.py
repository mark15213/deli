# Authentication dependencies
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db
from app.models.models import User
from app.core.security import verify_token

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Get current user from JWT token.
    Validates token and retrieves user from database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
        
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    # Get user from DB
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get current active user.
    Can be extended to check for active status/roles.
    """
    # For now, all users are active
    # For now, all users are active
    return current_user

# --- Debug / Dev Dependencies ---

import uuid
from app.models.models import User

async def get_mock_user(db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    """
    Return a mock user for debugging/development without auth.
    Creates the user if not exists to ensure valid foreign keys.
    """
    # Use a fixed UUID for the mock user so it persists across restarts/calls effectively if DB is persistent
    mock_id = uuid.UUID("00000000-0000-0000-0000-000000000001") 
    
    # Try to find existing
    stmt = select(User).where(User.id == mock_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=mock_id,
            email="debug@deli.app",
            username="Debug User",
        )
        db.add(user)
        # Commit manually here since this is a dep? 
        # Ideally deps shouldn't commit side effects but for a mock user generator it's acceptable.
        await db.commit()
        await db.refresh(user)
        
    return user
