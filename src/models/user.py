"""User data class for type hints and data transfer."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """User data class representing a user record."""

    id: int
    email: str
    hashed_password: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_row(cls, row: dict) -> "User":
        """Create User instance from database row dict."""
        return cls(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            full_name=row.get("full_name"),
            is_active=row["is_active"],
            is_superuser=row["is_superuser"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
