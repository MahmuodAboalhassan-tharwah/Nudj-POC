"""
MFA Service

TASK-013: Multi-factor authentication with TOTP.

Features:
- TOTP secret generation
- QR code URI generation
- Code verification
- Backup codes
"""
import secrets
import hashlib
from typing import List, Tuple, Optional
from datetime import datetime

import pyotp
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.app.auth.models import User
from src.backend.app.auth.exceptions import (
    MFAInvalidCodeException,
    MFANotEnabledException,
)


class MFAService:
    """
    TOTP-based multi-factor authentication service.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.issuer_name = settings.MFA_ISSUER_NAME

    async def generate_setup(self, user: User) -> dict:
        """
        Generate MFA setup data for a user.
        
        Returns:
            Dict with secret, QR code URI, and backup codes
        """
        # Generate TOTP secret
        secret = pyotp.random_base32()
        
        # Generate provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=self.issuer_name,
        )
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes()
        
        return {
            "secret": secret,
            "qr_code_uri": provisioning_uri,
            "backup_codes": backup_codes,
        }

    async def enable_mfa(
        self,
        user: User,
        secret: str,
        code: str,
    ) -> List[str]:
        """
        Enable MFA for a user after verifying the code.
        
        Args:
            user: User to enable MFA for
            secret: TOTP secret from setup
            code: Verification code from authenticator app
            
        Returns:
            List of backup codes
            
        Raises:
            MFAInvalidCodeException: Code verification failed
        """
        # Verify the code
        if not self._verify_totp(secret, code):
            raise MFAInvalidCodeException()
        
        # Generate backup codes
        backup_codes = self._generate_backup_codes()
        
        # Store encrypted secret (in production, encrypt this)
        user.mfa_secret = secret  # TODO: Encrypt with Fernet
        user.mfa_enabled = True
        
        return backup_codes

    async def verify_code(
        self,
        user: User,
        code: str,
    ) -> bool:
        """
        Verify a TOTP code for a user.
        
        Args:
            user: User to verify for
            code: 6-digit TOTP code
            
        Returns:
            True if code is valid
            
        Raises:
            MFANotEnabledException: MFA not enabled
            MFAInvalidCodeException: Invalid code
        """
        if not user.mfa_enabled or not user.mfa_secret:
            raise MFANotEnabledException()
        
        # Verify TOTP code
        if self._verify_totp(user.mfa_secret, code):
            return True
        
        raise MFAInvalidCodeException()

    async def disable_mfa(
        self,
        user: User,
        code: str,
    ) -> bool:
        """
        Disable MFA for a user.
        
        Args:
            user: User to disable MFA for
            code: Current TOTP code for verification
            
        Returns:
            True if MFA was disabled
        """
        if not user.mfa_enabled:
            raise MFANotEnabledException()
        
        # Verify the code first
        if not self._verify_totp(user.mfa_secret, code):
            raise MFAInvalidCodeException()
        
        user.mfa_enabled = False
        user.mfa_secret = None
        
        return True

    def _verify_totp(self, secret: str, code: str) -> bool:
        """
        Verify a TOTP code.
        
        Allows for 1 step tolerance (30 seconds each way).
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    def _generate_backup_codes(self, count: int = 10) -> List[str]:
        """
        Generate backup codes.
        
        Each code is 8 characters, alphanumeric.
        """
        codes = []
        for _ in range(count):
            # Generate 8-character code in format XXXX-XXXX
            raw = secrets.token_hex(4).upper()
            code = f"{raw[:4]}-{raw[4:]}"
            codes.append(code)
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash a backup code for storage."""
        normalized = code.replace("-", "").upper()
        return hashlib.sha256(normalized.encode()).hexdigest()
