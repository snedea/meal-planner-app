"""Authentication utilities for JWT and password hashing."""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from app.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt directly.

    Note: bcrypt has a 72-byte limit. We explicitly truncate to ensure
    compatibility and security.

    Args:
        password: Plain text password

    Returns:
        Hashed password as a string
    """
    # Truncate to 72 bytes (bcrypt's maximum)
    password_bytes = password.encode('utf-8')[:72]

    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password
        hashed_password: Hashed password (string from database)

    Returns:
        True if password matches, False otherwise
    """
    # Truncate to 72 bytes (same as hashing)
    password_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')

    try:
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except ValueError:
        # Invalid hash format
        return False


def create_access_token(user_id: str) -> str:
    """
    Create JWT access token.

    Args:
        user_id: User ID to encode in token

    Returns:
        JWT access token
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Create JWT refresh token.

    Args:
        user_id: User ID to encode in token

    Returns:
        JWT refresh token
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token data or None if invalid

    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
