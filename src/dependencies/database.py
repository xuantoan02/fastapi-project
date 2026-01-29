"""Database dependency for FastAPI."""

from db.session import get_db

__all__ = ["get_db"]
