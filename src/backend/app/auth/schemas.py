"""
Auth Pydantic Schemas

TASK-014: Request/Response schemas for auth endpoints.

Features:
- Input validation with Pydantic V2
- Bilingual error messages
- Consistent response format
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# =============================================================================
# Base Schemas
# =============================================================================

class BilingualMessage(BaseModel):
    """Bilingual message for responses."""
    message_en: str
    message_ar: str


class SuccessResponse(BilingualMessage):
    """Generic success response."""
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response format."""
    error: dict = Field(..., description="Error details with code and messages")


# =============================================================================
# Auth Schemas
# =============================================================================

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login response - may require MFA."""
    requires_mfa: bool = False
    mfa_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = "Bearer"
    expires_in: Optional[int] = None
    user: Optional["UserResponse"] = None


class MFAVerifyRequest(BaseModel):
    """MFA code verification request."""
    mfa_token: str
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")
    trust_device: bool = False


class RegisterRequest(BaseModel):
    """Registration request with invitation token."""
    token: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    name_ar: str = Field(..., min_length=2, max_length=100)
    name_en: str = Field(..., min_length=2, max_length=100)
    phone_sa: Optional[str] = Field(None, pattern=r"^\+966[0-9]{9}$")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain uppercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
            raise ValueError("Password must contain special character")
        return v


class TokenRefreshRequest(BaseModel):
    """Token refresh request."""
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    """Token refresh response."""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Password reset with token."""
    token: str
    password: str = Field(..., min_length=8)


class ChangePasswordRequest(BaseModel):
    """Password change (authenticated)."""
    current_password: str
    new_password: str = Field(..., min_length=8)


# =============================================================================
# MFA Schemas
# =============================================================================

class MFASetupResponse(BaseModel):
    """MFA setup data."""
    secret: str
    qr_code_uri: str
    backup_codes: List[str]


class MFAEnableRequest(BaseModel):
    """MFA enable verification."""
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class MFADisableRequest(BaseModel):
    """MFA disable verification."""
    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


# =============================================================================
# Invitation Schemas
# =============================================================================

class InvitationValidateResponse(BaseModel):
    """Invitation validation response."""
    is_valid: bool
    email: Optional[str] = None
    role: Optional[str] = None
    organization_name: Optional[str] = None
    expires_at: Optional[datetime] = None


class InviteUserRequest(BaseModel):
    """Send invitation request."""
    email: EmailStr
    role: str = Field(..., pattern=r"^(analyst|client_admin|assessor)$")
    organization_id: Optional[str] = None
    domain_ids: Optional[List[str]] = None


class BulkInviteRequest(BaseModel):
    """Bulk invitation request."""
    invitations: List[InviteUserRequest]


class InvitationResponse(BaseModel):
    """Invitation details response."""
    id: str
    email: str
    role: str
    organization_name: Optional[str]
    expires_at: datetime
    is_expired: bool
    is_used: bool
    created_at: datetime


# =============================================================================
# User Schemas
# =============================================================================

class UserResponse(BaseModel):
    """Current user response."""
    id: str
    email: str
    name_ar: str
    name_en: str
    role: str
    organization_id: Optional[str]
    mfa_enabled: bool
    permissions: List[str]


class UserDetailResponse(UserResponse):
    """Full user details."""
    phone_sa: Optional[str]
    is_active: bool
    is_verified: bool
    sso_provider: Optional[str]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class UserListResponse(BaseModel):
    """Paginated user list."""
    items: List[UserDetailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class UpdateUserRequest(BaseModel):
    """Update user request."""
    role: Optional[str] = None
    is_active: Optional[bool] = None


# =============================================================================
# Session Schemas
# =============================================================================

class SessionResponse(BaseModel):
    """Active session info."""
    id: str
    ip_address: str
    user_agent: Optional[str]
    last_activity_at: datetime
    is_current: bool


class SessionListResponse(BaseModel):
    """User sessions list."""
    sessions: List[SessionResponse]


# =============================================================================
# SSO Schemas
# =============================================================================

class SSOInitRequest(BaseModel):
    """SSO initialization request."""
    organization_id: str
    provider: str = Field(..., pattern=r"^(azure_ad|google)$")


class SSOInitResponse(BaseModel):
    """SSO initialization response."""
    authorization_url: str


class SSOConfigureRequest(BaseModel):
    """SSO configuration request."""
    organization_id: str
    provider: str = Field(..., pattern=r"^(azure_ad|google)$")
    client_id: str
    client_secret: str
    tenant_id: Optional[str] = None  # Azure AD only


# =============================================================================
# Audit Schemas
# =============================================================================

class AuditLogResponse(BaseModel):
    """Audit log entry."""
    id: str
    event_type: str
    user_id: Optional[str]
    user_email: Optional[str]
    ip_address: str
    user_agent: Optional[str]
    details: Optional[dict]
    organization_id: Optional[str]
    created_at: datetime


class AuditLogListResponse(BaseModel):
    """Paginated audit logs."""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Update forward references
LoginResponse.model_rebuild()
