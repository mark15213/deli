# Authentication Service
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models import User, NotionConnection
from app.core.security import encrypt_token
from app.services.notion_service import NotionService


class AuthService:
    """Service for handling user authentication and Notion integration."""
    
    @staticmethod
    async def authenticate_notion_user(db: AsyncSession, code: str) -> User:
        """
        Handle full Notion OAuth flow:
        1. Exchange code for Notion token
        2. Find or create User based on Notion owner info
        3. Update NotionConnection
        """
        # 1. Exchange token
        token_data = await NotionService.exchange_code_for_token(code)
        
        access_token = token_data.get("access_token")
        workspace_id = token_data.get("workspace_id")
        workspace_name = token_data.get("workspace_name")
        owner = token_data.get("owner", {}).get("user", {})
        
        email = owner.get("email")
        if not email:
            # Fallback if email is not provided (rare but possible)
            # We might generate a placeholder or raise error depending on policy
            raise HTTPException(status_code=400, detail="Could not retrieve email from Notion user")

        # 2. Find or create User
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                id=uuid.uuid4(),
                email=email,
                preferences={},  # Default preferences
            )
            db.add(user)
            # Flush to get user ID for connection
            await db.flush()
        
        # 3. Create or Update NotionConnection
        # We assume one connection per user for MVP, or per workspace
        # Check if this user already checks this workspace
        conn_stmt = select(NotionConnection).where(
            NotionConnection.user_id == user.id,
            NotionConnection.workspace_id == workspace_id
        )
        conn_result = await db.execute(conn_stmt)
        connection = conn_result.scalar_one_or_none()
        
        encrypted_token = encrypt_token(access_token)
        
        if connection:
            connection.access_token_encrypted = encrypted_token
            connection.workspace_name = workspace_name
            # Don't overwrite selected_databases if already set
        else:
            connection = NotionConnection(
                id=uuid.uuid4(),
                user_id=user.id,
                access_token_encrypted=encrypted_token,
                workspace_id=workspace_id,
                workspace_name=workspace_name,
                selected_databases={},
            )
            db.add(connection)
            
        await db.commit()
        await db.refresh(user, attribute_names=["notion_connections"])
        
        return user
