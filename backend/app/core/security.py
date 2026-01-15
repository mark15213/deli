# Security utilities for JWT and encryption
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from app.core.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str) -> dict | None:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        return None


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


# Fernet encryption for Notion tokens
_fernet_key: bytes | None = None


def _get_fernet() -> Fernet:
    """Get or create Fernet instance for encryption."""
    global _fernet_key
    if _fernet_key is None:
        # Derive a valid Fernet key from secret_key
        import hashlib
        import base64
        key = hashlib.sha256(settings.secret_key.encode()).digest()
        _fernet_key = base64.urlsafe_b64encode(key)
    return Fernet(_fernet_key)


def encrypt_token(token: str) -> str:
    """Encrypt a token for secure storage."""
    f = _get_fernet()
    return f.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a stored token."""
    f = _get_fernet()
    return f.decrypt(encrypted_token.encode()).decode()
