import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/lib/api';
import { Comment, CommentCreate } from '../types';

export const commentKeys = {
    all: ['comments'] as const,
    byResponse: (responseId: string) => [...commentKeys.all, 'response', responseId] as const,
};

export function useComments(responseId: string) {
    return useQuery({
        queryKey: commentKeys.byResponse(responseId),
        queryFn: async () => {
            const response = await api.get<Comment[]>(`/comments/response/${responseId}`);
            return response.data;
        },
        enabled: !!responseId,
    });
}

export function useAddComment() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: async (data: CommentCreate) => {
            const response = await api.post<Comment>('/comments/', data);
            return response.data;
        },
        onSuccess: (newComment) => {
            queryClient.invalidateQueries({
                queryKey: commentKeys.byResponse(newComment.response_id),
            });
        },
    });
}
