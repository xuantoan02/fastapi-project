"""Item management endpoints."""

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import CurrentUser, DBSession
from dependencies.pagination import PaginationParams
from schemas.common import Message, PaginatedResponse
from schemas.item import ItemCreate, ItemResponse, ItemUpdate
from services.item_service import ItemService

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[ItemResponse])
async def list_items(
    db: DBSession,
    current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[ItemResponse]:
    """List all items for the current user."""
    item_service = ItemService(db)
    items = await item_service.get_list_by_owner(
        current_user.id, skip=pagination.skip, limit=pagination.limit
    )
    total = await item_service.count_by_owner(current_user.id)

    return PaginatedResponse(
        items=[ItemResponse(**asdict(item)) for item in items],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(
    item_in: ItemCreate,
    db: DBSession,
    current_user: CurrentUser,
) -> ItemResponse:
    """Create a new item."""
    item_service = ItemService(db)
    item = await item_service.create(item_in, owner_id=current_user.id)
    return ItemResponse(**asdict(item))


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(
    item_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> ItemResponse:
    """Get an item by ID."""
    item_service = ItemService(db)
    item = await item_service.get_by_id_for_user(item_id, current_user)
    return ItemResponse(**asdict(item))


@router.patch("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_in: ItemUpdate,
    db: DBSession,
    current_user: CurrentUser,
) -> ItemResponse:
    """Update an item."""
    item_service = ItemService(db)
    item = await item_service.update(item_id, item_in, current_user)
    return ItemResponse(**asdict(item))


@router.delete("/{item_id}", response_model=Message)
async def delete_item(
    item_id: int,
    db: DBSession,
    current_user: CurrentUser,
) -> Message:
    """Delete an item."""
    item_service = ItemService(db)
    await item_service.delete(item_id, current_user)
    return Message(message="Item deleted successfully")
