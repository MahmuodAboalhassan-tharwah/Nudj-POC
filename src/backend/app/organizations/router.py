from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.app.auth.services import get_current_user
from src.backend.app.auth.models import User, Role
from src.backend.app.organizations.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from src.backend.app.organizations.service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.post("/", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = OrganizationService(db)
    return await service.create_organization(data)

@router.get("/", response_model=List[OrganizationResponse])
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only Super Admin can list all. Client Admins might see their own via a different endpoint or context?
    # For now, restrict list to Super Admin
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = OrganizationService(db)
    return await service.list_organizations(skip, limit)

@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Super Admin or Client Admin of THAT org
    if current_user.role != Role.SUPER_ADMIN and (
        current_user.organization_id != str(org_id)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    service = OrganizationService(db)
    return await service.get_organization(org_id)

@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: UUID,
    data: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != Role.SUPER_ADMIN and (
        current_user.role != Role.CLIENT_ADMIN or current_user.organization_id != str(org_id)
    ):
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = OrganizationService(db)
    return await service.update_organization(org_id, data)

@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = OrganizationService(db)
    await service.delete_organization(org_id)
