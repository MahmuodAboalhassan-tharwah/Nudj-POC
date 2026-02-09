import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export interface FrameworkDomainConfig {
    id: string;
    domain_id: number;
    name_en: string;
    name_ar: string;
    description_en?: string;
    description_ar?: string;
    default_weight: number;
}

export interface FrameworkDomainConfigUpdate {
    default_weight: number;
}

export const useFrameworkDomains = () => {
    return useQuery({
        queryKey: ['framework-domains'],
        queryFn: async () => {
            const response = await api.get<FrameworkDomainConfig[]>('/framework/domains');
            return response.data;
        },
    });
};

export const useUpdateDomainWeight = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async ({ domainId, data }: { domainId: number; data: FrameworkDomainConfigUpdate }) => {
            const response = await api.patch<FrameworkDomainConfig>(`/framework/domains/${domainId}`, data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['framework-domains'] });
        },
    });
};
