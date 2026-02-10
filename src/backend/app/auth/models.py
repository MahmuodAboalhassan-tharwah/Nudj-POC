"""
Nudj Auth Module - SQLAlchemy 2.0 Models

TASK-001: Create auth SQLAlchemy models and Alembic migration

Models:
- User: Core user entity with role, MFA, SSO support
- Invitation: Secure invitation tokens for registration
- RefreshToken: JWT refresh token tracking
- PasswordResetToken: Password reset flow tokens
- UserSession: Active session tracking
- UserDomainAssignment: Assessor domain access
- AnalystOrgAssignment: Analyst organization access
- SSOConfiguration: Per-org SSO settings
- DataDeletionRequest: PDPL compliance requests
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Integer,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.database import Base


# ============================================================================
# Enums
# ============================================================================

class Role(str, enum.Enum):
    """User roles in hierarchical order (highest to lowest)."""
    SUPER_ADMIN = "super_admin"
    ANALYST = "analyst"
    CLIENT_ADMIN = "client_admin"
    ASSESSOR = "assessor"


class SSOProvider(str, enum.Enum):
    """Supported SSO providers."""
    AZURE_AD = "azure_ad"
    GOOGLE = "google"


class DeletionStatus(str, enum.Enum):
    """Data deletion request status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"


# ============================================================================
# Mixins
# ============================================================================

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=True,
    )


# ============================================================================
# Models
# ============================================================================

class User(TimestampMixin, Base):
    """
    Core user entity.
    
    Supports:
    - Local authentication (email/password)
    - SSO authentication (Azure AD, Google)
    - MFA via TOTP
    - Account lockout after failed attempts
    - Soft delete via is_active flag
    """
    __tablename__ = "users"

    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Identity
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Nullable for SSO-only users
    name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_sa: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Role & Organization
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, index=True)
    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # MFA
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Encrypted TOTP secret

    # SSO
    sso_provider: Mapped[Optional[SSOProvider]] = mapped_column(Enum(SSOProvider), nullable=True)
    sso_external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Security
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Invitation reference
    created_by_invitation_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("invitations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[List["UserSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    domain_assignments: Mapped[List["UserDomainAssignment"]] = relationship(
        back_populates="user",
        foreign_keys="UserDomainAssignment.user_id",
    )
    analyst_assignments: Mapped[List["AnalystOrgAssignment"]] = relationship(
        back_populates="analyst",
        foreign_keys="AnalystOrgAssignment.user_id",
    )

    # Indexes
    __table_args__ = (
        Index("ix_users_org_role", "organization_id", "role"),
        Index("ix_users_sso", "sso_provider", "sso_external_id"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role.value})>"


class Invitation(TimestampMixin, Base):
    """
    Secure invitation for user registration.
    
    - Token valid for 7 days
    - Single use (marked used_at when accepted)
    - Pre-assigns role, organization, and domains
    """
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Invitation token (URL-safe random string)
    token: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    
    # Invitee details
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[Role] = mapped_column(Enum(Role), nullable=False)
    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )
    
    # Domain access for assessors (JSONB array of domain IDs)
    domain_ids: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Lifecycle
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Audit
    invited_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    @property
    def is_expired(self) -> bool:
        """Check if invitation has expired."""
        return datetime.utcnow() > self.expires_at

    @property
    def is_used(self) -> bool:
        """Check if invitation has been used."""
        return self.used_at is not None

    def __repr__(self) -> str:
        return f"<Invitation {self.email} ({self.role.value})>"


class RefreshToken(TimestampMixin, Base):
    """
    JWT refresh token tracking for token rotation.
    
    - Stores hash of token (not the token itself)
    - Tracks device info for security
    - Revocable individually or all at once
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Owner
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token (stored as hash)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Lifecycle
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Device info for security
    device_info: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 max length

    # Relationship
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

    def __repr__(self) -> str:
        return f"<RefreshToken user={self.user_id}>"


class PasswordResetToken(TimestampMixin, Base):
    """
    Password reset flow token.
    
    - Single use
    - 1-hour expiry
    - Stored as hash
    """
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Owner
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Token (stored as hash)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Lifecycle
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<PasswordResetToken user={self.user_id}>"


class UserSession(TimestampMixin, Base):
    """
    Active user session tracking.
    
    - Tracks last activity for timeout
    - Stores device info for security
    - Redis used for real-time activity, DB for persistence
    """
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Owner
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Session token (stored as hash)
    session_token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Device info
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Activity tracking
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationship
    user: Mapped["User"] = relationship(back_populates="sessions")

    def __repr__(self) -> str:
        return f"<UserSession user={self.user_id}>"


class UserDomainAssignment(Base):
    """
    Assessor domain access assignment.
    
    - Links assessor to specific HR domains within an assessment
    - Assigned by Client Admin
    """
    __tablename__ = "user_domain_assignments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Assessor
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Assessment (optional - could be org-wide)
    assessment_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Assigned domains (JSONB array of domain IDs)
    domain_ids: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Audit
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    assigned_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        back_populates="domain_assignments",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        UniqueConstraint("user_id", "assessment_id", name="uq_user_assessment_domain"),
    )

    def __repr__(self) -> str:
        return f"<UserDomainAssignment user={self.user_id} domains={self.domain_ids}>"


class AnalystOrgAssignment(Base):
    """
    Analyst organization access assignment.
    
    - Links analyst to specific client organizations
    - Assigned by Super Admin
    """
    __tablename__ = "analyst_org_assignments"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Analyst
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Organization
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Audit
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    assigned_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationship
    analyst: Mapped["User"] = relationship(
        back_populates="analyst_assignments",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_analyst_org"),
    )

    def __repr__(self) -> str:
        return f"<AnalystOrgAssignment analyst={self.user_id} org={self.organization_id}>"


class SSOConfiguration(TimestampMixin, Base):
    """
    Per-organization SSO configuration.
    
    - Configured by Super Admin
    - Supports Azure AD and Google Workspace
    - Client secret stored encrypted
    """
    __tablename__ = "sso_configurations"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Organization
    organization_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Provider config
    provider: Mapped[SSOProvider] = mapped_column(Enum(SSOProvider), nullable=False)
    tenant_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Azure AD tenant
    client_id: Mapped[str] = mapped_column(String(255), nullable=False)
    client_secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Audit
    configured_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "provider", name="uq_org_sso_provider"),
    )

    def __repr__(self) -> str:
        return f"<SSOConfiguration org={self.organization_id} provider={self.provider.value}>"


class DataDeletionRequest(TimestampMixin, Base):
    """
    PDPL compliance - user data deletion request.
    
    - 30-day processing window
    - PII anonymized, assessment data preserved for benchmarks
    """
    __tablename__ = "data_deletion_requests"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # User requesting deletion
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Lifecycle
    requested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Processing
    status: Mapped[DeletionStatus] = mapped_column(
        Enum(DeletionStatus),
        default=DeletionStatus.PENDING,
        nullable=False,
    )
    processed_by: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<DataDeletionRequest user={self.user_id} status={self.status.value}>"
