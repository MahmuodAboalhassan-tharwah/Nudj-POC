from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel

# Reusing/extending Assessment shapes for reporting
# We need a flat structure that is easy to pass to the template context

class ReportElement(BaseModel):
    name: str # e.g. "Workforce Planning"
    maturity_level: int # 1-4
    score: float # 0.0, 33.3, 66.7, 100.0
    comment: Optional[str]

class ReportDomain(BaseModel):
    name: str
    weight: float
    score: float
    elements: List[ReportElement]

class AssessmentReportData(BaseModel):
    # Assessment Info
    assessment_id: UUID
    status: str
    deadline: Optional[datetime]
    completed_at: Optional[datetime]
    overall_score: float
    
    # Organization Info
    organization_name_en: str
    organization_name_ar: str
    sector: str
    size: str
    region: str
    
    # Detail
    domains: List[ReportDomain]
