"""
Authentication Pydantic Schemas
Defines request and response structures for user registration, login, and JWT tokens.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128, description="Plaintext password (min 6 characters)")
    full_name: str = Field(..., min_length=2, max_length=128, description="Candidate full legal name")
    role: Optional[str] = "student"


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    is_active: bool
    auth_provider: str
    has_profile: bool = False

    model_config = ConfigDict(from_attributes=True)
