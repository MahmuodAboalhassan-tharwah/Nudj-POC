"""
Admin Router

TASK-015: Admin routes for user management and audit logs.

Endpoints:
- GET /admin/users - List users (paginated)
- POST /admin/users/invite - Invite new user
- GET /admin/users/{id} - Get user details
- PATCH /admin/users/{id} - Update user
- DELETE /admin/users/{id} - Deactivate user
- GET /admin/audit-logs - List audit logs
- GET /admin/audit-logs/export - Export audit logs as CSV
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend.database import get_async_session
from src.backend.app.auth.models import User, Role
from src.backend.app.auth.dependencies import (
    get_current_user,
    require_permission,
    require_role,
)
from src.backend.app.auth.invitation_service import InvitationService
from src.backend.app.common.audit_service import AuditService
from src.backend.app.auth.schemas import (
    InviteUserRequest,
    BulkInviteRequest,
    UserDetailResponse,
    UserListResponse,
    UpdateUserRequest,
    AuditLogListResponse,
    InvitationResponse,
    SuccessResponse,
)


router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# User Management
# =============================================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    role: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    user: User = Depends(require_permission("users:read")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List all users with pagination and filters.
    
    Requires: users:read permission
    """
    query = select(User)
    count_query = select(func.count(User.id))
    
    # Filter by role
    if role:
        try:
            role_enum = Role(role)
            query = query.where(User.role == role_enum)
            count_query = count_query.where(User.role == role_enum)
        except ValueError:
            pass  # Invalid role, ignore filter
    
    # Filter by organization (for tenant isolation)
    if organization_id:
        query = query.where(User.organization_id == organization_id)
        count_query = count_query.where(User.organization_id == organization_id)
    
    # Apply tenant isolation for non-super admins
    if user.role != Role.SUPER_ADMIN:
        query = query.where(User.organization_id == user.organization_id)
        count_query = count_query.where(User.organization_id == user.organization_id)
    
    # Search
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            (User.email.ilike(search_pattern)) |
            (User.name_en.ilike(search_pattern)) |
            (User.name_ar.ilike(search_pattern))
        )
    
    # Get total count
    total_result = await session.execute(count_query)
    total = total_result.scalar()
    
    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())
    
    result = await session.execute(query)
    users = result.scalars().all()
    
    return UserListResponse(
        items=[
            UserDetailResponse(
                id=u.id,
                email=u.email,
                name_ar=u.name_ar or "",
                name_en=u.name_en or "",
                role=u.role.value,
                organization_id=u.organization_id,
                mfa_enabled=u.mfa_enabled,
                permissions=[],
                phone_sa=u.phone_sa,
                is_active=u.is_active,
                is_verified=u.is_verified,
                sso_provider=u.sso_provider.value if u.sso_provider else None,
                last_login_at=u.last_login_at,
                created_at=u.created_at,
                updated_at=u.updated_at,
            )
            for u in users
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.post("/users/invite", response_model=InvitationResponse)
async def invite_user(
    request: InviteUserRequest,
    user: User = Depends(require_permission("users:invite")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Send invitation to new user.
    
    Requires: users:invite permission
    """
    invitation_service = InvitationService(session)
    
    invitation = await invitation_service.create_invitation(
        email=request.email,
        role=Role(request.role),
        invited_by=user.id,
        organization_id=request.organization_id or user.organization_id,
    )
    
    return InvitationResponse(
        id=invitation.id,
        email=invitation.email,
        role=invitation.role.value,
        organization_name=None,
        expires_at=invitation.expires_at,
        is_expired=invitation.is_expired,
        is_used=invitation.is_used,
        created_at=invitation.created_at,
    )


@router.post("/users/invite/bulk", response_model=SuccessResponse)
async def bulk_invite_users(
    request: BulkInviteRequest,
    user: User = Depends(require_permission("users:invite")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Send bulk invitations.
    
    Requires: users:invite permission
    """
    invitation_service = InvitationService(session)
    
    invitations_data = [
        {
            "email": inv.email,
            "role": Role(inv.role),
            "organization_id": inv.organization_id or user.organization_id,
        }
        for inv in request.invitations
    ]
    
    await invitation_service.bulk_create_invitations(
        invitations=invitations_data,
        invited_by=user.id,
    )
    
    return SuccessResponse(
        message_en=f"Sent {len(request.invitations)} invitations",
        message_ar=f"تم إرسال {len(request.invitations)} دعوات",
    )


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: str,
    user: User = Depends(require_permission("users:read")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get user details by ID.
    
    Requires: users:read permission
    """
    from src.backend.app.common.exceptions import NotFoundException
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise NotFoundException()
    
    # Tenant isolation check
    if user.role != Role.SUPER_ADMIN:
        if target_user.organization_id != user.organization_id:
            raise NotFoundException()
    
    return UserDetailResponse(
        id=target_user.id,
        email=target_user.email,
        name_ar=target_user.name_ar or "",
        name_en=target_user.name_en or "",
        role=target_user.role.value,
        organization_id=target_user.organization_id,
        mfa_enabled=target_user.mfa_enabled,
        permissions=[],
        phone_sa=target_user.phone_sa,
        is_active=target_user.is_active,
        is_verified=target_user.is_verified,
        sso_provider=target_user.sso_provider.value if target_user.sso_provider else None,
        last_login_at=target_user.last_login_at,
        created_at=target_user.created_at,
        updated_at=target_user.updated_at,
    )


@router.patch("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    user: User = Depends(require_permission("users:write")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Update user role or status.
    
    Requires: users:write permission
    """
    from src.backend.app.common.exceptions import NotFoundException
    from src.backend.app.auth.permissions import PermissionService
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise NotFoundException()
    
    # Cannot modify higher role
    if request.role:
        new_role = Role(request.role)
        if not PermissionService.can_manage_role(user.role, new_role):
            from src.backend.app.auth.exceptions import InsufficientPermissionsException
            raise InsufficientPermissionsException()
        target_user.role = new_role
    
    if request.is_active is not None:
        target_user.is_active = request.is_active

    await session.flush()
    await session.commit()  # Commit changes to database

    return UserDetailResponse(
        id=target_user.id,
        email=target_user.email,
        name_ar=target_user.name_ar or "",
        name_en=target_user.name_en or "",
        role=target_user.role.value,
        organization_id=target_user.organization_id,
        mfa_enabled=target_user.mfa_enabled,
        permissions=[],
        phone_sa=target_user.phone_sa,
        is_active=target_user.is_active,
        is_verified=target_user.is_verified,
        sso_provider=target_user.sso_provider.value if target_user.sso_provider else None,
        last_login_at=target_user.last_login_at,
        created_at=target_user.created_at,
        updated_at=target_user.updated_at,
    )


@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def deactivate_user(
    user_id: str,
    user: User = Depends(require_permission("users:delete")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Deactivate user (soft delete).
    
    Requires: users:delete permission
    """
    from src.backend.app.common.exceptions import NotFoundException
    
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        raise NotFoundException()

    target_user.is_active = False
    await session.commit()  # Commit changes to database

    return SuccessResponse(
        message_en="User deactivated successfully",
        message_ar="تم تعطيل المستخدم بنجاح",
    )


# =============================================================================
# Audit Logs
# =============================================================================

@router.get("/audit-logs", response_model=AuditLogListResponse)
async def list_audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    event_type: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    organization_id: Optional[str] = Query(None),
    user: User = Depends(require_permission("audit:read")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    List audit logs with pagination and filters.
    
    Requires: audit:read permission
    """
    audit_service = AuditService(session)

    # Build filter parameters (query_logs expects individual kwargs, not a dict)
    filter_kwargs = {
        "page": page,
        "page_size": page_size,
    }

    if event_type:
        try:
            from src.backend.app.common.models import AuditEventType
            filter_kwargs["event_type"] = AuditEventType(event_type)
        except ValueError:
            pass  # Invalid event type, ignore filter

    if user_id:
        filter_kwargs["user_id"] = user_id

    # Tenant isolation for non-super admins
    if user.role != Role.SUPER_ADMIN:
        filter_kwargs["organization_id"] = user.organization_id
    elif organization_id:
        filter_kwargs["organization_id"] = organization_id

    logs, total = await audit_service.query_logs(**filter_kwargs)
    
    return AuditLogListResponse(
        items=[
            {
                "id": log.id,
                "event_type": log.event_type.value,
                "user_id": log.user_id,
                "user_email": None,  # TODO: Join with user
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details,
                "organization_id": log.organization_id,
                "created_at": log.created_at,
            }
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size,
    )


@router.get("/audit-logs/export")
async def export_audit_logs(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    user: User = Depends(require_permission("audit:export")),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Export audit logs as CSV.
    
    Requires: audit:export permission
    """
    audit_service = AuditService(session)
    
    csv_content = await audit_service.export_csv(
        organization_id=user.organization_id if user.role != Role.SUPER_ADMIN else None,
    )
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=audit_logs.csv"
        },
    )
