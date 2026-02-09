from __future__ import annotations
from uuid import uuid4
from datetime import datetime
from typing import Optional, List
import enum

from sqlalchemy import String, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.database import Base
from src.backend.app.common.models import TimestampMixin

class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name_ar: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[str] = mapped_column(String(255), nullable=False)
    cr_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Classification
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g., ISIC code or name
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True) # e.g., "Small", "Medium", "Enterprise"
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True) # e.g., "Riyadh", "Makkah"
    
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships can be added here if needed, or in the other models
    # users: Mapped[List["User"]] = relationship(back_populates="organization")
    # assessments: Mapped[List["Assessment"]] = relationship(back_populates="organization") 
