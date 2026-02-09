from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.backend.app.assessments.models import AssessmentStatus

class EvidenceResponse(BaseModel):
    id: UUID
    file_name: str
    file_url: str
    mime_type: Optional[str]
    size_bytes: Optional[int]
    uploaded_by: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AssessmentElementResponseSchema(BaseModel):
    id: UUID
    domain_record_id: UUID
    element_id: int
    maturity_level: Optional[int]
    score: Optional[float]
    comment: Optional[str]
    evidence: List[EvidenceResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class AssessmentElementUpdate(BaseModel):
    maturity_level: int
    comment: Optional[str] = None

class AssessmentDomainResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    domain_id: int
    weight: float
    score: Optional[float]
    status: str
    assignee_id: Optional[UUID]
    elements: List[AssessmentElementResponseSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

class AssessmentDomainUpdate(BaseModel):
    assignee_id: Optional[UUID]

class AssessmentCreate(BaseModel):
    organization_id: UUID
    deadline: Optional[datetime] = None
    domain_ids: Optional[List[int]] = None # Optional subset

class AssessmentUpdate(BaseModel):
    deadline: Optional[datetime] = None
    status: Optional[AssessmentStatus] = None

class AssessmentResponse(BaseModel):
    id: UUID
    organization_id: UUID
    status: AssessmentStatus
    score: Optional[float]
    deadline: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    domains: List[AssessmentDomainResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
