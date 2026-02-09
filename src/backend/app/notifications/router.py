from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User
from src.backend.app.notifications.service import NotificationService
from src.backend.app.notifications.schemas import NotificationResponse, NotificationUpdate

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    return await service.get_user_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        unread_only=unread_only
    )

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    count = await service.get_unread_count(current_user.id)
    return {"count": count}

@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    notification = await service.mark_as_read(notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    return notification

@router.patch("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = NotificationService(db)
    count = await service.mark_all_as_read(current_user.id)
    return {"updated_count": count}
