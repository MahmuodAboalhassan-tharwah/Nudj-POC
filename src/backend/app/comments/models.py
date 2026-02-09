from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.backend.database import Base
from src.backend.app.common.models import TimestampMixin

class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    response_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_element_responses.id"), nullable=False, index=True)
    
    parent_id: Mapped[UUID] = mapped_column(ForeignKey("comments.id"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationships
    author: Mapped["User"] = relationship("User", foreign_keys=[user_id])
    replies: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
        remote_side=[parent_id]
    )
    parent: Mapped["Comment"] = relationship(
        "Comment",
        back_populates="replies",
        remote_side=[id],
        uselist=False
    )
    response: Mapped["AssessmentElementResponse"] = relationship("AssessmentElementResponse", back_populates="comments")
