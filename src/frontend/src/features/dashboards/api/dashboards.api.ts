import { useQuery } from '@tanstack/react-query';
import { api } from '@/shared/lib/api';
import { PortfolioDashboardResponse, ClientDashboardResponse } from '../types/dashboard.types';

export const dashboardKeys = {
    all: ['dashboards'] as const,
    portfolio: () => [...dashboardKeys.all, 'portfolio'] as const,
    organization: (id: string) => [...dashboardKeys.all, 'organization', id] as const,
};

export function usePortfolioDashboard() {
    return useQuery({
        queryKey: dashboardKeys.portfolio(),
        queryFn: async () => {
            const { data } = await api.get<PortfolioDashboardResponse>('/dashboards/portfolio');
            return data;
        },
    });
}

export function useClientDashboard(organizationId: string | undefined) {
    return useQuery({
        queryKey: dashboardKeys.organization(organizationId || ''),
        queryFn: async () => {
            if (!organizationId) throw new Error('Organization ID is required');
            const { data } = await api.get<ClientDashboardResponse>(`/dashboards/organization/${organizationId}`);
            return data;
        },
        enabled: !!organizationId,
    });
}
