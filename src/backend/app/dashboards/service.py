from uuid import UUID
from typing import List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.app.organizations.models import Organization
from src.backend.app.assessments.models import Assessment, AssessmentStatus
from src.backend.app.auth.models import User
from src.backend.app.dashboards.schemas import (
    PortfolioDashboardResponse, PortfolioStats, AssessmentSummary,
    ClientDashboardResponse, OrganizationStats, RecentActivity
)

class DashboardService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_portfolio_dashboard(self) -> PortfolioDashboardResponse:
        # 1. Stats
        # Total Orgs
        org_count = await self.session.scalar(select(func.count(Organization.id)).where(Organization.is_active == True))
        
        # Total Assessments
        assessment_count = await self.session.scalar(select(func.count(Assessment.id)))
        
        # Active vs Completed
        active_count = await self.session.scalar(select(func.count(Assessment.id)).where(Assessment.status != AssessmentStatus.COMPLETED))
        completed_count = await self.session.scalar(select(func.count(Assessment.id)).where(Assessment.status == AssessmentStatus.COMPLETED))
        
        # Avg Score (of completed only? or all with score?)
        avg_score = await self.session.scalar(select(func.avg(Assessment.score)).where(Assessment.score != None)) or 0.0

        # Total Users
        user_count = await self.session.scalar(select(func.count(User.id)))

        stats = PortfolioStats(
            total_organizations=org_count or 0,
            total_users=user_count or 0,
            total_assessments=assessment_count or 0,
            average_maturity_score=round(avg_score, 1),
            active_assessments_count=active_count or 0,
            completed_assessments_count=completed_count or 0
        )

        # 2. Recent Assessments
        query = (
            select(Assessment)
            .order_by(Assessment.updated_at.desc())
            .limit(5)
            .options(selectinload(Assessment.organization_id)) # We don't have a relationship mapped for organization_id in Assessment model yet?
            # Wait, in Assessment model we didn't add the relationship back to organization properly because Org model was created LATER.
            # We need to fix that or fetch org name manually.
            # Let's assume we can join or fetch.
            # For now, let's just fetch orgs separately or assume we fix the model.
        )
        
        # To populate organization_name, we need a join.
        # But let's check Assessment model again.
        # It has organization_id mapped column.
        # We can join with Organization table.
        
        recent_query = (
            select(Assessment, Organization)
            .join(Organization, Assessment.organization_id == Organization.id)
            .order_by(Assessment.updated_at.desc())
            .limit(10)
        )
        recent_result = await self.session.execute(recent_query)
        rows = recent_result.all()
        
        recent_assessments = []
        for assessment, org in rows:
            recent_assessments.append(AssessmentSummary(
                id=assessment.id,
                organization_name=org.name_en, # or name_ar depending on locale? let's default to EN for API
                status=assessment.status,
                score=assessment.score,
                deadline=assessment.deadline,
                updated_at=assessment.updated_at
            ))

        return PortfolioDashboardResponse(
            stats=stats,
            recent_assessments=recent_assessments
        )

    async def get_client_dashboard(self, organization_id: UUID) -> ClientDashboardResponse:
        # 1. Stats
        total = await self.session.scalar(
            select(func.count(Assessment.id)).where(Assessment.organization_id == organization_id)
        )
        active = await self.session.scalar(
             select(func.count(Assessment.id))
             .where(Assessment.organization_id == organization_id, Assessment.status != AssessmentStatus.COMPLETED)
        )
        completed = await self.session.scalar(
             select(func.count(Assessment.id))
             .where(Assessment.organization_id == organization_id, Assessment.status == AssessmentStatus.COMPLETED)
        )
        avg_score = await self.session.scalar(
             select(func.avg(Assessment.score))
             .where(Assessment.organization_id == organization_id, Assessment.score != None)
        ) or 0.0

        # Next deadline
        next_deadline = await self.session.scalar(
            select(func.min(Assessment.deadline))
            .where(
                Assessment.organization_id == organization_id, 
                Assessment.status != AssessmentStatus.COMPLETED,
                Assessment.deadline >= func.now()
            )
        )

        stats = OrganizationStats(
            total_assessments=total or 0,
            active_assessments=active or 0,
            completed_assessments=completed or 0,
            average_score=round(avg_score, 1),
            next_deadline=next_deadline
        )

        # 2. Active Assessments list
        assessments_query = (
             select(Assessment)
             .where(Assessment.organization_id == organization_id, Assessment.status != AssessmentStatus.COMPLETED)
             .order_by(Assessment.deadline.asc())
             .limit(5)
        )
        assessments_result = await self.session.execute(assessments_query)
        assessments = assessments_result.scalars().all()
        
        # We need organization name for the summary, even if it's the same org.
        # Efficiently we can just query the org once.
        org = await self.session.get(Organization, organization_id)
        org_name = org.name_en if org else "Unknown"

        active_assessments = [
            AssessmentSummary(
                id=a.id,
                organization_name=org_name,
                status=a.status,
                score=a.score,
                deadline=a.deadline,
                updated_at=a.updated_at
            ) for a in assessments
        ]

        # 3. Recent Activity (Mocked for now as we don't have an Audit Log / Activity table explicitly for this view yet)
        # We can implement a real Activity Log later.
        recent_activity = [] # Empty for now

        return ClientDashboardResponse(
            stats=stats,
            active_assessments=active_assessments,
            recent_activity=recent_activity
        )
