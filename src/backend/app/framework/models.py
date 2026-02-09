from uuid import UUID, uuid4
from sqlalchemy import String, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.backend.database import Base
from src.backend.app.common.models import TimestampMixin

class FrameworkDomainConfig(Base, TimestampMixin):
    __tablename__ = "framework_domain_configs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    domain_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True) # 1-9
    
    name_en: Mapped[str] = mapped_column(String, nullable=False)
    name_ar: Mapped[str] = mapped_column(String, nullable=False)
    description_en: Mapped[str] = mapped_column(Text, nullable=True)
    description_ar: Mapped[str] = mapped_column(Text, nullable=True)
    
    default_weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
