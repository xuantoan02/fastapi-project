"""Authentication endpoints."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from dependencies import CurrentUser, DBSession
from schemas.token import Token
from schemas.user import UserCreate, UserResponse
from services.auth_service import AuthService
from services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, db: DBSession) -> UserResponse:
    """Register a new user."""
    user_service = UserService(db)
    user = await user_service.create(user_in)
    return UserResponse(**asdict(user))


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
) -> Token:
    """Login and get access token."""
    auth_service = AuthService(db)
    return await auth_service.login(form_data.username, form_data.password)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: DBSession) -> Token:
    """Refresh access token."""
    auth_service = AuthService(db)
    return await auth_service.refresh_token(refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser) -> UserResponse:
    """Get current user information."""
    return UserResponse(**asdict(current_user))
