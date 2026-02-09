from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class OrganizationBase(BaseModel):
    name_ar: str
    name_en: str
    cr_number: Optional[str] = None
    sector: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name_ar: Optional[str] = None
    name_en: Optional[str] = None
    cr_number: Optional[str] = None
    sector: Optional[str] = None
    size: Optional[str] = None
    region: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None

class OrganizationResponse(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
