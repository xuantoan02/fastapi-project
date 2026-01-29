"""Middleware package."""

from middleware.cors import setup_cors
from middleware.error_handler import setup_exception_handlers

__all__ = ["setup_cors", "setup_exception_handlers"]
