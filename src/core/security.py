"""Security utilities for password hashing and JWT handling."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


class JWTStrategy(ABC):
    """Abstract base class for JWT signing strategies."""

    @abstractmethod
    def encode(self, payload: dict) -> str:
        """Encode payload to JWT token."""
        pass

    @abstractmethod
    def decode(self, token: str) -> dict | None:
        """Decode JWT token to payload."""
        pass

    def _build_access_payload(
        self, subject: str | int, expires_delta: timedelta | None = None
    ) -> dict:
        """Build payload for access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        return {"exp": expire, "sub": str(subject), "type": "access"}

    def _build_refresh_payload(self, subject: str | int) -> dict:
        """Build payload for refresh token."""
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
        return {"exp": expire, "sub": str(subject), "type": "refresh"}

    def create_access_token(
        self, subject: str | int, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token."""
        payload = self._build_access_payload(subject, expires_delta)
        return self.encode(payload)

    def create_refresh_token(self, subject: str | int) -> str:
        """Create a JWT refresh token."""
        payload = self._build_refresh_payload(subject)
        return self.encode(payload)


class SymmetricJWT(JWTStrategy):
    """
    Symmetric JWT strategy using HMAC algorithms (HS256, HS384, HS512).

    Uses the same secret key for both signing and verification.
    Best for: Monolithic applications, simple setups.
    """

    def __init__(
        self,
        secret_key: str | None = None,
        algorithm: str = "HS256",
    ):
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm
        if not self.algorithm.startswith("HS"):
            raise ValueError(f"SymmetricJWT requires HS* algorithm, got {algorithm}")

    def encode(self, payload: dict) -> str:
        """Encode payload using symmetric key."""
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict | None:
        """Decode token using symmetric key."""
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            return None


class AsymmetricJWT(JWTStrategy):
    """
    Asymmetric JWT strategy using RSA algorithms (RS256, RS384, RS512).

    Uses private key for signing and public key for verification.
    Best for: Microservices, distributed systems where services only need to verify tokens.
    """

    def __init__(
        self,
        private_key: str | None = None,
        public_key: str | None = None,
        algorithm: str = "RS256",
    ):
        self.private_key = private_key
        self.public_key = public_key
        self.algorithm = algorithm
        if not self.algorithm.startswith("RS"):
            raise ValueError(f"AsymmetricJWT requires RS* algorithm, got {algorithm}")

    def encode(self, payload: dict) -> str:
        """Encode payload using private key."""
        if not self.private_key:
            raise ValueError("Private key required for encoding")
        return jwt.encode(payload, self.private_key, algorithm=self.algorithm)

    def decode(self, token: str) -> dict | None:
        """Decode token using public key."""
        if not self.public_key:
            raise ValueError("Public key required for decoding")
        try:
            return jwt.decode(token, self.public_key, algorithms=[self.algorithm])
        except JWTError:
            return None

    @staticmethod
    def generate_keypair(key_size: int = 2048) -> tuple[str, str]:
        """Generate RSA key pair (private_key, public_key) in PEM format."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        public_key = private_key.public_key()

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode()

        return private_pem, public_pem


