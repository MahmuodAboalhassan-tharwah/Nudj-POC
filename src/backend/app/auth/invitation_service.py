"""
Invitation Service

TASK-009: Secure invitation management for registration.

Features:
- Generate secure invitation tokens
- Email sending (placeholder)
- Token validation with expiry check
- Bulk invitation support
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.config import settings
from src.backend.app.auth.models import Invitation, Role
from src.backend.app.auth.exceptions import (
    InvitationNotFoundException,
    InvitationExpiredException,
    InvitationUsedException,
    EmailAlreadyRegisteredException,
)


class InvitationService:
    """
    Invitation management service.
    
    Handles creating, validating, and consuming invitations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.expire_days = settings.INVITATION_EXPIRE_DAYS

    async def create_invitation(
        self,
        email: str,
        role: Role,
        organization_id: Optional[str] = None,
        domain_ids: Optional[List[str]] = None,
        invited_by: Optional[str] = None,
    ) -> Invitation:
        """
        Create a new invitation.
        
        Args:
            email: Invitee's email address
            role: Assigned role for the user
            organization_id: Organization to join (required for non-Super Admin)
            domain_ids: HR domains for assessors
            invited_by: User ID of the inviter
            
        Returns:
            Created Invitation object
            
        Raises:
            EmailAlreadyRegisteredException: If email already registered
        """
        # Check if email already registered
        from src.backend.app.auth.models import User
        
        existing_user = await self.session.execute(
            select(User).where(User.email == email.lower())
        )
        if existing_user.scalar_one_or_none():
            raise EmailAlreadyRegisteredException()
        
        # Invalidate any existing pending invitations for this email
        await self._invalidate_pending_invitations(email)
        
        # Create new invitation
        invitation = Invitation(
            token=self._generate_token(),
            email=email.lower(),
            role=role,
            organization_id=organization_id,
            domain_ids={"ids": domain_ids} if domain_ids else None,
            expires_at=datetime.utcnow() + timedelta(days=self.expire_days),
            invited_by=invited_by,
        )
        
        self.session.add(invitation)
        await self.session.flush()
        
        return invitation

    async def create_bulk_invitations(
        self,
        invitations_data: List[Dict[str, Any]],
        invited_by: str,
    ) -> List[Invitation]:
        """
        Create multiple invitations at once.
        
        Args:
            invitations_data: List of invitation dicts with email, role, etc.
            invited_by: User ID of the inviter
            
        Returns:
            List of created Invitation objects
        """
        created = []
        for data in invitations_data:
            try:
                invitation = await self.create_invitation(
                    email=data["email"],
                    role=Role(data["role"]),
                    organization_id=data.get("organization_id"),
                    domain_ids=data.get("domain_ids"),
                    invited_by=invited_by,
                )
                created.append(invitation)
            except EmailAlreadyRegisteredException:
                # Skip already registered emails in bulk
                continue
        
        return created

    async def validate_invitation(self, token: str) -> Invitation:
        """
        Validate an invitation token.
        
        Args:
            token: The invitation token
            
        Returns:
            Valid Invitation object
            
        Raises:
            InvitationNotFoundException: Token not found
            InvitationExpiredException: Token expired
            InvitationUsedException: Already used
        """
        invitation = await self.session.execute(
            select(Invitation).where(Invitation.token == token)
        )
        invitation = invitation.scalar_one_or_none()
        
        if not invitation:
            raise InvitationNotFoundException()
        
        if invitation.used_at is not None:
            raise InvitationUsedException()
        
        if invitation.expires_at < datetime.utcnow():
            raise InvitationExpiredException()
        
        return invitation

    async def consume_invitation(self, token: str) -> Invitation:
        """
        Mark an invitation as used.
        
        Args:
            token: The invitation token
            
        Returns:
            Updated Invitation object
        """
        invitation = await self.validate_invitation(token)
        invitation.used_at = datetime.utcnow()
        
        return invitation

    async def resend_invitation(
        self,
        invitation_id: str,
        resent_by: str,
    ) -> Invitation:
        """
        Resend an invitation with a new token and expiry.
        
        Args:
            invitation_id: ID of the invitation to resend
            resent_by: User ID of the person resending
            
        Returns:
            Updated Invitation object
        """
        invitation = await self.session.get(Invitation, invitation_id)
        
        if not invitation:
            raise InvitationNotFoundException()
        
        if invitation.used_at is not None:
            raise InvitationUsedException()
        
        # Generate new token and expiry
        invitation.token = self._generate_token()
        invitation.expires_at = datetime.utcnow() + timedelta(days=self.expire_days)
        
        return invitation

    async def get_pending_invitations(
        self,
        organization_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 25,
    ) -> tuple[List[Invitation], int]:
        """
        Get pending invitations for an organization.
        
        Args:
            organization_id: Filter by org (None for all - Super Admin only)
            page: Page number
            page_size: Items per page
            
        Returns:
            Tuple of (invitations, total_count)
        """
        query = select(Invitation).where(
            and_(
                Invitation.used_at.is_(None),
                Invitation.expires_at > datetime.utcnow(),
            )
        )
        
        if organization_id:
            query = query.where(Invitation.organization_id == organization_id)
        
        # Count total
        from sqlalchemy import func
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0
        
        # Get page
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.session.execute(query)
        invitations = result.scalars().all()
        
        return list(invitations), total

    async def _invalidate_pending_invitations(self, email: str) -> None:
        """Expire any pending invitations for an email."""
        result = await self.session.execute(
            select(Invitation).where(
                and_(
                    Invitation.email == email.lower(),
                    Invitation.used_at.is_(None),
                )
            )
        )
        
        for invitation in result.scalars().all():
            invitation.expires_at = datetime.utcnow()

    def _generate_token(self) -> str:
        """Generate a secure URL-safe token."""
        return secrets.token_urlsafe(64)


async def send_invitation_email(
    invitation: Invitation,
    base_url: str,
) -> bool:
    """
    Send invitation email (placeholder implementation).
    
    TODO: Integrate with SendGrid in production.
    
    Args:
        invitation: The invitation to send
        base_url: Application base URL for the registration link
        
    Returns:
        True if email sent successfully
    """
    registration_url = f"{base_url}/register?token={invitation.token}"
    
    # Placeholder - log instead of sending
    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        f"[EMAIL PLACEHOLDER] Invitation sent to {invitation.email}: {registration_url}"
    )
    
    return True
