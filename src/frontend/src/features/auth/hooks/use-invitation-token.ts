import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import { InvitationValidateResponse } from '../types/auth.types';

export const useInvitationToken = (token: string | null) => {
    return useQuery({
        queryKey: ['invitation', token],
        queryFn: async () => {
            if (!token) return null;
            const response = await apiClient.get<InvitationValidateResponse>(`/auth/invitation/validate?token=${token}`);
            return response.data;
        },
        enabled: !!token,
        retry: false,
    });
};
