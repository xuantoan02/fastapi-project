"""Item service for business logic operations using raw SQL."""

from sqlalchemy.ext.asyncio import AsyncConnection

from core.exceptions import ForbiddenError, NotFoundError
from db.session import execute_query, fetch_all, fetch_one, fetch_scalar
from models.item import Item
from models.user import User
from schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Service class for item-related operations using raw SQL."""

    def __init__(self, db: AsyncConnection) -> None:
        self.db = db

    async def get_by_id(self, item_id: int) -> Item:
        """Get an item by ID."""
        query = """
            SELECT id, title, description, owner_id, created_at, updated_at
            FROM items
            WHERE id = :item_id
        """
        row = await fetch_one(self.db, query, {"item_id": item_id})
        if not row:
            raise NotFoundError("Item")
        return Item.from_row(row)

    async def get_by_id_for_user(self, item_id: int, user: User) -> Item:
        """Get an item by ID and verify user access."""
        item = await self.get_by_id(item_id)
        if item.owner_id != user.id and not user.is_superuser:
            raise ForbiddenError("Not authorized to access this item")
        return item

    async def get_list_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[Item]:
        """Get a list of items for a specific owner with pagination."""
        query = """
            SELECT id, title, description, owner_id, created_at, updated_at
            FROM items
            WHERE owner_id = :owner_id
            ORDER BY id
            OFFSET :skip LIMIT :limit
        """
        rows = await fetch_all(
            self.db, query, {"owner_id": owner_id, "skip": skip, "limit": limit}
        )
        return [Item.from_row(row) for row in rows]

    async def count_by_owner(self, owner_id: int) -> int:
        """Count total items for a specific owner."""
        query = "SELECT COUNT(id) FROM items WHERE owner_id = :owner_id"
        result = await fetch_scalar(self.db, query, {"owner_id": owner_id})
        return result or 0

    async def create(self, item_in: ItemCreate, owner_id: int) -> Item:
        """Create a new item."""
        query = """
            INSERT INTO items (title, description, owner_id, created_at, updated_at)
            VALUES (:title, :description, :owner_id, NOW(), NOW())
            RETURNING id, title, description, owner_id, created_at, updated_at
        """
        params = {
            "title": item_in.title,
            "description": item_in.description,
            "owner_id": owner_id,
        }
        row = await fetch_one(self.db, query, params)
        return Item.from_row(row)

    async def update(self, item_id: int, item_in: ItemUpdate, user: User) -> Item:
        """Update an existing item."""
        item = await self.get_by_id(item_id)
        if item.owner_id != user.id and not user.is_superuser:
            raise ForbiddenError("Not authorized to modify this item")

        update_data = item_in.model_dump(exclude_unset=True)
        if not update_data:
            return item

        set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        update_data["item_id"] = item_id

        query = f"""
            UPDATE items
            SET {set_clauses}, updated_at = NOW()
            WHERE id = :item_id
            RETURNING id, title, description, owner_id, created_at, updated_at
        """
        row = await fetch_one(self.db, query, update_data)
        return Item.from_row(row)

    async def delete(self, item_id: int, user: User) -> None:
        """Delete an item."""
        item = await self.get_by_id(item_id)
        if item.owner_id != user.id and not user.is_superuser:
            raise ForbiddenError("Not authorized to delete this item")

        query = "DELETE FROM items WHERE id = :item_id"
        await execute_query(self.db, query, {"item_id": item_id})
