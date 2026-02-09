from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import List

from src.backend.app.comments.models import Comment
from src.backend.app.comments.schemas import CommentCreate

class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_comment(self, user_id: UUID, data: CommentCreate) -> Comment:
        comment = Comment(
            user_id=user_id,
            response_id=data.response_id,
            parent_id=data.parent_id,
            content=data.content
        )
        self.session.add(comment)
        await self.session.commit()
        
        # Reload with relationships
        stmt = select(Comment).where(Comment.id == comment.id).options(
            selectinload(Comment.author)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_response_comments(self, response_id: UUID) -> List[Comment]:
        # Fetch top-level comments with their nested replies
        # selectinload handles the recursion for the replies relationship
        stmt = select(Comment).where(
            Comment.response_id == response_id,
            Comment.parent_id == None
        ).options(
            selectinload(Comment.author),
            selectinload(Comment.replies).selectinload(Comment.author),
            selectinload(Comment.replies).selectinload(Comment.replies) # Support up to 3 levels of nesting easily
        ).order_by(Comment.created_at.asc())
        
        result = await self.session.execute(stmt)
        return result.scalars().all()
