from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)
    parent_id: UUID | None = None

class CommentCreate(CommentBase):
    response_id: UUID

class CommentAuthor(BaseModel):
    id: UUID
    full_name: str
    avatar_url: str | None = None

    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    response_id: UUID
    parent_id: UUID | None
    content: str
    created_at: datetime
    author: CommentAuthor
    replies: list["CommentResponse"] = []

    class Config:
        from_attributes = True

# For self-referential type hinting in Pydantic v2
CommentResponse.model_rebuild()
