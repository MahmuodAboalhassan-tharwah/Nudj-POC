from datetime import datetime
from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.app.assessments.models import (
    Assessment, AssessmentDomain, AssessmentElementResponse, AssessmentStatus, Evidence
)
from src.backend.app.delegations.models import AssessmentDelegation, DelegationStatus
from src.backend.app.auth.models import Role
from src.backend.app.assessments.schemas import (
    AssessmentCreate, AssessmentUpdate, AssessmentDomainUpdate, AssessmentElementUpdate
)
from src.backend.app.assessments.exceptions import (
    AssessmentNotFound, DomainNotFound, ElementResponseNotFound
)
# We will inject ScoringService later or use it here
# from src.backend.app.assessments.scoring import ScoringService
from src.backend.app.framework.service import FrameworkService

HR_DOMAINS = [1, 2, 3, 4, 5, 6, 7, 8, 9] # IDs of the 9 domains
ELEMENTS_PER_DOMAIN = {
    1: [1, 2, 3], # Placeholder structure, normally this would come from a config or DB
    2: [4, 5, 6],
    # ... assuming 3-5 elements per domain for now. 
    # In a real app, we'd query the 'Framework' tables or config. 
    # For POC, let's assume 3 elements per domain: ID = (domain_id * 10) + k
}

class AssessmentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_access(self, user_id: UUID, role: Role, assessment_id: UUID, domain_id: Optional[UUID] = None) -> bool:
        # Super Admin and Analyst have global/org-wide read/write usually
        if role in [Role.SUPER_ADMIN, Role.ANALYST]:
            return True
            
        # Check if user is creator of assessment
        stmt = select(Assessment).where(Assessment.id == assessment_id)
        result = await self.session.execute(stmt)
        assessment = result.scalar_one_or_none()
        if not assessment:
            return False
            
        if assessment.created_by == user_id:
            return True

        # Check for delegations
        delegation_stmt = select(AssessmentDelegation).where(
            AssessmentDelegation.assessment_id == assessment_id,
            AssessmentDelegation.user_id == user_id,
            AssessmentDelegation.status == DelegationStatus.ACTIVE
        )
        
        # If a specific domain is requested, check if delegated to that domain OR whole assessment
        if domain_id:
             delegation_stmt = delegation_stmt.where(
                 (AssessmentDelegation.domain_id == domain_id) | (AssessmentDelegation.domain_id == None)
             )
        
        delegation_result = await self.session.execute(delegation_stmt)
        if delegation_result.scalar_one_or_none():
            return True
            
        return False

    async def create_assessment(self, data: AssessmentCreate, user_id: UUID) -> Assessment:
        # Create Assessment
        assessment = Assessment(
            organization_id=data.organization_id,
            deadline=data.deadline,
            created_by=user_id,
            status=AssessmentStatus.DRAFT
        )
        self.session.add(assessment)
        await self.session.flush() # Get ID

        # Create Domains
        domains_to_create = data.domain_ids if data.domain_ids else HR_DOMAINS
        
        # Get domain configs for weights
        framework_service = FrameworkService(self.session)
        domain_configs = await framework_service.get_all_configs()
        config_map = {c.domain_id: c for c in domain_configs}
        
        for domain_id in domains_to_create:
            config = config_map.get(domain_id)
            weight = config.default_weight if config else 1.0

            domain = AssessmentDomain(
                assessment_id=assessment.id,
                domain_id=domain_id,
                weight=weight,
                status="PENDING"
            )
            self.session.add(domain)
            await self.session.flush()
            
            # Create Element Responses (empty)
            # Mocking elements: 3 per domain
            for i in range(1, 4):
                element_id = domain_id * 100 + i # e.g. Domain 1 -> 101, 102, 103
                response = AssessmentElementResponse(
                    domain_record_id=domain.id,
                    element_id=element_id
                )
                self.session.add(response)

        await self.session.commit()
        return await self.get_assessment(assessment.id)

    async def get_assessment(self, assessment_id: UUID) -> Assessment:
        result = await self.session.execute(
            select(Assessment)
            .options(
                selectinload(Assessment.domains).selectinload(AssessmentDomain.elements).selectinload(AssessmentElementResponse.evidence),
                selectinload(Assessment.domains).selectinload(AssessmentDomain.assignee)
            )
            .where(Assessment.id == assessment_id)
        )
        assessment = result.scalars().first()
        if not assessment:
            raise AssessmentNotFound()
        return assessment

    async def list_assessments(self, organization_id: UUID, skip: int = 0, limit: int = 20) -> List[Assessment]:
        result = await self.session.execute(
            select(Assessment)
            .where(Assessment.organization_id == organization_id)
            .offset(skip).limit(limit)
            .order_by(Assessment.created_at.desc())
        )
        return result.scalars().all()

    async def update_assessment(self, assessment_id: UUID, data: AssessmentUpdate) -> Assessment:
        assessment = await self.get_assessment(assessment_id)
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(assessment, key, value)
        await self.session.commit()
        await self.session.refresh(assessment)
        return assessment

    async def update_domain_assignee(self, assessment_id: UUID, domain_id: UUID, assignee_id: UUID) -> AssessmentDomain:
        # Check if domain exists
        result = await self.session.execute(
            select(AssessmentDomain)
            .where(AssessmentDomain.id == domain_id, AssessmentDomain.assessment_id == assessment_id)
        )
        domain = result.scalars().first()
        if not domain:
            raise DomainNotFound()
            
        domain.assignee_id = assignee_id
        await self.session.commit()
        await self.session.refresh(domain)
        return domain

    async def update_element_response(self, response_id: UUID, data: AssessmentElementUpdate, user_id: UUID, user_role: Role) -> AssessmentElementResponse:
        stmt = select(AssessmentElementResponse).options(
            selectinload(AssessmentElementResponse.domain)
        ).where(AssessmentElementResponse.id == response_id)
        
        result = await self.session.execute(stmt)
        response = result.scalars().first()
        if not response:
            raise ElementResponseNotFound()
        
        # Check access
        if not await self.check_access(user_id, user_role, response.domain.assessment_id, response.domain_record_id):
            raise AssessmentNotFound() # or a custom Forbidden error
            
        response.maturity_level = data.maturity_level
        response.comment = data.comment
        # Basic scoring logic stub - usually ScoringService handles this
        # level 1=0, 2=33, 3=67, 4=100 ? Or 0, 25, 50, 75, 100?
        # Let's assume standard maturity 1-4: 1=25%, 2=50%, 3=75%, 4=100% or similar. 
        # For now, just setting score = level * 25.
        if data.maturity_level:
            response.score = data.maturity_level * 25.0 
            
        await self.session.commit()
        await self.session.refresh(response)
        return response
