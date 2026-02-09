export interface Comment {
    id: string;
    user_id: string;
    response_id: string;
    parent_id: string | null;
    content: string;
    created_at: string;
    author: {
        id: string;
        full_name: string;
        avatar_url: string | null;
    };
    replies: Comment[];
}

export interface CommentCreate {
    response_id: string;
    parent_id?: string | null;
    content: string;
}
