"""Authentication dependencies for FastAPI."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncConnection

from core.exceptions import NotFoundError
from core.security import SymmetricJWT
from dependencies.database import get_db
from models.user import User
from services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
_jwt = SymmetricJWT()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncConnection, Depends(get_db)],
) -> User:
    """Get current authenticated user from JWT token."""
    payload = _jwt.decode(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload.get("sub", 0))
    user_service = UserService(db)
    try:
        user = await user_service.get_by_id(user_id)
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
    return user


async def get_current_active_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user and verify superuser status."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSuperuser = Annotated[User, Depends(get_current_active_superuser)]
DBSession = Annotated[AsyncConnection, Depends(get_db)]
