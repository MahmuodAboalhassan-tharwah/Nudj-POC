from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User, Role
from src.backend.app.delegations.service import DelegationService
from src.backend.app.delegations.schemas import DelegationCreate, DelegationResponse

router = APIRouter(prefix="/delegations", tags=["delegations"])

@router.post("/", response_model=DelegationResponse, status_code=status.HTTP_201_CREATED)
async def create_delegation(
    data: DelegationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only Client Admins or Super Admins can delegate usually. 
    # For now, let's allow Client Admin to delegate within their org.
    if current_user.role not in [Role.CLIENT_ADMIN, Role.SUPER_ADMIN]:
        raise HTTPException(status_code=403, detail="Permission denied")
        
    service = DelegationService(db)
    return await service.create_delegation(current_user.id, data)

@router.get("/my", response_model=List[DelegationResponse])
async def get_my_delegations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DelegationService(db)
    delegations = await service.get_user_delegations(current_user.id)
    return [DelegationResponse.from_orm(d) for d in delegations]

@router.get("/assessment/{assessment_id}", response_model=List[DelegationResponse])
async def get_assessment_delegations(
    assessment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DelegationService(db)
    delegations = await service.get_assessment_delegations(assessment_id)
    return [DelegationResponse.from_orm(d) for d in delegations]

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_delegation(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = DelegationService(db)
    success = await service.revoke_delegation(id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Delegation not found")
    return None
