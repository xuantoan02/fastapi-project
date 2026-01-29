"""Database session management using raw SQL queries."""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from core.config import settings

engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


async def get_db() -> AsyncGenerator[AsyncConnection, None]:
    """Dependency for getting async database connections for raw SQL queries."""
    async with engine.connect() as conn:
        try:
            yield conn
            await conn.commit()
        except Exception:
            await conn.rollback()
            raise


async def execute_query(conn: AsyncConnection, query: str, params: dict | None = None):
    """Execute a raw SQL query and return the result."""
    result = await conn.execute(text(query), params or {})
    return result


async def fetch_one(conn: AsyncConnection, query: str, params: dict | None = None):
    """Execute query and fetch one row as dict."""
    result = await conn.execute(text(query), params or {})
    row = result.fetchone()
    if row:
        return dict(row._mapping)
    return None


async def fetch_all(conn: AsyncConnection, query: str, params: dict | None = None):
    """Execute query and fetch all rows as list of dicts."""
    result = await conn.execute(text(query), params or {})
    rows = result.fetchall()
    return [dict(row._mapping) for row in rows]


async def fetch_scalar(conn: AsyncConnection, query: str, params: dict | None = None):
    """Execute query and fetch single scalar value."""
    result = await conn.execute(text(query), params or {})
    return result.scalar()
