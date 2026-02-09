"""
Auth Dependencies

TASK-016: FastAPI dependencies and security guards.

Features:
- JWT token extraction and validation
- Current user resolution
- Role-based access control
- Tenant isolation
"""
from typing import Optional, List
from functools import lru_cache

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_async_session
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.jwt_service import JWTService
from src.backend.app.auth.permissions import PermissionService
from src.backend.app.auth.exceptions import (
    InvalidCredentialsException,
    TokenExpiredException,
    InsufficientPermissionsException,
)


# HTTP Bearer scheme
bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache()
def get_jwt_service() -> JWTService:
    """Get JWT service singleton."""
    return JWTService()


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        InvalidCredentialsException: No token or invalid token
        TokenExpiredException: Token has expired
    """
    if not credentials:
        raise InvalidCredentialsException()
    
    token = credentials.credentials
    
    # Validate token
    is_valid, payload, error = jwt_service.validate_access_token(token)
    
    if not is_valid or payload is None:
        if error == "expired":
            raise TokenExpiredException()
        raise InvalidCredentialsException()
    
    # Get user from database
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidCredentialsException()
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise InvalidCredentialsException()
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> Optional[User]:
    """Get current user if authenticated, otherwise None."""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, session, jwt_service)
    except (InvalidCredentialsException, TokenExpiredException):
        return None


def require_role(*roles: Role):
    """
    Dependency factory for role-based access.
    
    Usage:
        @router.get("/admin")
        async def admin_only(user: User = Depends(require_role(Role.SUPER_ADMIN))):
            ...
    """
    async def role_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if user.role not in roles:
            raise InsufficientPermissionsException()
        return user
    
    return role_checker


def require_permission(permission: str):
    """
    Dependency factory for permission-based access.
    
    Usage:
        @router.post("/users")
        async def create_user(user: User = Depends(require_permission("users:write"))):
            ...
    """
    async def permission_checker(
        user: User = Depends(get_current_user),
    ) -> User:
        if not PermissionService.has_permission(user.role, permission):
            raise InsufficientPermissionsException()
        return user
    
    return permission_checker


async def get_client_info(request: Request) -> dict:
    """Extract client information from request."""
    # Get real IP (handle proxies)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip_address = forwarded.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client else "unknown"
    
    return {
        "ip_address": ip_address,
        "user_agent": request.headers.get("User-Agent", "unknown"),
    }


# Type aliases for common dependencies
SuperAdminUser = User  # After require_role(Role.SUPER_ADMIN)
AnalystUser = User     # After require_role(Role.SUPER_ADMIN, Role.ANALYST)
ClientAdminUser = User # After require_role(Role.CLIENT_ADMIN)
