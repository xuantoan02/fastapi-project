"""User management endpoints."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import CurrentSuperuser, CurrentUser, DBSession
from dependencies.pagination import PaginationParams
from schemas.common import Message, PaginatedResponse
from schemas.user import UserResponse, UserUpdate
from services.user_service import UserService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[UserResponse])
async def list_users(
    db: DBSession,
    current_user: CurrentSuperuser,
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[UserResponse]:
    """List all users (admin only)."""
    user_service = UserService(db)
    users = await user_service.get_list(pagination.skip, pagination.limit)
    total = await user_service.count()
    return PaginatedResponse(
        items=[UserResponse(**asdict(u)) for u in users],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    """Get a specific user by ID."""
    user_service = UserService(db)
    user = await user_service.get_by_id(user_id)
    return UserResponse(**asdict(user))


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> UserResponse:
    """Update a user."""
    user_service = UserService(db)
    user = await user_service.update(user_id, user_in)
    return UserResponse(**asdict(user))


@router.delete("/{user_id}", response_model=Message)
async def delete_user(
    user_id: int,
    db: DBSession,
    current_user: CurrentSuperuser,
) -> Message:
    """Delete a user (admin only)."""
    user_service = UserService(db)
    await user_service.delete(user_id)
    return Message(message="User deleted successfully")
