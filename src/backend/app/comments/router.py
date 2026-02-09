from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from src.backend.database import get_db
from src.backend.app.auth.dependencies import get_current_user
from src.backend.app.auth.models import User
from src.backend.app.comments.service import CommentService
from src.backend.app.comments.schemas import CommentCreate, CommentResponse

router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CommentService(db)
    return await service.add_comment(current_user.id, data)

@router.get("/response/{response_id}", response_model=List[CommentResponse])
async def get_comments(
    response_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = CommentService(db)
    return await service.get_response_comments(response_id)
