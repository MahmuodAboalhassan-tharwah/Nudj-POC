import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/shared/lib/api-client';
import { useAuthStore } from '../store/auth.store';
import {
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    MFAVerifyRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    User
} from '../types/auth.types';

// =============================================================================
// Queries
// =============================================================================

export const useCurrentUser = () => {
    const { setAuth, logout } = useAuthStore();

    return useQuery({
        queryKey: ['currentUser'],
        queryFn: async () => {
            const response = await apiClient.get<User>('/auth/me');
            return response.data;
        },
        retry: false,
        enabled: !!useAuthStore.getState().accessToken,
    });
};

// =============================================================================
// Mutations
// =============================================================================

export const useLogin = () => {
    return useMutation({
        mutationFn: async (data: LoginRequest) => {
            const response = await apiClient.post<LoginResponse>('/auth/login', data);
            return response.data;
        },
    });
};

export const useRegister = () => {
    return useMutation({
        mutationFn: async (data: RegisterRequest) => {
            const response = await apiClient.post<LoginResponse>('/auth/register', data);
            return response.data;
        },
    });
};

export const useVerifyMFA = () => {
    return useMutation({
        mutationFn: async (data: MFAVerifyRequest) => {
            const response = await apiClient.post<LoginResponse>('/auth/mfa/verify', data);
            return response.data;
        },
    });
};

export const useLogout = () => {
    const { logout } = useAuthStore();
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async () => {
            await apiClient.post('/auth/logout');
        },
        onSuccess: () => {
            logout();
            queryClient.clear();
        },
        onError: () => {
            // Force logout even on error
            logout();
            queryClient.clear();
        }
    });
};

export const useForgotPassword = () => {
    return useMutation({
        mutationFn: async (data: ForgotPasswordRequest) => {
            await apiClient.post('/auth/forgot-password', data);
        },
    });
};

export const useResetPassword = () => {
    return useMutation({
        mutationFn: async (data: ResetPasswordRequest) => {
            await apiClient.post('/auth/reset-password', data);
        },
    });
};

export const useChangePassword = () => {
    return useMutation({
        mutationFn: async (data: ChangePasswordRequest) => {
            await apiClient.post('/auth/change-password', data);
        },
    });
};

export const useMFASetup = () => {
    return useQuery({
        queryKey: ['mfaSetup'],
        queryFn: async () => {
            const response = await apiClient.get('/auth/mfa/setup');
            return response.data;
        },
        enabled: false, // Manual trigger only
    });
};

export const useEnableMFA = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (code: string) => {
            await apiClient.post('/auth/mfa/enable', { code });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['currentUser'] });
        }
    });
};

export const useDisableMFA = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: async (code: string) => {
            await apiClient.post('/auth/mfa/disable', { code });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['currentUser'] });
        }
    });
};
