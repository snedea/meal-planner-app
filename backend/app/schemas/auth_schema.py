"""Authentication-related Pydantic schemas."""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request."""
    refresh_token: str


class TokenData(BaseModel):
    """Schema for token data."""
    sub: str  # user_id
    type: str  # 'access' or 'refresh'
