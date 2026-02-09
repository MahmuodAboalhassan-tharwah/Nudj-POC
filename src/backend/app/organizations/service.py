from uuid import UUID
from typing import List, Optional
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.backend.app.organizations.models import Organization
from src.backend.app.organizations.schemas import OrganizationCreate, OrganizationUpdate

class OrganizationNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")

class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_organization(self, data: OrganizationCreate) -> Organization:
        org = Organization(**data.model_dump())
        self.session.add(org)
        await self.session.commit()
        await self.session.refresh(org)
        return org

    async def get_organization(self, org_id: UUID) -> Organization:
        query = select(Organization).where(Organization.id == org_id)
        result = await self.session.execute(query)
        org = result.scalars().first()
        if not org:
            raise OrganizationNotFound()
        return org

    async def update_organization(self, org_id: UUID, data: OrganizationUpdate) -> Organization:
        org = await self.get_organization(org_id)
        
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(org, key, value)
            
        await self.session.commit()
        await self.session.refresh(org)
        return org

    async def delete_organization(self, org_id: UUID) -> None:
        # Soft delete
        org = await self.get_organization(org_id)
        org.is_active = False
        await self.session.commit()

    async def list_organizations(self, skip: int = 0, limit: int = 20) -> List[Organization]:
        query = select(Organization).where(Organization.is_active == True).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
