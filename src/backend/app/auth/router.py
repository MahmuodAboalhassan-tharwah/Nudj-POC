"""
Auth Router

TASK-015: FastAPI routes for authentication.

Endpoints:
- POST /auth/login - Login with email/password
- POST /auth/mfa/verify - Verify MFA code
- POST /auth/register - Register via invitation
- POST /auth/refresh - Refresh access token
- POST /auth/logout - Logout and revoke tokens
- POST /auth/forgot-password - Request password reset
- POST /auth/reset-password - Reset password with token
- GET /auth/me - Get current user
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_async_session
from src.backend.config import settings
from src.backend.app.auth.service import AuthService
from src.backend.app.auth.session_service import SessionService
from src.backend.app.auth.mfa_service import MFAService
from src.backend.app.auth.invitation_service import InvitationService
from src.backend.app.auth.dependencies import (
    get_current_user,
    get_current_user_optional,
    get_client_info,
)
from src.backend.app.auth.schemas import (
    LoginRequest,
    LoginResponse,
    MFAVerifyRequest,
    RegisterRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    InvitationValidateResponse,
    UserResponse,
    MFASetupResponse,
    MFAEnableRequest,
    MFADisableRequest,
    SuccessResponse,
    SessionListResponse,
)
from src.backend.app.auth.models import User
from src.backend.app.auth.permissions import PermissionService


router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# Authentication Endpoints
# =============================================================================

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Login with email and password.
    
    Returns access/refresh tokens or MFA pending token if MFA enabled.
    """
    client_info = await get_client_info(http_request)
    auth_service = AuthService(session)
    
    result = await auth_service.login(
        email=request.email,
        password=request.password,
        ip_address=client_info["ip_address"],
        user_agent=client_info["user_agent"],
    )
    
    return LoginResponse(**result)


