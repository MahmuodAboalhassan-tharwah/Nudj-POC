"""
Common Exception Classes and Handlers

TASK-004: Global exception classes and FastAPI exception handlers.

Provides:
- NudjException base class
- HTTP-level exceptions
- Global exception handler registration
"""
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


# =============================================================================
# Base Exception
# =============================================================================

class NudjException(Exception):
    """
    Base exception for all Nudj custom exceptions.
    
    Includes:
    - HTTP status code
    - Error code (for i18n in frontend)
    - User-friendly messages (ar/en)
    - Optional details for debugging (not shown to users in production)
    """
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"
    message_ar: str = "حدث خطأ داخلي"
    message_en: str = "An internal error occurred"

    def __init__(
        self,
        message_en: Optional[str] = None,
        message_ar: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message_en = message_en or self.__class__.message_en
        self.message_ar = message_ar or self.__class__.message_ar
        self.details = details
        super().__init__(self.message_en)

    def to_dict(self, include_details: bool = False) -> Dict[str, Any]:
        """Convert exception to API response format."""
        result = {
            "error": {
                "code": self.error_code,
                "message_en": self.message_en,
                "message_ar": self.message_ar,
            }
        }
        if include_details and self.details:
            result["error"]["details"] = self.details
        return result


# Alias for backward compatibility
AppException = NudjException


# =============================================================================
# HTTP Exceptions
# =============================================================================

class BadRequestException(NudjException):
    """400 Bad Request - Invalid input or parameters."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "BAD_REQUEST"
    message_ar = "طلب غير صالح"
    message_en = "Bad request"


class UnauthorizedException(NudjException):
    """401 Unauthorized - Authentication required or failed."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "UNAUTHORIZED"
    message_ar = "غير مصرح"
    message_en = "Unauthorized"


class ForbiddenException(NudjException):
    """403 Forbidden - Authenticated but not allowed."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "FORBIDDEN"
    message_ar = "غير مسموح"
    message_en = "Forbidden"


class NotFoundException(NudjException):
    """404 Not Found - Resource does not exist."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    message_ar = "غير موجود"
    message_en = "Not found"


class ConflictException(NudjException):
    """409 Conflict - Resource already exists or state conflict."""
    status_code = status.HTTP_409_CONFLICT
    error_code = "CONFLICT"
    message_ar = "تعارض"
    message_en = "Conflict"


class ValidationException(NudjException):
    """422 Unprocessable Entity - Validation failed."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    message_ar = "خطأ في التحقق"
    message_en = "Validation error"


class TooManyRequestsException(NudjException):
    """429 Too Many Requests - Rate limit exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    message_ar = "تم تجاوز الحد المسموح"
    message_en = "Rate limit exceeded"


class InternalServerException(NudjException):
    """500 Internal Server Error - Unexpected error."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "INTERNAL_ERROR"
    message_ar = "حدث خطأ داخلي"
    message_en = "An internal error occurred"


class ServiceUnavailableException(NudjException):
    """503 Service Unavailable - External service down."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
    message_ar = "الخدمة غير متاحة"
    message_en = "Service unavailable"


# =============================================================================
# Exception Handlers
# =============================================================================

async def nudj_exception_handler(request: Request, exc: NudjException) -> JSONResponse:
    """Handle all NudjException subclasses."""
    from src.backend.config import settings
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(include_details=settings.DEBUG),
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    from src.backend.config import settings
    import logging
    
    logger = logging.getLogger(__name__)
    logger.exception(f"Unhandled exception: {exc}")
    
    error = InternalServerException()
    if settings.DEBUG:
        error.details = {"exception": str(exc)}
    
    return JSONResponse(
        status_code=error.status_code,
        content=error.to_dict(include_details=settings.DEBUG),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers with the FastAPI app."""
    app.add_exception_handler(NudjException, nudj_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
