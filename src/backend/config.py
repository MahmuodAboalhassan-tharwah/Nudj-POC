"""
Nudj Application Configuration

TASK-003: Pydantic Settings for all application configuration.

Loads from environment variables with .env file support.
Sections: Database, Redis, JWT, Session, Email, SMS, Security, App.
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Usage:
        from src.backend.config import settings
        print(settings.APP_NAME)
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==========================================================================
    # App
    # ==========================================================================
    APP_NAME: str = "Nudj"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ==========================================================================
    # Database (PostgreSQL with asyncpg)
    # ==========================================================================
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nudj"
    
    # ==========================================================================
    # Redis
    # ==========================================================================
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # ==========================================================================
    # JWT Authentication
    # ==========================================================================
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_SECURE_RANDOM_STRING"
    JWT_ALGORITHM: str = "HS256"  # HS256 for POC, RS256 for production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==========================================================================
    # Session Management
    # ==========================================================================
    SESSION_TIMEOUT_MINUTES: int = 30  # Inactivity timeout
    SESSION_TIMEOUT_MIN: int = 15  # Minimum allowed
    SESSION_TIMEOUT_MAX: int = 120  # Maximum allowed

    # ==========================================================================
    # Password Policy
    # ==========================================================================
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True

    # ==========================================================================
    # Account Security
    # ==========================================================================
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    PASSWORD_RESET_EXPIRE_HOURS: int = 1
    INVITATION_EXPIRE_DAYS: int = 7

    # ==========================================================================
    # Rate Limiting
    # ==========================================================================
    RATE_LIMIT_LOGIN_PER_MINUTE: int = 20
    RATE_LIMIT_REGISTER_PER_10MIN: int = 10
    RATE_LIMIT_PASSWORD_RESET_PER_HOUR: int = 5

    # ==========================================================================
    # Email Service
    # ==========================================================================
    EMAIL_PROVIDER: str = "sendgrid"  # sendgrid, ses
    SENDGRID_API_KEY: Optional[str] = None
    EMAIL_FROM_ADDRESS: str = "noreply@nudj.sa"
    EMAIL_FROM_NAME: str = "Nudj HR Platform"

    # ==========================================================================
    # SMS Service (Saudi OTP)
    # ==========================================================================
    SMS_PROVIDER: str = "unifonic"  # unifonic (Saudi-based)
    UNIFONIC_APP_ID: Optional[str] = None
    UNIFONIC_SENDER_ID: str = "Nudj"
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 6

    # ==========================================================================
    # MFA
    # ==========================================================================
    MFA_ISSUER_NAME: str = "Nudj HR Platform"
    MFA_MANDATORY_ROLES: List[str] = ["super_admin", "analyst"]

    # ==========================================================================
    # Security Headers & CORS
    # ==========================================================================
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://nudj.sa",
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    CSP_ENABLED: bool = False

    # ==========================================================================
    # Encryption (for PII fields - PDPL compliance)
    # ==========================================================================
    ENCRYPTION_KEY: str = "CHANGE_ME_32_BYTE_KEY_FOR_FERNET"  # Fernet key

    # ==========================================================================
    # API Configuration
    # ==========================================================================
    API_V1_PREFIX: str = "/api/v1"


# Global settings instance
settings = Settings()
