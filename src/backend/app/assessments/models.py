from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import String, ForeignKey, Float, Enum as SQLEnum, Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from src.backend.database import Base
from src.backend.app.common.models import TimestampMixin

class AssessmentStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"

class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id"), nullable=False, index=True) # Assuming org table exists or uses users.organization_id logic? 
    # Wait, in the Auth feature, we didn't explicitly create an Organizations table, we just had organization_id on User. 
    # For now, I will treat organization_id as a UUID. Ideally, there should be an organizations table.
    # In TASK-001 (Auth), organization_id was on User. Let's assume there is NO foreign key constraint to an 'organizations' table yet if it wasn't created in Phase 1. 
    # However, PROJECT_CONTEXT mentions "Organization management". 
    # Let me check if 'organizations' table exists. If not, I'll just index it without FK for now or assume it will be created.
    # actually, looking at the previous conversation, I don't see an organizations table created. 
    # I will proceed without FK for organization_id for now, just index.
    
    status: Mapped[AssessmentStatus] = mapped_column(
        SQLEnum(AssessmentStatus, name="assessment_status"), 
        default=AssessmentStatus.DRAFT, 
        index=True
    )
    score: Mapped[float] = mapped_column(Float, nullable=True) # Overall score
    deadline: Mapped[datetime] = mapped_column(nullable=True)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    domains: Mapped[list["AssessmentDomain"]] = relationship(
        back_populates="assessment", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class AssessmentDomain(Base, TimestampMixin):
    __tablename__ = "assessment_domains"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True) # Using int ID for domains might be easier, or UUID. Let's stick to UUID for consistency or Auto-increment if high volume. 
    # Actually, domains are unique per assessment. ID should probably be UUID to avoid enumeration or just int. UUID is safer for distributed.
    # Let's use UUID.
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    
    assessment_id: Mapped[UUID] = mapped_column(ForeignKey("assessments.id"), nullable=False, index=True)
    domain_id: Mapped[int] = mapped_column(Integer, nullable=False) # 1-9 corresponding to framework
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, default="PENDING") # PENDING, IN_PROGRESS, COMPLETED
    assignee_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    
    # Relationships
    assessment: Mapped["Assessment"] = relationship(back_populates="domains")
    elements: Mapped[list["AssessmentElementResponse"]] = relationship(
        back_populates="domain", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    assignee: Mapped["User"] = relationship() # We need to import User or use string "User" if circular. User is in auth.models.

class AssessmentElementResponse(Base, TimestampMixin):
    __tablename__ = "assessment_element_responses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    domain_record_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_domains.id"), nullable=False, index=True)
    
    element_id: Mapped[int] = mapped_column(Integer, nullable=False) # ID from the framework
    maturity_level: Mapped[int] = mapped_column(Integer, nullable=True) # 1-4
    score: Mapped[float] = mapped_column(Float, nullable=True) # 0, 33, 67, 100
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Relationships
    domain: Mapped["AssessmentDomain"] = relationship(back_populates="elements")
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="response", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="response",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

class Evidence(Base, TimestampMixin):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    response_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_element_responses.id"), nullable=False, index=True)
    
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=False) # S3 key or URL
    mime_type: Mapped[str] = mapped_column(String, nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    uploaded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    response: Mapped["AssessmentElementResponse"] = relationship(back_populates="evidence")

