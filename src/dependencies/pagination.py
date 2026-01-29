"""Pagination dependency for FastAPI."""

from typing import Annotated

from fastapi import Query


class PaginationParams:
    """Pagination parameters for list endpoints."""

    def __init__(
        self,
        skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
        limit: Annotated[
            int, Query(ge=1, le=100, description="Number of items to return")
        ] = 20,
    ) -> None:
        self.skip = skip
        self.limit = limit


Pagination = Annotated[PaginationParams, Query()]
