from datetime import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# --- Shared Components ---

class AssessmentSummary(BaseModel):
    id: UUID
    organization_name: str
    status: str
    score: Optional[float]
    deadline: Optional[datetime]
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RecentActivity(BaseModel):
    id: UUID
    type: str # "assessment_created", "assessment_completed", "evidence_uploaded"
    description: str
    timestamp: datetime
    user_name: str

# --- Super Admin Portfolio ---

class PortfolioStats(BaseModel):
    total_organizations: int
    total_users: int
    total_assessments: int
    average_maturity_score: float
    active_assessments_count: int
    completed_assessments_count: int

class PortfolioDashboardResponse(BaseModel):
    stats: PortfolioStats
    recent_assessments: List[AssessmentSummary]
    # potential for charts: assessments_by_status, top_performing_orgs, etc.

# --- Client Admin Dashboard ---

class OrganizationStats(BaseModel):
    total_assessments: int
    active_assessments: int
    completed_assessments: int
    average_score: float
    next_deadline: Optional[datetime]

class ClientDashboardResponse(BaseModel):
    stats: OrganizationStats
    active_assessments: List[AssessmentSummary]
    recent_activity: List[RecentActivity]
