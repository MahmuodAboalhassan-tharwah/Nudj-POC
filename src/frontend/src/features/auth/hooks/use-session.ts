import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import { Session } from '../types/auth.types';

export const useSession = () => {
    const queryClient = useQueryClient();

    const { data: sessions, isLoading } = useQuery({
        queryKey: ['sessions'],
        queryFn: async () => {
            const response = await apiClient.get<{ sessions: Session[] }>('/auth/sessions');
            return response.data.sessions;
        },
    });

    const revokeSession = useMutation({
        mutationFn: async (sessionId: string) => {
            await apiClient.delete(`/auth/sessions/${sessionId}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sessions'] });
        },
    });

    const revokeAllSessions = useMutation({
        mutationFn: async () => {
            await apiClient.delete('/auth/sessions');
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['sessions'] });
        },
    });

    return {
        sessions,
        isLoading,
        revokeSession: revokeSession.mutate,
        revokeAllSessions: revokeAllSessions.mutate,
        isRevoking: revokeSession.isPending || revokeAllSessions.isPending,
    };
};
