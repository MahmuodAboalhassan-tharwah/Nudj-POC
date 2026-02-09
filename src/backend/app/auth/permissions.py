"""
Permissions Service

TASK-013: Role-based access control and permission checks.

Features:
- Role hierarchy enforcement
- Permission checking
- Tenant isolation guards
- Domain access control for assessors
"""
from typing import Optional, List, Set
from functools import lru_cache

from src.backend.app.auth.models import Role


# Role hierarchy (higher roles inherit lower role permissions)
ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 4,
    Role.ANALYST: 3,
    Role.CLIENT_ADMIN: 2,
    Role.ASSESSOR: 1,
}

# Permission definitions by role
ROLE_PERMISSIONS = {
    Role.SUPER_ADMIN: {
        # User management
        "users:read", "users:write", "users:delete", "users:invite",
        # Organization management
        "orgs:read", "orgs:write", "orgs:delete",
        # Assessment management
        "assessments:read", "assessments:write", "assessments:delete",
        # Reports
        "reports:read", "reports:write", "reports:export",
        # Admin functions
        "audit:read", "audit:export",
        "settings:read", "settings:write",
        "sso:configure",
    },
    Role.ANALYST: {
        # User management (read-only)
        "users:read",
        # Organization management (read-only)
        "orgs:read",
        # Assessment management
        "assessments:read", "assessments:write",
        # Reports
        "reports:read", "reports:write", "reports:export",
    },
    Role.CLIENT_ADMIN: {
        # User management (org-scoped)
        "users:read", "users:write", "users:invite",
        # Assessment management (org-scoped)
        "assessments:read", "assessments:write",
        # Reports (org-scoped)
        "reports:read",
    },
    Role.ASSESSOR: {
        # Limited to assigned domains
        "assessments:read",
    },
}


class PermissionService:
    """
    Permission checking and authorization service.
    """

    @staticmethod
    @lru_cache(maxsize=128)
    def get_role_permissions(role: Role) -> Set[str]:
        """Get all permissions for a role."""
        return ROLE_PERMISSIONS.get(role, set())

    @staticmethod
    def has_permission(role: Role, permission: str) -> bool:
        """
        Check if a role has a specific permission.
        
        Args:
            role: User's role
            permission: Permission to check (e.g., "users:write")
            
        Returns:
            True if role has the permission
        """
        permissions = PermissionService.get_role_permissions(role)
        return permission in permissions

    @staticmethod
    def has_any_permission(role: Role, permissions: List[str]) -> bool:
        """Check if role has any of the given permissions."""
        role_perms = PermissionService.get_role_permissions(role)
        return bool(role_perms & set(permissions))

    @staticmethod
    def has_all_permissions(role: Role, permissions: List[str]) -> bool:
        """Check if role has all of the given permissions."""
        role_perms = PermissionService.get_role_permissions(role)
        return set(permissions).issubset(role_perms)

    @staticmethod
    def is_higher_role(role1: Role, role2: Role) -> bool:
        """
        Check if role1 is higher than role2 in hierarchy.
        
        Args:
            role1: First role
            role2: Second role
            
        Returns:
            True if role1 > role2
        """
        return ROLE_HIERARCHY.get(role1, 0) > ROLE_HIERARCHY.get(role2, 0)

    @staticmethod
    def can_manage_role(manager_role: Role, target_role: Role) -> bool:
        """
        Check if manager can manage users with target role.
        
        Managers can only manage users with lower roles.
        """
        return PermissionService.is_higher_role(manager_role, target_role)

    @staticmethod
    def check_tenant_access(
        user_role: Role,
        user_org_id: Optional[str],
        target_org_id: str,
    ) -> bool:
        """
        Check if user can access resources in target organization.
        
        - Super Admin: Access all orgs
        - Analyst: Access assigned orgs (handled separately)
        - Client Admin/Assessor: Access own org only
        """
        if user_role == Role.SUPER_ADMIN:
            return True
        
        # Analyst access is checked via AnalystOrgAssignment
        if user_role == Role.ANALYST:
            # This should be checked against assignments in DB
            return True  # Placeholder - actual check in middleware
        
        # Client Admin and Assessor: own org only
        return user_org_id == target_org_id

    @staticmethod
    def get_allowed_roles_for_invite(inviter_role: Role) -> List[Role]:
        """
        Get roles that can be assigned by the inviter.
        
        - Super Admin: Can invite any role
        - Analyst: Cannot invite (no users:invite permission)
        - Client Admin: Can invite Client Admin and Assessor
        """
        if inviter_role == Role.SUPER_ADMIN:
            return list(Role)
        elif inviter_role == Role.CLIENT_ADMIN:
            return [Role.CLIENT_ADMIN, Role.ASSESSOR]
        else:
            return []


# Permission decorator factory for routes
def require_permission(permission: str):
    """
    Decorator to require a specific permission.
    
    Usage:
        @require_permission("users:write")
        async def update_user(...):
            ...
    """
    def decorator(func):
        func._required_permission = permission
        return func
    return decorator


def require_any_permission(*permissions: str):
    """
    Decorator to require any of the given permissions.
    
    Usage:
        @require_any_permission("users:read", "users:write")
        async def get_users(...):
            ...
    """
    def decorator(func):
        func._required_permissions = list(permissions)
        func._permission_mode = "any"
        return func
    return decorator


def require_roles(*roles: Role):
    """
    Decorator to require specific roles.
    
    Usage:
        @require_roles(Role.SUPER_ADMIN, Role.ANALYST)
        async def admin_function(...):
            ...
    """
    def decorator(func):
        func._required_roles = list(roles)
        return func
    return decorator
