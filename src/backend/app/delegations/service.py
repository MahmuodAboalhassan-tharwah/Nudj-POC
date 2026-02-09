from uuid import UUID
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.backend.app.delegations.models import AssessmentDelegation, DelegationStatus
from src.backend.app.delegations.schemas import DelegationCreate
from src.backend.app.notifications.service import NotificationService
from src.backend.app.notifications.schemas import NotificationCreate
from src.backend.app.notifications.models import NotificationType
from src.backend.app.assessments.models import Assessment, AssessmentDomain

class DelegationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_delegation(self, creator_id: UUID, data: DelegationCreate) -> AssessmentDelegation:
        delegation = AssessmentDelegation(
            assessment_id=data.assessment_id,
            domain_id=data.domain_id,
            user_id=data.user_id,
            created_by=creator_id,
            notes=data.notes,
            status=DelegationStatus.ACTIVE
        )
        self.session.add(delegation)
        await self.session.commit()
        await self.session.refresh(delegation)

        # Notify the delegatee
        await self._notify_delegatee(delegation)

        return delegation

    async def _notify_delegatee(self, delegation: AssessmentDelegation):
        # Fetch some details for the notification
        stmt = select(Assessment).where(Assessment.id == delegation.assessment_id)
        result = await self.session.execute(stmt)
        assessment = result.scalar_one()

        title = "New Assessment Task Delegated"
        domain_str = "the whole assessment"
        if delegation.domain_id:
             d_stmt = select(AssessmentDomain).where(AssessmentDomain.id == delegation.domain_id)
             d_result = await self.session.execute(d_stmt)
             domain = d_result.scalar_one_or_none()
             if domain:
                 domain_str = f"Domain {domain.domain_id}"

        message = f"You have been assigned to {domain_str} for assessment {assessment.id}."
        
        notification_service = NotificationService(self.session)
        await notification_service.create_notification(NotificationCreate(
            user_id=delegation.user_id,
            title=title,
            message=message,
            type=NotificationType.ACTION,
            link=f"/assessments/{assessment.id}"
        ))

    async def revoke_delegation(self, delegation_id: UUID, revoker_id: UUID) -> bool:
        stmt = select(AssessmentDelegation).where(AssessmentDelegation.id == delegation_id)
        result = await self.session.execute(stmt)
        delegation = result.scalar_one_or_none()
        
        if not delegation:
            return False
            
        # Optional: check if revoker has permission (e.g. is creator or admin)
        delegation.status = DelegationStatus.REVOKED
        await self.session.commit()
        return True

    async def get_assessment_delegations(self, assessment_id: UUID) -> List[AssessmentDelegation]:
        stmt = select(AssessmentDelegation).where(
            AssessmentDelegation.assessment_id == assessment_id,
            AssessmentDelegation.status == DelegationStatus.ACTIVE
        ).options(
            selectinload(AssessmentDelegation.delegatee),
            selectinload(AssessmentDelegation.delegator)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_user_delegations(self, user_id: UUID) -> List[AssessmentDelegation]:
        stmt = select(AssessmentDelegation).where(
            AssessmentDelegation.user_id == user_id,
            AssessmentDelegation.status == DelegationStatus.ACTIVE
        ).options(
            selectinload(AssessmentDelegation.assessment)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
