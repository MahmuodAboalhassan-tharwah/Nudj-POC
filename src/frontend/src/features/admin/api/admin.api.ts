import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import {
    UserListItem,
    PaginatedUsers,
    InviteUserRequest,
    PaginatedAuditLogs,
    UpdateUserRequest
} from '../../admin/types/admin.types';

// =============================================================================
// User Management
// =============================================================================

export const useUsers = (params: { page: number; pageSize: number; role?: string; search?: string; organization_id?: string }) => {
    return useQuery({
        queryKey: ['users', params],
        queryFn: async () => {
            const response = await apiClient.get<PaginatedUsers>('/admin/users', { params });
            return response.data;
        },
        keepPreviousData: true,
    });
};

export const useUser = (userId: string) => {
    return useQuery({
        queryKey: ['user', userId],
        queryFn: async () => {
            const response = await apiClient.get<UserListItem>(`/admin/users/${userId}`);
            return response.data;
        },
        enabled: !!userId,
    });
};

export const useInviteUser = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: InviteUserRequest) => {
            const response = await apiClient.post('/admin/users/invite', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
        }
    });
};

export const useUpdateUser = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ userId, data }: { userId: string; data: UpdateUserRequest }) => {
            const response = await apiClient.patch(`/admin/users/${userId}`, data);
            return response.data;
        },
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            queryClient.invalidateQueries({ queryKey: ['user', variables.userId] });
        }
    });
};

export const useDeactivateUser = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (userId: string) => {
            await apiClient.delete(`/admin/users/${userId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
        }
    });
};

export const useBulkInvite = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: { invitations: InviteUserRequest[] }) => {
            const response = await apiClient.post('/admin/users/invite/bulk', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
        }
    });
};

// =============================================================================
// Audit Logs
// =============================================================================

export const useAuditLogs = (params: { page: number; pageSize: number; event_type?: string; user_id?: string }) => {
    return useQuery({
        queryKey: ['auditLogs', params],
        queryFn: async () => {
            const response = await apiClient.get<PaginatedAuditLogs>('/admin/audit-logs', { params });
            return response.data;
        },
        keepPreviousData: true,
    });
};

export const useExportAuditLogs = () => {
    return useMutation({
        mutationFn: async (params: { start_date?: string; end_date?: string }) => {
            const response = await apiClient.get('/admin/audit-logs/export', {
                params,
                responseType: 'blob'
            });

            // Create download link
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'audit_logs.csv');
            document.body.appendChild(link);
            link.click();
            link.remove();
        },
    });
};
