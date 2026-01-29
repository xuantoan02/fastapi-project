"""Error handling middleware."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException


def setup_exception_handlers(app: FastAPI) -> None:
    """Setup custom exception handlers for the application."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if app.debug else None,
            },
        )
