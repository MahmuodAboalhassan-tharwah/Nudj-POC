"""
Nudj Platform - FastAPI Application

Main application entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.config import settings
from src.backend.database import Base, get_engine
from src.backend.app.common.exceptions import register_exception_handlers
from src.backend.app.common.middleware import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
)
from src.backend.app.auth.router import router as auth_router
from src.backend.app.admin.router import router as admin_router
from src.backend.app.assessments.router import router as assessments_router
from src.backend.app.organizations.router import router as organizations_router
from src.backend.app.dashboards.router import router as dashboards_router
from src.backend.app.reports.router import router as reports_router
from src.backend.app.notifications.router import router as notifications_router
from src.backend.app.comments.router import router as comments_router
from src.backend.app.delegations.router import router as delegations_router
from src.backend.app.framework.router import router as framework_router


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Nudj Platform API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Create database tables in development
    if settings.DEBUG:
        engine = get_engine()
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from src.backend.app.auth import models as auth_models
            from src.backend.app.common import models as common_models
            from src.backend.app.comments import models as comments_models
            from src.backend.app.delegations import models as delegations_models
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nudj Platform API...")


# Create FastAPI application
app = FastAPI(
    title="Nudj Platform API",
    description="HR Maturity Assessment Platform - Authentication & Authorization API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
# Disable rate limiting in development to avoid blocking CORS preflight requests
if not settings.DEBUG:
    app.add_middleware(RateLimitMiddleware, max_requests=100, window_seconds=60)

# Register exception handlers
register_exception_handlers(app)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(assessments_router, prefix="/api")
app.include_router(organizations_router, prefix="/api")
app.include_router(dashboards_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(delegations_router, prefix="/api")
app.include_router(framework_router, prefix="/api")


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Nudj Platform API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else None,
    }
