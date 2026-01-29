"""Item schemas for request/response validation."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """Base item schema with common fields."""

    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    """Schema for creating a new item."""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""

    title: str | None = None
    description: str | None = None


class ItemResponse(ItemBase):
    """Schema for item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
