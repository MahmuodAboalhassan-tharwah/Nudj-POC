from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import String, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.database import Base
from src.backend.app.common.models import TimestampMixin

class DelegationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"

class AssessmentDelegation(Base, TimestampMixin):
    __tablename__ = "assessment_delegations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    domain_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_domains.id", ondelete="CASCADE"), nullable=True, index=True) # If null, delegates whole assessment
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True) # Delegatee
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False) # Delegator
    
    status: Mapped[DelegationStatus] = mapped_column(
        SQLEnum(DelegationStatus, name="delegation_status"),
        default=DelegationStatus.ACTIVE,
        index=True
    )
    
    notes: Mapped[str] = mapped_column(String(500), nullable=True)

    # Relationships
    assessment: Mapped["Assessment"] = relationship()
    domain: Mapped["AssessmentDomain"] = relationship()
    delegatee: Mapped["User"] = relationship(foreign_keys=[user_id])
    delegator: Mapped["User"] = relationship(foreign_keys=[created_by])
