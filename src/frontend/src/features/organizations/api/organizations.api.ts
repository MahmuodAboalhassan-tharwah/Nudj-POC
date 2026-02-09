import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/api-client';
import { Organization, OrganizationCreatePayload, OrganizationUpdatePayload, OrganizationListParams } from '../types/organization.types';

export const useOrganizations = (params?: OrganizationListParams) => {
    return useQuery({
        queryKey: ['organizations', params],
        queryFn: async () => {
            const response = await apiClient.get<Organization[]>('/organizations', { params });
            return response.data;
        },
    });
};

export const useOrganization = (id: string) => {
    return useQuery({
        queryKey: ['organization', id],
        queryFn: async () => {
            const response = await apiClient.get<Organization>(`/organizations/${id}`);
            return response.data;
        },
        enabled: !!id,
    });
};

export const useCreateOrganization = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (data: OrganizationCreatePayload) => {
            const response = await apiClient.post<Organization>('/organizations', data);
            return response.data;
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
    });
};

export const useUpdateOrganization = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async ({ id, data }: { id: string; data: OrganizationUpdatePayload }) => {
            const response = await apiClient.put<Organization>(`/organizations/${id}`, data);
            return response.data;
        },
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
            queryClient.invalidateQueries({ queryKey: ['organization', data.id] });
        },
    });
};

export const useDeleteOrganization = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (id: string) => {
            await apiClient.delete(`/organizations/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['organizations'] });
        },
    });
};
