"""
Nudj Common Models

TASK-002: Audit log model and common base classes.

Provides:
- TimestampMixin for created_at/updated_at
- AuditEventType enum for all auth events
- AuditLog model (append-only)
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.database import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class AuditEventType(str, enum.Enum):
    """All auditable authentication and authorization events."""
    
    # Login events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    
    # Password events
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET_REQUESTED = "password_reset_requested"
    PASSWORD_RESET_COMPLETED = "password_reset_completed"
    
    # MFA events
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFIED = "mfa_verified"
    MFA_FAILED = "mfa_failed"
    
    # User management events
    USER_REGISTERED = "user_registered"
    ROLE_CHANGED = "role_changed"
    USER_DEACTIVATED = "user_deactivated"
    USER_REACTIVATED = "user_reactivated"
    
    # Invitation events
    INVITATION_SENT = "invitation_sent"
    INVITATION_ACCEPTED = "invitation_accepted"
    INVITATION_EXPIRED = "invitation_expired"
    INVITATION_RESENT = "invitation_resent"
    
    # Session events
    SESSION_CREATED = "session_created"
    SESSION_EXPIRED = "session_expired"
    SESSION_REVOKED = "session_revoked"
    
    # Security events
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    
    # PDPL compliance events
    DATA_EXPORT_REQUESTED = "data_export_requested"
    DATA_EXPORT_COMPLETED = "data_export_completed"
    DATA_DELETION_REQUESTED = "data_deletion_requested"
    DATA_DELETION_COMPLETED = "data_deletion_completed"
    
    # SSO events
    SSO_LOGIN_INITIATED = "sso_login_initiated"
    SSO_LOGIN_SUCCESS = "sso_login_success"
    SSO_LOGIN_FAILED = "sso_login_failed"
    SSO_CONFIGURED = "sso_configured"


class AuditLog(Base):
    """
    Append-only audit log for authentication events.
    
    IMPORTANT:
    - This table is append-only by design
    - No UPDATE or DELETE operations allowed
    - 5-year retention policy
    - Partitioned by month for performance (handled at DB level)
    """
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    # Event type
    event_type: Mapped[AuditEventType] = mapped_column(
        Enum(AuditEventType),
        nullable=False,
        index=True,
    )

    # Actor (may be null for failed login attempts with unknown email)
    user_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Request context
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)  # IPv6 max
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Event details (flexible JSONB for event-specific data)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Tenant context
    organization_id: Mapped[Optional[str]] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamp (no updated_at since append-only)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        index=True,
    )

    __table_args__ = (
        # Composite indexes for common queries
        Index("ix_audit_event_created", "event_type", "created_at"),
        Index("ix_audit_org_created", "organization_id", "created_at"),
        Index("ix_audit_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.event_type.value} at {self.created_at}>"
