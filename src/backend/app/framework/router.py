from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User, Role
from src.backend.app.framework.schemas import FrameworkDomainConfigResponse, FrameworkDomainConfigUpdate
from src.backend.app.framework.service import FrameworkService

router = APIRouter(prefix="/framework", tags=["Framework Configuration"])

@router.get("/domains", response_model=List[FrameworkDomainConfigResponse])
async def list_domain_configs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Any authenticated user can view config? Or just admins?
    # Usually handy for frontend to get names, however frontend has them in locales.
    # But for dynamic weights, maybe necessary. 
    # Let's allow authenticated users for now.
    service = FrameworkService(db)
    return await service.get_all_configs()

@router.patch("/domains/{domain_id}", response_model=FrameworkDomainConfigResponse)
async def update_domain_weight(
    domain_id: int,
    data: FrameworkDomainConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Only Super Admins can modify framework configuration"
        )
        
    service = FrameworkService(db)
    return await service.update_config(domain_id, data)
