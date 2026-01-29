"""User service for business logic operations using raw SQL."""

from sqlalchemy.ext.asyncio import AsyncConnection

from core.exceptions import ConflictError, NotFoundError
from core.security import get_password_hash
from db.session import fetch_all, fetch_one, fetch_scalar, execute_query
from models.user import User
from schemas.user import UserCreate, UserUpdate


class UserService:
    """Service class for user-related operations using raw SQL."""

    def __init__(self, db: AsyncConnection) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User:
        """Get a user by ID."""
        query = """
            SELECT id, email, hashed_password, full_name, is_active, is_superuser,
                   created_at, updated_at
            FROM users
            WHERE id = :user_id
        """
        row = await fetch_one(self.db, query, {"user_id": user_id})
        if not row:
            raise NotFoundError("User")
        return User.from_row(row)

    async def get_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        query = """
            SELECT id, email, hashed_password, full_name, is_active, is_superuser,
                   created_at, updated_at
            FROM users
            WHERE email = :email
        """
        row = await fetch_one(self.db, query, {"email": email})
        if row:
            return User.from_row(row)
        return None

    async def get_list(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get a list of users with pagination."""
        query = """
            SELECT id, email, hashed_password, full_name, is_active, is_superuser,
                   created_at, updated_at
            FROM users
            ORDER BY id
            OFFSET :skip LIMIT :limit
        """
        rows = await fetch_all(self.db, query, {"skip": skip, "limit": limit})
        return [User.from_row(row) for row in rows]

    async def count(self) -> int:
        """Count total users."""
        query = "SELECT COUNT(id) FROM users"
        result = await fetch_scalar(self.db, query)
        return result or 0

    async def create(self, user_in: UserCreate) -> User:
        """Create a new user."""
        existing = await self.get_by_email(user_in.email)
        if existing:
            raise ConflictError("User with this email already exists")

        query = """
            INSERT INTO users (email, hashed_password, full_name, is_active, is_superuser,
                              created_at, updated_at)
            VALUES (:email, :hashed_password, :full_name, :is_active, :is_superuser,
                   NOW(), NOW())
            RETURNING id, email, hashed_password, full_name, is_active, is_superuser,
                      created_at, updated_at
        """
        params = {
            "email": user_in.email,
            "hashed_password": get_password_hash(user_in.password),
            "full_name": user_in.full_name,
            "is_active": True,
            "is_superuser": False,
        }
        row = await fetch_one(self.db, query, params)
        return User.from_row(row)

    async def update(self, user_id: int, user_in: UserUpdate) -> User:
        """Update an existing user."""
        await self.get_by_id(user_id)

        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        if not update_data:
            return await self.get_by_id(user_id)

        set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        update_data["user_id"] = user_id

        query = f"""
            UPDATE users
            SET {set_clauses}, updated_at = NOW()
            WHERE id = :user_id
            RETURNING id, email, hashed_password, full_name, is_active, is_superuser,
                      created_at, updated_at
        """
        row = await fetch_one(self.db, query, update_data)
        return User.from_row(row)

    async def delete(self, user_id: int) -> None:
        """Delete a user."""
        await self.get_by_id(user_id)
        query = "DELETE FROM users WHERE id = :user_id"
        await execute_query(self.db, query, {"user_id": user_id})
