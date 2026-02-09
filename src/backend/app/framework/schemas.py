from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class FrameworkDomainConfigBase(BaseModel):
    name_en: str
    name_ar: str
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    default_weight: float

class FrameworkDomainConfigUpdate(BaseModel):
    name_en: Optional[str] = None
    name_ar: Optional[str] = None
    description_en: Optional[str] = None
    description_ar: Optional[str] = None
    default_weight: Optional[float] = None

class FrameworkDomainConfigResponse(FrameworkDomainConfigBase):
    id: UUID
    domain_id: int

    class Config:
        from_attributes = True
