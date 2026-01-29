"""Authentication service for login and token operations."""

from sqlalchemy.ext.asyncio import AsyncConnection

from core.exceptions import UnauthorizedError
from core.security import SymmetricJWT, verify_password
from models.user import User
from schemas.token import Token
from services.user_service import UserService


class AuthService:
    """Service class for authentication operations."""

    def __init__(self, db: AsyncConnection) -> None:
        self.db = db
        self.user_service = UserService(db)
        self.jwt = SymmetricJWT()

    async def authenticate(self, email: str, password: str) -> User:
        """Authenticate a user with email and password."""
        user = await self.user_service.get_by_email(email)
        if not user:
            raise UnauthorizedError("Incorrect email or password")
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedError("User is inactive")
        return user

    async def login(self, email: str, password: str) -> Token:
        """Login and return access and refresh tokens."""
        user = await self.authenticate(email, password)
        return Token(
            access_token=self.jwt.create_access_token(user.id),
            refresh_token=self.jwt.create_refresh_token(user.id),
        )

    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        payload = self.jwt.decode(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user_id = int(payload.get("sub", 0))
        user = await self.user_service.get_by_id(user_id)
        if not user.is_active:
            raise UnauthorizedError("User is inactive")

        return Token(
            access_token=self.jwt.create_access_token(user.id),
            refresh_token=self.jwt.create_refresh_token(user.id),
        )
