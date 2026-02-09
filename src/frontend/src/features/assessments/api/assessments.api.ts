import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/api-client';
import {
    Assessment,
    AssessmentCreatePayload,
    AssessmentResponse,
    AssessmentUpdatePayload,
    AssignDomainPayload,
    AssessmentDomain,
    SubmitElementResponsePayload,
    AssessmentElementResponse,
    AssessmentDelegation,
    CreateDelegationPayload
} from '../types/assessment.types';

// Keys
export const assessmentKeys = {
    all: ['assessments'] as const,
    lists: () => [...assessmentKeys.all, 'list'] as const,
    detail: (id: string) => [...assessmentKeys.all, 'detail', id] as const,
    delegations: (assessmentId: string) => [...assessmentKeys.all, 'delegations', assessmentId] as const,
};

// API Functions
const getAssessments = async (): Promise<Assessment[]> => {
    const response = await apiClient.get<Assessment[]>('/assessments');
    return response.data;
};

const getAssessment = async (id: string): Promise<Assessment> => {
    const response = await apiClient.get<Assessment>(`/assessments/${id}`);
    return response.data;
};

const createAssessment = async (payload: AssessmentCreatePayload): Promise<Assessment> => {
    const response = await apiClient.post<Assessment>('/assessments', payload);
    return response.data;
};

const updateAssessment = async ({ id, data }: { id: string; data: AssessmentUpdatePayload }): Promise<Assessment> => {
    const response = await apiClient.patch<Assessment>(`/assessments/${id}`, data);
    return response.data;
};

const assignDomain = async ({ assessmentId, domainId, assigneeId }: { assessmentId: string; domainId: string; assigneeId: string }): Promise<AssessmentDomain> => {
    const response = await apiClient.post<AssessmentDomain>(`/assessments/${assessmentId}/domains/${domainId}/assign?assignee_id=${assigneeId}`);
    return response.data;
};

const submitResponse = async ({ responseId, data }: { responseId: string; data: SubmitElementResponsePayload }): Promise<AssessmentElementResponse> => {
    const response = await apiClient.post<AssessmentElementResponse>(`/assessments/responses/${responseId}`, data);
    return response.data;
};

const uploadEvidence = async ({ responseId, file }: { responseId: string; file: File }): Promise<void> => {
    const formData = new FormData();
    formData.append('file', file);
    await apiClient.post(`/assessments/responses/${responseId}/evidence`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
};

const getDelegations = async (assessmentId: string): Promise<AssessmentDelegation[]> => {
    const response = await apiClient.get<AssessmentDelegation[]>(`/delegations/assessment/${assessmentId}`);
    return response.data;
};

const createDelegation = async (payload: CreateDelegationPayload): Promise<AssessmentDelegation> => {
    const response = await apiClient.post<AssessmentDelegation>('/delegations', payload);
    return response.data;
};

const revokeDelegation = async (id: string): Promise<void> => {
    await apiClient.delete(`/delegations/${id}`);
};

// Hooks
export const useAssessments = () => {
    return useQuery({
        queryKey: assessmentKeys.lists(),
        queryFn: getAssessments,
    });
};

export const useAssessment = (id: string, enabled = true) => {
    return useQuery({
        queryKey: assessmentKeys.detail(id),
        queryFn: () => getAssessment(id),
        enabled: !!id && enabled,
    });
};

export const useCreateAssessment = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: createAssessment,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
        },
    });
};

export const useUpdateAssessment = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: updateAssessment,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(data.id) });
            queryClient.invalidateQueries({ queryKey: assessmentKeys.lists() });
        },
    });
};

export const useAssignDomain = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: assignDomain,
        onSuccess: (data, variables) => {
            queryClient.invalidateQueries({ queryKey: assessmentKeys.detail(variables.assessmentId) });
        },
    });
};

export const useSubmitResponse = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: submitResponse,
        onSuccess: () => {
            // Invalidate assessment detail to refresh scores/progress
            // We might need assessmentId in context or variables to invalidate specifically
            queryClient.invalidateQueries({ queryKey: assessmentKeys.all });
        },
    });
};

export const useUploadEvidence = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: uploadEvidence,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: assessmentKeys.all });
        },
    });
};

export const useDelegations = (assessmentId: string) => {
    return useQuery({
        queryKey: assessmentKeys.delegations(assessmentId),
        queryFn: () => getDelegations(assessmentId),
        enabled: !!assessmentId,
    });
};

export const useCreateDelegation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: createDelegation,
        onSuccess: (data) => {
            queryClient.invalidateQueries({ queryKey: assessmentKeys.delegations(data.assessmentId) });
        },
    });
};

export const useRevokeDelegation = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: revokeDelegation,
        onSuccess: (_, id) => {
            // We might need to invalidate all delegations since we don't have the assessmentId here easily
            // or pass it in variables
            queryClient.invalidateQueries({ queryKey: assessmentKeys.all });
        },
    });
};
