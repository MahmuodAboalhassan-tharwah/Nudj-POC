"""
Security Middleware

TASK-016: Rate limiting, security headers, and request logging.
"""
import time
import logging
from typing import Callable, Dict
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.backend.config import settings


logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware.
    
    Implements sliding window rate limiting per IP.
    """

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_counts: Dict[str, list] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/health"]:
            return await call_next(request)

        # Get client IP
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0].strip() if forwarded else (
            request.client.host if request.client else "unknown"
        )

        # Clean old requests
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip] if t > cutoff
        ]

        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.max_requests:
            return Response(
                content='{"error": {"code": "RATE_LIMIT_EXCEEDED", "message_en": "Too many requests", "message_ar": "طلبات كثيرة جداً"}}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": str(self.window_seconds)},
            )

        # Record request
        self.request_counts[client_ip].append(now)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    
    Implements OWASP recommended headers.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # OWASP security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # CSP header
        if settings.CSP_ENABLED:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self';"
            )

        # HSTS for production
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests for debugging and monitoring.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log request (skip health checks)
        if request.url.path not in ["/health", "/api/health"]:
            logger.info(
                "Request: %s %s - %s - %.3fs",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"

        return response


class TenantIsolationMiddleware(BaseHTTPMiddleware):
    """
    Ensure tenant isolation for multi-tenant requests.
    
    Adds organization context to request state.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract organization from JWT if available (handled in dependencies)
        # This middleware just ensures the context is available
        request.state.organization_id = None

        return await call_next(request)
