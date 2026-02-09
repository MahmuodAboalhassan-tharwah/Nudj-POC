export type NotificationType = 'info' | 'success' | 'warning' | 'error' | 'action_required';

export interface Notification {
    id: string;
    user_id: string;
    title: string;
    message: string;
    type: NotificationType;
    link?: string;
    is_read: boolean;
    created_at: string;
}

export interface NotificationResponse {
    items: Notification[];
    total: number;
}