@router.post("/mfa/verify", response_model=LoginResponse)
async def verify_mfa(
    request: MFAVerifyRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Verify MFA code after login.
    
    Requires MFA pending token from login response.
    """
    client_info = await get_client_info(http_request)
    auth_service = AuthService(session)
    
    result = await auth_service.verify_mfa(
        mfa_token=request.mfa_token,
        code=request.code,
        ip_address=client_info["ip_address"],
        user_agent=client_info["user_agent"],
    )
    
    return LoginResponse(**result)


@router.post("/register", response_model=LoginResponse)
async def register(
    request: RegisterRequest,
    http_request: Request,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Register using invitation token.
    
    Sets password and profile information.
    """
    client_info = await get_client_info(http_request)
    auth_service = AuthService(session)
    
    result = await auth_service.register(
        token=request.token,
        password=request.password,
        name_ar=request.name_ar,
        name_en=request.name_en,
        phone_sa=request.phone_sa,
        ip_address=client_info["ip_address"],
        user_agent=client_info["user_agent"],
    )
    
    return LoginResponse(**result)


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: TokenRefreshRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Refresh access token using refresh token.
    
    Implements token rotation (old refresh token is revoked).
    """
    auth_service = AuthService(session)
    result = await auth_service.refresh_token(request.refresh_token)
    return TokenRefreshResponse(**result)


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Logout current user.
    
    Revokes all tokens and ends session.
    """
    auth_service = AuthService(session)
    await auth_service.logout(user.id)
    
    return SuccessResponse(
        message_en="Logged out successfully",
        message_ar="تم تسجيل الخروج بنجاح",
    )


@router.post("/forgot-password", response_model=SuccessResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Request password reset email.
    
    Always returns success to prevent email enumeration.
    """
    auth_service = AuthService(session)
    await auth_service.request_password_reset(request.email)
    
    return SuccessResponse(
        message_en="If an account exists, a reset email has been sent",
        message_ar="إذا كان الحساب موجوداً، تم إرسال بريد إعادة التعيين",
    )


@router.post("/reset-password", response_model=SuccessResponse)
async def reset_password(
    request: ResetPasswordRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Reset password using token from email.
    """
    auth_service = AuthService(session)
    await auth_service.reset_password(request.token, request.password)
    
    return SuccessResponse(
        message_en="Password reset successfully",
        message_ar="تم إعادة تعيين كلمة المرور بنجاح",
    )


@router.post("/change-password", response_model=SuccessResponse)
async def change_password(
    request: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Change password (authenticated user).
    """
    auth_service = AuthService(session)
    await auth_service.change_password(
        user=user,
        current_password=request.current_password,
        new_password=request.new_password,
    )
    
    return SuccessResponse(
        message_en="Password changed successfully",
        message_ar="تم تغيير كلمة المرور بنجاح",
    )


# =============================================================================
# User Profile Endpoints
# =============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    """Get current authenticated user's profile."""
    permissions = list(PermissionService.get_role_permissions(user.role))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name_ar=user.name_ar or "",
        name_en=user.name_en or "",
        role=user.role.value,
        organization_id=user.organization_id,
        mfa_enabled=user.mfa_enabled,
        permissions=permissions,
    )


# =============================================================================
# MFA Endpoints
# =============================================================================

@router.get("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Generate MFA setup data (secret, QR code URI).
    
    Does not enable MFA - use POST /mfa/enable after verification.
    """
    mfa_service = MFAService(session)
    return await mfa_service.generate_setup(user)


@router.post("/mfa/enable", response_model=SuccessResponse)
async def enable_mfa(
    request: MFAEnableRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Enable MFA after verifying setup code.
    """
    mfa_service = MFAService(session)
    await mfa_service.enable_mfa(user, user.mfa_secret, request.code)
    
    return SuccessResponse(
        message_en="MFA enabled successfully",
        message_ar="تم تفعيل المصادقة الثنائية بنجاح",
    )


@router.post("/mfa/disable", response_model=SuccessResponse)
async def disable_mfa(
    request: MFADisableRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Disable MFA (requires current code).
    """
    mfa_service = MFAService(session)
    await mfa_service.disable_mfa(user, request.code)
    
    return SuccessResponse(
        message_en="MFA disabled successfully",
        message_ar="تم تعطيل المصادقة الثنائية بنجاح",
    )


# =============================================================================
# Invitation Endpoints
# =============================================================================

@router.get("/invitation/validate", response_model=InvitationValidateResponse)
async def validate_invitation(
    token: str = Query(..., description="Invitation token"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Validate invitation token and return details.
    """
    invitation_service = InvitationService(session)
    invitation = await invitation_service.validate_token(token)
    
    if not invitation:
        return InvitationValidateResponse(is_valid=False)
    
    return InvitationValidateResponse(
        is_valid=True,
        email=invitation.email,
        role=invitation.role.value,
        organization_name=None,  # TODO: Fetch org name
        expires_at=invitation.expires_at,
    )


# =============================================================================
# Session Endpoints
# =============================================================================

@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all active sessions for current user.
    """
    session_service = SessionService(session)
    sessions = await session_service.get_user_sessions(user.id)
    
    return SessionListResponse(
        sessions=[
            {
                "id": s.id,
                "ip_address": s.ip_address,
                "user_agent": s.user_agent,
                "last_activity_at": s.last_activity_at,
                "is_current": False,  # TODO: Compare with current session
            }
            for s in sessions
        ]
    )


@router.delete("/sessions/{session_id}", response_model=SuccessResponse)
async def revoke_session(
    session_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Revoke a specific session.
    """
    session_service = SessionService(session)
    await session_service.revoke_session(user.id, session_id)
    
    return SuccessResponse(
        message_en="Session revoked successfully",
        message_ar="تم إلغاء الجلسة بنجاح",
    )


@router.delete("/sessions", response_model=SuccessResponse)
async def revoke_all_sessions(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Revoke all sessions except current.
    """
    session_service = SessionService(session)
    await session_service.revoke_all_sessions(user.id)
    
    return SuccessResponse(
        message_en="All other sessions revoked",
        message_ar="تم إلغاء جميع الجلسات الأخرى",
    )
