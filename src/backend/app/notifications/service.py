from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc, func
from uuid import UUID
from typing import List, Optional

from src.backend.app.notifications.models import Notification, NotificationType
from src.backend.app.notifications.schemas import NotificationCreate

class NotificationService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_notification(self, data: NotificationCreate) -> Notification:
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            type=data.type,
            link=data.link,
            is_read=False
        )
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_user_notifications(
        self, 
        user_id: UUID, 
        limit: int = 20, 
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
            
        stmt = stmt.order_by(desc(Notification.created_at)).offset(offset).limit(limit)
        
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_unread_count(self, user_id: UUID) -> int:
        stmt = select(func.count()).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def mark_as_read(self, notification_id: UUID, user_id: UUID) -> Optional[Notification]:
        # ensure user owns the notification
        stmt = select(Notification).where(
            Notification.id == notification_id, 
            Notification.user_id == user_id
        )
        result = await self.session.execute(stmt)
        notification = result.scalar_one_or_none()
        
        if notification:
            notification.is_read = True
            await self.session.commit()
            await self.session.refresh(notification)
            
        return notification

    async def mark_all_as_read(self, user_id: UUID) -> int:
        stmt = update(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).values(is_read=True)
        
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
