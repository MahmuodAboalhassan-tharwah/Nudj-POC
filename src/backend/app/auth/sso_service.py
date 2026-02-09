"""
SSO Service

TASK-013: Single Sign-On integration (stubbed for POC).

Features:
- Azure AD OAuth2 flow (placeholder)
- Google Workspace OAuth2 flow (placeholder)
- User matching by email
- Organization-based SSO config
"""
from typing import Optional, Dict, Any
from urllib.parse import urlencode

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.app.auth.models import User, SSOConfiguration, SSOProvider
from src.backend.app.auth.exceptions import (
    SSONotConfiguredException,
    SSOAuthenticationFailedException,
    SSOUserNotInvitedException,
)


class SSOService:
    """
    Single Sign-On service.
    
    NOTE: This is a stub implementation for POC.
    In production, integrate with Azure AD and Google OAuth2.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_sso_config(
        self,
        organization_id: str,
        provider: SSOProvider,
    ) -> Optional[SSOConfiguration]:
        """Get SSO configuration for an organization."""
        result = await self.session.execute(
            select(SSOConfiguration).where(
                SSOConfiguration.organization_id == organization_id,
                SSOConfiguration.provider == provider,
                SSOConfiguration.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def initiate_sso(
        self,
        organization_id: str,
        provider: SSOProvider,
        redirect_uri: str,
    ) -> str:
        """
        Initiate SSO login flow.
        
        Args:
            organization_id: Organization to authenticate for
            provider: SSO provider (azure_ad, google)
            redirect_uri: OAuth callback URL
            
        Returns:
            Authorization URL to redirect user to
            
        Raises:
            SSONotConfiguredException: SSO not set up for org
        """
        config = await self.get_sso_config(organization_id, provider)
        
        if not config:
            raise SSONotConfiguredException()
        
        # Build authorization URL
        if provider == SSOProvider.AZURE_AD:
            return self._build_azure_auth_url(config, redirect_uri)
        elif provider == SSOProvider.GOOGLE:
            return self._build_google_auth_url(config, redirect_uri)
        
        raise SSONotConfiguredException()

    async def handle_callback(
        self,
        provider: SSOProvider,
        code: str,
        state: str,
    ) -> User:
        """
        Handle SSO callback and return authenticated user.
        
        Args:
            provider: SSO provider
            code: Authorization code from callback
            state: State parameter for CSRF protection
            
        Returns:
            Authenticated User
            
        Raises:
            SSOAuthenticationFailedException: Auth failed
            SSOUserNotInvitedException: User not in system
        """
        # Exchange code for tokens (stubbed)
        user_info = await self._exchange_code(provider, code)
        
        if not user_info:
            raise SSOAuthenticationFailedException()
        
        # Find user by email
        email = user_info.get("email", "").lower()
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise SSOUserNotInvitedException()
        
        if not user.is_active:
            raise SSOAuthenticationFailedException()
        
        # Update SSO info
        user.sso_provider = provider
        user.sso_external_id = user_info.get("sub")
        
        return user

    async def configure_sso(
        self,
        organization_id: str,
        provider: SSOProvider,
        client_id: str,
        client_secret: str,
        tenant_id: Optional[str] = None,
        configured_by: Optional[str] = None,
    ) -> SSOConfiguration:
        """
        Configure SSO for an organization.
        
        Args:
            organization_id: Organization to configure
            provider: SSO provider
            client_id: OAuth client ID
            client_secret: OAuth client secret (will be encrypted)
            tenant_id: Azure AD tenant ID (for Azure only)
            configured_by: User ID of configurator
            
        Returns:
            Created/updated SSOConfiguration
        """
        # Check for existing config
        existing = await self.get_sso_config(organization_id, provider)
        
        if existing:
            # Update existing
            existing.client_id = client_id
            existing.client_secret_encrypted = self._encrypt_secret(client_secret)
            existing.tenant_id = tenant_id
            existing.is_active = True
            return existing
        
        # Create new
        config = SSOConfiguration(
            organization_id=organization_id,
            provider=provider,
            client_id=client_id,
            client_secret_encrypted=self._encrypt_secret(client_secret),
            tenant_id=tenant_id,
            configured_by=configured_by,
        )
        
        self.session.add(config)
        await self.session.flush()
        
        return config

    def _build_azure_auth_url(
        self,
        config: SSOConfiguration,
        redirect_uri: str,
    ) -> str:
        """Build Azure AD authorization URL."""
        base_url = f"https://login.microsoftonline.com/{config.tenant_id}/oauth2/v2.0/authorize"
        
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "response_mode": "query",
        }
        
        return f"{base_url}?{urlencode(params)}"

    def _build_google_auth_url(
        self,
        config: SSOConfiguration,
        redirect_uri: str,
    ) -> str:
        """Build Google OAuth authorization URL."""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        params = {
            "client_id": config.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "openid email profile",
            "access_type": "offline",
        }
        
        return f"{base_url}?{urlencode(params)}"

    async def _exchange_code(
        self,
        provider: SSOProvider,
        code: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Exchange authorization code for user info.
        
        NOTE: This is a stub. In production, make actual OAuth token requests.
        """
        # Stub implementation - return mock user info
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[SSO STUB] Would exchange code with {provider.value}")
        
        # In production:
        # 1. Exchange code for access token
        # 2. Use access token to get user info
        # 3. Return user info dict
        
        return None  # SSO not implemented for POC

    def _encrypt_secret(self, secret: str) -> str:
        """
        Encrypt a client secret for storage.
        
        NOTE: In production, use Fernet encryption.
        """
        # Stub - just base64 encode for POC
        import base64
        return base64.b64encode(secret.encode()).decode()

    def _decrypt_secret(self, encrypted: str) -> str:
        """Decrypt a client secret."""
        import base64
        return base64.b64decode(encrypted.encode()).decode()
