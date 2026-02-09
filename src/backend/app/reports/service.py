from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.backend.app.assessments.models import Assessment, AssessmentDomain, AssessmentElementResponse, AssessmentStatus
from src.backend.app.organizations.models import Organization
from src.backend.app.reports.schemas import AssessmentReportData, ReportDomain, ReportElement

class ReportingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_assessment_metadata(self, assessment_id: UUID) -> Optional[Assessment]:
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_assessment_report_data(self, assessment_id: UUID) -> AssessmentReportData:
        # Fetch Assessment with all related data
        query = (
            select(Assessment)
            .where(Assessment.id == assessment_id)
            .options(
                selectinload(Assessment.domains).selectinload(AssessmentDomain.element_responses)
            )
        )
        result = await self.session.execute(query)
        assessment = result.scalar_one_or_none()

        if not assessment:
            raise ValueError(f"Assessment {assessment_id} not found")

        # Fetch Organization separately since relationship might not be fully established/loaded
        org_query = select(Organization).where(Organization.id == assessment.organization_id)
        org_result = await self.session.execute(org_query)
        org = org_result.scalar_one_or_none()
        
        if not org:
             # Fallback if org logic is mocked or missing
             org_name_en = "Unknown Organization"
             org_name_ar = "منظمة غير معروفة"
             sector = "N/A"
             size = "N/A"
             region = "N/A"
        else:
             org_name_en = org.name_en
             org_name_ar = org.name_ar
             sector = org.sector
             size = org.size
             region = org.region

        # Transform to Report Data Structure
        report_domains = []
        
        # Sort domains by some logic? For now insertion order or ID
        sorted_domains = sorted(assessment.domains, key=lambda d: d.domain_id) # assuming domain_id maps to 1-9
        
        for domain in sorted_domains:
            elements = []
            for resp in domain.element_responses:
                # We need element name. In POC, this might be hardcoded in the FE or Service.
                # For the report we might need a lookup map if it's not in DB.
                # Let's use a placeholder name or ID for now if we don't have a content table.
                # In real app, we'd query the Content/Question table.
                element_name = f"Element {resp.element_id}" 
                
                elements.append(ReportElement(
                    name=element_name,
                    maturity_level=resp.maturity_level,
                    score=resp.score,
                    comment=resp.comment
                ))
            
            report_domains.append(ReportDomain(
                name=f"Domain {domain.domain_id}", # Again, need name mapping
                weight=0.0, # Need to fetch weight from config or domain model
                score=domain.score,
                elements=elements
            ))

        return AssessmentReportData(
            assessment_id=assessment.id,
            status=assessment.status,
            deadline=assessment.deadline,
            completed_at=assessment.updated_at if assessment.status == AssessmentStatus.COMPLETED else None,
            overall_score=assessment.score or 0.0,
            organization_name_en=org_name_en,
            organization_name_ar=org_name_ar,
            sector=sector,
            size=size,
            region=region,
            domains=report_domains
        )
