from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User, Role
from src.backend.app.dashboards.schemas import PortfolioDashboardResponse, ClientDashboardResponse
from src.backend.app.dashboards.service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["Dashboards"])

@router.get("/portfolio", response_model=PortfolioDashboardResponse)
async def get_portfolio_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role != Role.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    service = DashboardService(db)
    return await service.get_portfolio_dashboard()

@router.get("/organization/{org_id}", response_model=ClientDashboardResponse)
async def get_client_dashboard(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Authorization: Super Admin OR Client Admin of that Org
    if current_user.role != Role.SUPER_ADMIN and (
        current_user.organization_id != str(org_id)
    ):
         raise HTTPException(status_code=403, detail="Not authorized")

    service = DashboardService(db)
    return await service.get_client_dashboard(org_id)
