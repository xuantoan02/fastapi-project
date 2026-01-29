"""Custom exception classes for the application."""

from typing import Any


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        detail: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found error."""

    def __init__(self, resource: str = "Resource", detail: Any = None) -> None:
        super().__init__(
            message=f"{resource} not found",
            status_code=404,
            detail=detail,
        )


class BadRequestError(AppException):
    """Bad request error."""

    def __init__(self, message: str = "Bad request", detail: Any = None) -> None:
        super().__init__(message=message, status_code=400, detail=detail)


class UnauthorizedError(AppException):
    """Authentication error."""

    def __init__(
        self, message: str = "Could not validate credentials", detail: Any = None
    ) -> None:
        super().__init__(message=message, status_code=401, detail=detail)


class ForbiddenError(AppException):
    """Authorization error."""

    def __init__(
        self, message: str = "Not enough permissions", detail: Any = None
    ) -> None:
        super().__init__(message=message, status_code=403, detail=detail)


class ConflictError(AppException):
    """Conflict error (e.g., duplicate resource)."""

    def __init__(
        self, message: str = "Resource already exists", detail: Any = None
    ) -> None:
        super().__init__(message=message, status_code=409, detail=detail)
