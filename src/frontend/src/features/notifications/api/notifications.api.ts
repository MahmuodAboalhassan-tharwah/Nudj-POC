import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Notification } from '@/features/notifications/types/notification.types';

export const notificationKeys = {
    all: ['notifications'] as const,
    list: () => [...notificationKeys.all, 'list'] as const,
    unreadCount: () => [...notificationKeys.all, 'unreadCount'] as const,
};

export function useNotifications(limit = 20) {
    return useQuery({
        queryKey: notificationKeys.list(),
        queryFn: async () => {
            const { data } = await api.get<Notification[]>('/notifications', {
                params: { limit }
            });
            return data;
        },
        refetchInterval: 30000, // Poll every 30s
    });
}

export function useUnreadCount() {
    return useQuery({
        queryKey: notificationKeys.unreadCount(),
        queryFn: async () => {
            const { data } = await api.get<{ count: number }>('/notifications/unread-count');
            return data.count;
        },
        refetchInterval: 30000, // Poll every 30s
    });
}

export function useMarkAsRead() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (notificationId: string) => {
            const { data } = await api.patch<Notification>(`/notifications/${notificationId}/read`);
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: notificationKeys.all });
        },
    });
}

export function useMarkAllAsRead() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async () => {
            const { data } = await api.patch<{ updated_count: number }>('/notifications/read-all');
            return data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: notificationKeys.all });
        },
    });
}
