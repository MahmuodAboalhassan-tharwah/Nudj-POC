from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from src.backend.app.delegations.models import DelegationStatus

class DelegationBase(BaseModel):
    assessment_id: UUID
    domain_id: Optional[UUID] = None
    user_id: UUID
    notes: Optional[str] = None

class DelegationCreate(DelegationBase):
    pass

class DelegationResponse(DelegationBase):
    id: UUID
    created_by: UUID
    status: DelegationStatus
    created_at: datetime
    updated_at: Optional[datetime]
    
    delegatee_name: Optional[str] = None
    delegator_name: Optional[str] = None
    domain_name: Optional[str] = None

    class Config:
        from_attributes = True
