import { useAuthStore } from '../../features/auth/store/auth.store';
import { useCurrentUser } from '../../features/auth/api/auth.api';
import { Role } from '../../features/auth/types/auth.types';

export const useAuth = () => {
    const { user, isAuthenticated, isLoading: isStoreLoading } = useAuthStore();
    const { data: remoteUser, isLoading: isQueryLoading } = useCurrentUser();

    const currentUser = remoteUser || user;
    const isLoading = isStoreLoading || isQueryLoading;

    const hasRole = (roles: Role | Role[]) => {
        if (!currentUser) return false;
        const requiredRoles = Array.isArray(roles) ? roles : [roles];
        return requiredRoles.includes(currentUser.role);
    };

    const hasPermission = (permission: string) => {
        if (!currentUser) return false;
        return currentUser.permissions.includes(permission);
    };

    const isSuperAdmin = currentUser?.role === 'super_admin';
    const isClientAdmin = currentUser?.role === 'client_admin';
    const isAnalyst = currentUser?.role === 'analyst';
    const isAssessor = currentUser?.role === 'assessor';

    return {
        user: currentUser,
        isAuthenticated,
        isLoading,
        hasRole,
        hasPermission,
        isSuperAdmin,
        isClientAdmin,
        isAnalyst,
        isAssessor,
        organizationId: currentUser?.organization_id,
    };
};
