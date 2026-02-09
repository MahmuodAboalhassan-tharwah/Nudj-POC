"""
Auth-Specific Exceptions

TASK-004: Authentication and authorization exception classes.

Provides detailed, bilingual error messages for auth flows.
"""
from typing import Optional, Dict, Any
from fastapi import status
from src.backend.app.common.exceptions import NudjException


# =============================================================================
# Authentication Exceptions
# =============================================================================

class InvalidCredentialsException(NudjException):
    """Login failed - invalid email or password."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "INVALID_CREDENTIALS"
    message_ar = "البريد الإلكتروني أو كلمة المرور غير صحيحة"
    message_en = "Invalid email or password"


class AccountLockedException(NudjException):
    """Account locked due to too many failed attempts."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "ACCOUNT_LOCKED"
    message_ar = "تم تأمين الحساب. حاول مرة أخرى لاحقاً"
    message_en = "Account is locked. Please try again later"

    def __init__(self, locked_until_minutes: Optional[int] = None, **kwargs):
        details = {}
        if locked_until_minutes:
            details["locked_minutes_remaining"] = locked_until_minutes
        super().__init__(details=details, **kwargs)


class AccountDeactivatedException(NudjException):
    """User account is deactivated."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "ACCOUNT_DEACTIVATED"
    message_ar = "تم إلغاء تنشيط الحساب"
    message_en = "Account is deactivated"


class EmailNotVerifiedException(NudjException):
    """Email not verified."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "EMAIL_NOT_VERIFIED"
    message_ar = "البريد الإلكتروني غير مؤكد"
    message_en = "Email is not verified"


# =============================================================================
# Token Exceptions
# =============================================================================

class TokenExpiredException(NudjException):
    """Token has expired."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "TOKEN_EXPIRED"
    message_ar = "انتهت صلاحية الرمز"
    message_en = "Token has expired"


class TokenInvalidException(NudjException):
    """Token is invalid or malformed."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "TOKEN_INVALID"
    message_ar = "الرمز غير صالح"
    message_en = "Token is invalid"


class TokenRevokedException(NudjException):
    """Token has been revoked."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "TOKEN_REVOKED"
    message_ar = "تم إلغاء الرمز"
    message_en = "Token has been revoked"


# =============================================================================
# Session Exceptions
# =============================================================================

class SessionExpiredException(NudjException):
    """Session has expired due to inactivity."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "SESSION_EXPIRED"
    message_ar = "انتهت الجلسة بسبب عدم النشاط"
    message_en = "Session expired due to inactivity"


# =============================================================================
# MFA Exceptions
# =============================================================================

class MFARequiredException(NudjException):
    """MFA verification required to complete login."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "MFA_REQUIRED"
    message_ar = "مطلوب التحقق بخطوتين"
    message_en = "Multi-factor authentication required"


class MFAInvalidCodeException(NudjException):
    """Invalid MFA code."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "MFA_INVALID_CODE"
    message_ar = "رمز التحقق غير صحيح"
    message_en = "Invalid verification code"


class MFANotEnabledException(NudjException):
    """MFA not enabled for this user."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "MFA_NOT_ENABLED"
    message_ar = "لم يتم تفعيل التحقق بخطوتين"
    message_en = "MFA is not enabled"


class MFASetupRequiredException(NudjException):
    """MFA setup required for this role."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "MFA_SETUP_REQUIRED"
    message_ar = "يجب تفعيل التحقق بخطوتين لهذا الدور"
    message_en = "MFA setup is required for this role"


# =============================================================================
# Invitation Exceptions
# =============================================================================

class InvitationNotFoundException(NudjException):
    """Invitation not found."""
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "INVITATION_NOT_FOUND"
    message_ar = "الدعوة غير موجودة"
    message_en = "Invitation not found"


class InvitationExpiredException(NudjException):
    """Invitation has expired."""
    status_code = status.HTTP_410_GONE
    error_code = "INVITATION_EXPIRED"
    message_ar = "انتهت صلاحية الدعوة"
    message_en = "Invitation has expired"


class InvitationUsedException(NudjException):
    """Invitation has already been used."""
    status_code = status.HTTP_410_GONE
    error_code = "INVITATION_USED"
    message_ar = "تم استخدام الدعوة بالفعل"
    message_en = "Invitation has already been used"


# =============================================================================
# Password Exceptions
# =============================================================================

class PasswordTooWeakException(NudjException):
    """Password does not meet requirements."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "PASSWORD_TOO_WEAK"
    message_ar = "كلمة المرور لا تلبي المتطلبات"
    message_en = "Password does not meet requirements"

    def __init__(self, missing_requirements: Optional[list] = None, **kwargs):
        details = {}
        if missing_requirements:
            details["missing_requirements"] = missing_requirements
        super().__init__(details=details, **kwargs)


class PasswordResetExpiredException(NudjException):
    """Password reset link has expired."""
    status_code = status.HTTP_410_GONE
    error_code = "PASSWORD_RESET_EXPIRED"
    message_ar = "انتهت صلاحية رابط إعادة تعيين كلمة المرور"
    message_en = "Password reset link has expired"


# =============================================================================
# Registration Exceptions
# =============================================================================

class EmailAlreadyRegisteredException(NudjException):
    """Email is already registered."""
    status_code = status.HTTP_409_CONFLICT
    error_code = "EMAIL_ALREADY_REGISTERED"
    message_ar = "البريد الإلكتروني مسجل بالفعل"
    message_en = "Email is already registered"


class RegistrationNotAllowedException(NudjException):
    """Registration requires a valid invitation."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "REGISTRATION_NOT_ALLOWED"
    message_ar = "التسجيل يتطلب دعوة صالحة"
    message_en = "Registration requires a valid invitation"


# =============================================================================
# Authorization Exceptions
# =============================================================================

class InsufficientPermissionsException(NudjException):
    """User does not have required permissions."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "INSUFFICIENT_PERMISSIONS"
    message_ar = "لا تملك الصلاحيات الكافية"
    message_en = "Insufficient permissions"


class TenantAccessDeniedException(NudjException):
    """User cannot access this organization's resources."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "TENANT_ACCESS_DENIED"
    message_ar = "لا يمكنك الوصول إلى موارد هذه المنظمة"
    message_en = "Access to this organization's resources is denied"


class DomainAccessDeniedException(NudjException):
    """User cannot access this HR domain."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "DOMAIN_ACCESS_DENIED"
    message_ar = "لا يمكنك الوصول إلى هذا المجال"
    message_en = "Access to this domain is denied"


# =============================================================================
# SSO Exceptions
# =============================================================================

class SSONotConfiguredException(NudjException):
    """SSO not configured for this organization."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "SSO_NOT_CONFIGURED"
    message_ar = "لم يتم تكوين تسجيل الدخول الموحد لهذه المنظمة"
    message_en = "SSO is not configured for this organization"


class SSOAuthenticationFailedException(NudjException):
    """SSO authentication failed."""
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "SSO_AUTH_FAILED"
    message_ar = "فشل تسجيل الدخول الموحد"
    message_en = "SSO authentication failed"


class SSOUserNotInvitedException(NudjException):
    """SSO user must be invited first."""
    status_code = status.HTTP_403_FORBIDDEN
    error_code = "SSO_USER_NOT_INVITED"
    message_ar = "يجب دعوة المستخدم أولاً"
    message_en = "User must be invited before SSO login"
