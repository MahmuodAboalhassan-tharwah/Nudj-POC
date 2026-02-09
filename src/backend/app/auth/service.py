"""
Auth Service

TASK-010: Core authentication service orchestrating login, registration, tokens.

Features:
- Login with lockout protection
- Registration via invitation
- Token refresh with rotation
- Logout with token revocation
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.app.auth.models import User, Role, RefreshToken
from src.backend.app.auth.jwt_service import jwt_service
from src.backend.app.auth.password_service import password_service
from src.backend.app.auth.invitation_service import InvitationService
from src.backend.app.auth.exceptions import (
    InvalidCredentialsException,
    AccountLockedException,
    AccountDeactivatedException,
    TokenInvalidException,
    TokenRevokedException,
    MFARequiredException,
    MFASetupRequiredException,
)


class AuthService:
    """
    Core authentication service.
    
    Handles login, registration, token management.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.max_attempts = settings.MAX_LOGIN_ATTEMPTS
        self.lockout_minutes = settings.LOCKOUT_DURATION_MINUTES
        self.mfa_mandatory_roles = settings.MFA_MANDATORY_ROLES

    async def login(
        self,
        email: str,
        password: str,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User's email
            password: Plain text password
            ip_address: Client IP for audit
            user_agent: Client user agent for audit
            
        Returns:
            Dict with tokens and user info, or MFA requirement
            
        Raises:
            InvalidCredentialsException: Invalid email/password
            AccountLockedException: Too many failed attempts
            AccountDeactivatedException: User is deactivated
        """
        # Find user
        result = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        # User not found - use same error for security
        if not user:
            raise InvalidCredentialsException()
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.utcnow():
            minutes_remaining = int(
                (user.locked_until - datetime.utcnow()).total_seconds() / 60
            )
            raise AccountLockedException(locked_until_minutes=minutes_remaining)
        
        # Check if account is active
        if not user.is_active:
            raise AccountDeactivatedException()
        
        # Verify password
        if not password_service.verify_password(password, user.password_hash):
            await self._handle_failed_login(user)
            raise InvalidCredentialsException()
        
        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.utcnow()
        
        # Check if MFA is required
        if user.mfa_enabled:
            # Return MFA pending token
            mfa_token = jwt_service.create_mfa_pending_token(
                user_id=user.id,
                email=user.email,
            )
            return {
                "requires_mfa": True,
                "mfa_token": mfa_token,
            }
        
        # Check if MFA setup is required for this role
        if user.role.value in self.mfa_mandatory_roles and not user.mfa_enabled:
            raise MFASetupRequiredException()
        
        # Generate tokens
        return await self._generate_auth_response(user, ip_address, user_agent)

    async def register(
        self,
        token: str,
        password: str,
        name_ar: str,
        name_en: str,
        phone_sa: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Register a new user via invitation.
        
        Args:
            token: Invitation token
            password: New password
            name_ar: Arabic name
            name_en: English name
            phone_sa: Optional Saudi phone
            
        Returns:
            Dict with tokens and user info
        """
        # Validate and consume invitation
        invitation_service = InvitationService(self.session)
        invitation = await invitation_service.consume_invitation(token)
        
        # Validate password
        is_valid, missing = password_service.validate_password(password)
        if not is_valid:
            from src.backend.app.auth.exceptions import PasswordTooWeakException
            raise PasswordTooWeakException(missing_requirements=missing)
        
        # Create user
        user = User(
            email=invitation.email,
            password_hash=password_service.hash_password(password),
            name_ar=name_ar,
            name_en=name_en,
            phone_sa=phone_sa,
            role=invitation.role,
            organization_id=invitation.organization_id,
            is_active=True,
            is_verified=True,  # Verified by invitation
            created_by_invitation_id=invitation.id,
        )
        
        self.session.add(user)
        await self.session.flush()
        
        # Create domain assignments if specified
        if invitation.domain_ids:
            from src.backend.app.auth.models import UserDomainAssignment
            
            assignment = UserDomainAssignment(
                user_id=user.id,
                domain_ids=invitation.domain_ids,
                assigned_by=invitation.invited_by,
            )
            self.session.add(assignment)
        
        # Check if MFA setup is required
        if user.role.value in self.mfa_mandatory_roles:
            # Return user info but indicate MFA setup required
            return {
                "requires_mfa_setup": True,
                "user": self._user_to_dict(user),
            }
        
        return await self._generate_auth_response(user, "127.0.0.1", None)

    async def refresh_tokens(
        self,
        refresh_token: str,
        ip_address: str,
        user_agent: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Refresh access token using refresh token.
        
        Implements token rotation - old refresh token is revoked.
        
        Args:
            refresh_token: Current refresh token
            ip_address: Client IP
            user_agent: Client user agent
            
        Returns:
            Dict with new tokens
            
        Raises:
            TokenInvalidException: Token invalid or expired
            TokenRevokedException: Token already revoked
        """
        # Decode refresh token
        try:
            payload = jwt_service.decode_token(refresh_token, expected_type="refresh")
        except Exception:
            raise TokenInvalidException()
        
        user_id = payload["sub"]
        jti = payload["jti"]
        
        # Find token in database
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.token_hash == jwt_service._hash_token(jti),
            )
        )
        stored_token = result.scalar_one_or_none()
        
        if not stored_token:
            raise TokenInvalidException()
        
        if stored_token.revoked_at:
            raise TokenRevokedException()
        
        # Revoke old token
        stored_token.revoked_at = datetime.utcnow()
        
        # Get user
        user = await self.session.get(User, user_id)
        if not user or not user.is_active:
            raise TokenInvalidException()
        
        # Generate new tokens
        return await self._generate_auth_response(user, ip_address, user_agent)

    async def logout(
        self,
        user_id: str,
        refresh_token: Optional[str] = None,
        revoke_all: bool = False,
    ) -> None:
        """
        Logout user by revoking tokens.
        
        Args:
            user_id: User to logout
            refresh_token: Specific token to revoke
            revoke_all: Revoke all user's refresh tokens
        """
        now = datetime.utcnow()
        
        if revoke_all:
            # Revoke all refresh tokens
            await self.session.execute(
                update(RefreshToken)
                .where(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked_at.is_(None),
                )
                .values(revoked_at=now)
            )
        elif refresh_token:
            # Revoke specific token
            try:
                payload = jwt_service.decode_token(refresh_token, expected_type="refresh")
                jti = payload["jti"]
                
                await self.session.execute(
                    update(RefreshToken)
                    .where(RefreshToken.token_hash == jwt_service._hash_token(jti))
                    .values(revoked_at=now)
                )
            except Exception:
                pass  # Token already invalid, just continue

    async def _handle_failed_login(self, user: User) -> None:
        """Handle failed login attempt."""
        user.failed_login_attempts += 1
        
        if user.failed_login_attempts >= self.max_attempts:
            user.locked_until = datetime.utcnow() + timedelta(
                minutes=self.lockout_minutes
            )

    async def _generate_auth_response(
        self,
        user: User,
        ip_address: str,
        user_agent: Optional[str],
    ) -> Dict[str, Any]:
        """Generate tokens and auth response."""
        # Get permissions based on role
        permissions = self._get_role_permissions(user.role)
        
        # Create access token
        access_token = jwt_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
            organization_id=user.organization_id,
            mfa_verified=user.mfa_enabled,
            permissions=permissions,
        )
        
        # Create and store refresh token
        refresh_token, token_hash = jwt_service.create_refresh_token(
            user_id=user.id,
        )
        
        stored_refresh = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            ),
            device_info=user_agent,
            ip_address=ip_address,
        )
        self.session.add(stored_refresh)
        
        return {
            "requires_mfa": False,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": self._user_to_dict(user),
        }

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user to response dict."""
        return {
            "id": user.id,
            "email": user.email,
            "name_ar": user.name_ar,
            "name_en": user.name_en,
            "role": user.role.value,
            "organization_id": user.organization_id,
            "mfa_enabled": user.mfa_enabled,
            "permissions": self._get_role_permissions(user.role),
        }

    def _get_role_permissions(self, role: Role) -> list[str]:
        """Get permissions for a role."""
        # Hierarchical permissions
        permissions_map = {
            Role.SUPER_ADMIN: [
                "users:read", "users:write", "users:delete",
                "orgs:read", "orgs:write", "orgs:delete",
                "assessments:read", "assessments:write",
                "reports:read", "reports:write",
                "audit:read", "settings:write",
            ],
            Role.ANALYST: [
                "users:read",
                "orgs:read",
                "assessments:read", "assessments:write",
                "reports:read", "reports:write",
            ],
            Role.CLIENT_ADMIN: [
                "users:read", "users:write",
                "assessments:read", "assessments:write",
                "reports:read",
            ],
            Role.ASSESSOR: [
                "assessments:read",
            ],
        }
        return permissions_map.get(role, [])
