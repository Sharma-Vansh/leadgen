"""
FastAPI Dependencies
Provides database session injection and authenticated user extraction.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from module_2_database_and_ingestion.db.session import get_async_session
from module_3_backend_and_matching.auth.security import decode_token
from module_3_backend_and_matching.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency returning an asynchronous SQLAlchemy database session."""
    async with get_async_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Validates JWT bearer token and retrieves the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        if user_id is None or token_type != "access":
            raise credentials_exception
    except (jwt.PyJWTError, Exception):
        raise credentials_exception

    stmt = (
        select(User)
        .options(selectinload(User.student_profile))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    return user


async def get_current_student(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensures that the current user has the student role."""
    if current_user.role != "student" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student privileges required"
        )
    return current_user
