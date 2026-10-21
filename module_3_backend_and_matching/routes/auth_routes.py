"""
Authentication Routes
Endpoints for user registration, login, token refresh, and profile session info.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from module_3_backend_and_matching.auth.dependencies import get_db, get_current_user
from module_3_backend_and_matching.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from module_3_backend_and_matching.models.user import User
from module_3_backend_and_matching.models.student_profile import StudentProfile
from module_3_backend_and_matching.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Registers a new candidate student and initializes their profile."""
    # Check if email is already taken
    stmt = select(User).where(User.email == payload.email.lower().strip())
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists"
        )

    # Create User
    new_user = User(
        email=payload.email.lower().strip(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=payload.role or "student",
        auth_provider="email",
        is_active=True
    )
    db.add(new_user)
    await db.flush()  # Generate user.id

    # Create associated default StudentProfile
    profile = StudentProfile(
        user_id=new_user.id,
        skills=[],
        certifications=[],
        preferred_roles=[],
        preferred_locations=[],
        profile_completeness_pct=15.0  # Basic info present
    )
    db.add(profile)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT Tokens
    token_data = {"sub": new_user.id, "email": new_user.email, "role": new_user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=new_user.id,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role
    )


@router.post("/login", response_model=TokenResponse)
async def login_user(
    payload: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Authenticates candidate credentials and issues fresh JWT access/refresh tokens."""
    stmt = select(User).where(User.email == payload.email.lower().strip())
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is currently suspended"
        )

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Rotates refresh tokens and issues fresh access tokens."""
    try:
        decoded = decode_token(payload.refresh_token)
        if decoded.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
        user_id = decoded.get("sub")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    token_data = {"sub": user.id, "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role
    )


@router.get("/me", response_model=UserResponse)
async def get_my_account(
    current_user: User = Depends(get_current_user)
):
    """Returns the current authenticated user's profile and authorization details."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        auth_provider=current_user.auth_provider,
        has_profile=current_user.student_profile is not None
    )
