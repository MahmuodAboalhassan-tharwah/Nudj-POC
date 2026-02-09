import { Skeleton } from '@/components/ui/skeleton';
import { useTranslation } from 'react-i18next';
import { useComments, useAddComment } from '../api/comments.api';
import { CommentItem } from './comment-item';
import { CommentInput } from './comment-input';
import { MessageSquareOff } from 'lucide-react';

interface CommentThreadProps {
  responseId: string;
}

export const CommentThread = ({ responseId }: CommentThreadProps) => {
  const { t } = useTranslation();
  const { data: comments, isLoading } = useComments(responseId);
  const addComment = useAddComment();

  const handleAddComment = (content: string) => {
    addComment.mutate({
      response_id: responseId,
      content,
      parent_id: null
    });
  };

  const handleReply = (parentId: string, content: string) => {
    addComment.mutate({
      response_id: responseId,
      content,
      parent_id: parentId
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        {[1, 2].map((i) => (
          <div key={i} className="flex gap-3">
            <Skeleton className="h-8 w-8 rounded-full shrink-0" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-24" />
              <Skeleton className="h-4 w-full" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Top-level Input */}
      <CommentInput 
        onSubmit={handleAddComment} 
        isPending={addComment.isPending} 
        placeholder={t('comments.placeholder')}
        submitLabel={t('comments.submit')}
      />

      {/* Comment List */}
      <div className="space-y-8">
        {!comments || comments.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-slate-400">
             <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mb-3">
                <MessageSquareOff className="h-6 w-6 text-slate-200" />
             </div>
             <p className="text-sm font-medium">{t('comments.noComments')}</p>
             <p className="text-xs">{t('comments.beFirst')}</p>
          </div>
        ) : (
          comments.map((comment) => (
            <CommentItem 
              key={comment.id} 
              comment={comment} 
              onReply={handleReply}
              isReplying={addComment.isPending}
            />
          ))
        )}
      </div>
    </div>
  );
};
