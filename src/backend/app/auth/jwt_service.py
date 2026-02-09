"""
JWT Service

TASK-007: JWT token creation, validation, and management.

Features:
- Access token generation (15 min expiry)
- Refresh token generation (7 days expiry)
- Token validation and decoding
- Token revocation support via Redis
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import secrets

import jwt
from pydantic import BaseModel

from src.backend.config import settings


class TokenPayload(BaseModel):
    """JWT payload structure."""
    sub: str  # User ID
    email: str
    role: str
    org: Optional[str] = None  # Organization ID
    mfa: bool = False  # MFA verified
    permissions: list[str] = []
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for revocation


class JWTService:
    """
    JWT token management service.
    
    Uses HS256 for POC (migratable to RS256 for production).
    """

    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS

    def create_access_token(
        self,
        user_id: str,
        email: str,
        role: str,
        organization_id: Optional[str] = None,
        mfa_verified: bool = False,
        permissions: list[str] = [],
        additional_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a short-lived access token.
        
        Args:
            user_id: User's unique ID
            email: User's email
            role: User's role (super_admin, analyst, etc.)
            organization_id: User's organization (null for Super Admin)
            mfa_verified: Whether MFA has been verified
            permissions: List of permission strings
            additional_claims: Any extra claims to include
            
        Returns:
            Encoded JWT string
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "role": role,
            "org": organization_id,
            "mfa": mfa_verified,
            "permissions": permissions,
            "exp": expire,
            "iat": now,
            "jti": self._generate_jti(),
            "type": "access",
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(
        self,
        user_id: str,
        device_info: Optional[str] = None,
    ) -> tuple[str, str]:
        """
        Create a long-lived refresh token.
        
        Returns:
            Tuple of (token, token_hash) - store hash in DB
        """
        now = datetime.utcnow()
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        # Generate a secure random token
        raw_token = secrets.token_urlsafe(32)
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "jti": self._generate_jti(),
            "type": "refresh",
        }
        
        encoded = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        token_hash = self._hash_token(raw_token)
        
        return encoded, token_hash

    def create_mfa_pending_token(
        self,
        user_id: str,
        email: str,
    ) -> str:
        """
        Create a short-lived token for MFA verification step.
        
        Valid for 5 minutes only.
        """
        now = datetime.utcnow()
        expire = now + timedelta(minutes=5)
        
        payload = {
            "sub": user_id,
            "email": email,
            "exp": expire,
            "iat": now,
            "jti": self._generate_jti(),
            "type": "mfa_pending",
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(
        self,
        token: str,
        expected_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Decode and validate a JWT token.
        
        Args:
            token: The JWT string
            expected_type: Optional check for token type (access, refresh, mfa_pending)
            
        Returns:
            Decoded payload dict
            
        Raises:
            jwt.ExpiredSignatureError: Token has expired
            jwt.InvalidTokenError: Token is invalid
        """
        payload = jwt.decode(
            token,
            self.secret_key,
            algorithms=[self.algorithm],
            options={"verify_exp": True},
        )
        
        if expected_type and payload.get("type") != expected_type:
            raise jwt.InvalidTokenError(f"Expected {expected_type} token")
        
        return payload

    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Verify an access token and return typed payload.
        
        Raises:
            jwt.ExpiredSignatureError: Token expired
            jwt.InvalidTokenError: Token invalid
        """
        payload = self.decode_token(token, expected_type="access")
        
        return TokenPayload(
            sub=payload["sub"],
            email=payload["email"],
            role=payload["role"],
            org=payload.get("org"),
            mfa=payload.get("mfa", False),
            permissions=payload.get("permissions", []),
            exp=datetime.fromtimestamp(payload["exp"]),
            iat=datetime.fromtimestamp(payload["iat"]),
            jti=payload["jti"],
        )

    def get_token_jti(self, token: str) -> str:
        """Extract JTI from token without full validation."""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )
            return payload.get("jti", "")
        except jwt.InvalidTokenError:
            return ""

    def _generate_jti(self) -> str:
        """Generate a unique JWT ID."""
        return secrets.token_urlsafe(16)

    def _hash_token(self, token: str) -> str:
        """Hash a token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()


# Global service instance
jwt_service = JWTService()
