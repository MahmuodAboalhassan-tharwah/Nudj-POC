"""
Common Pydantic Schemas

TASK-014: Shared schemas and validators.
"""
from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(25, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str


class ErrorDetail(BaseModel):
    """Error detail."""
    code: str
    message_en: str
    message_ar: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail
