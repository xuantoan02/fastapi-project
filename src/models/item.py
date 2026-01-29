"""Item data class for type hints and data transfer."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Item:
    """Item data class representing an item record."""

    id: int
    title: str
    description: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "Item":
        """Create Item instance from database row dict."""
        return cls(
            id=row["id"],
            title=row["title"],
            description=row.get("description"),
            owner_id=row["owner_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def __repr__(self) -> str:
        return f"<Item(id={self.id}, title={self.title})>"
