import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { formatDistanceToNow } from 'date-fns';
import { MessageSquare, Reply } from 'lucide-react';
import { Comment } from '../types';
import { CommentInput } from './comment-input';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface CommentItemProps {
  comment: Comment;
  onReply: (parentId: string, content: string) => void;
  isReplying?: boolean;
}

export const CommentItem = ({ comment, onReply, isReplying = false }: CommentItemProps) => {
  const { t } = useTranslation();
  const [showReplyInput, setShowReplyInput] = useState(false);

  const handleReplySubmit = (content: string) => {
    onReply(comment.id, content);
    setShowReplyInput(false);
  };

  return (
    <div className="group space-y-3">
      <div className="flex gap-3">
        {/* User Avatar Placeholder */}
        <div className="h-8 w-8 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0">
          <span className="text-[10px] font-bold text-slate-500 uppercase">
            {comment.author.full_name?.[0] || 'U'}
          </span>
        </div>

        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-slate-800">{comment.author.full_name}</span>
            <span className="text-[10px] font-medium text-slate-400">
              {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
            </span>
          </div>
          <p className="text-sm text-slate-600 leading-relaxed font-medium">
            {comment.content}
          </p>
          
          <div className="flex items-center gap-4 pt-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-auto p-0 text-xs font-bold text-primary/70 hover:text-primary bg-transparent hover:bg-transparent flex items-center gap-1.5"
              onClick={() => setShowReplyInput(!showReplyInput)}
            >
              <Reply className="h-3 w-3" />
              {t('comments.reply')}
            </Button>
            
            {comment.replies && comment.replies.length > 0 && (
               <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase tracking-tighter">
                 <MessageSquare className="h-3 w-3" />
                 {comment.replies.length} {comment.replies.length === 1 ? t('comments.replySingular') : t('comments.replies')}
               </div>
            )}
          </div>
        </div>
      </div>

      {showReplyInput && (
        <div className="ml-11">
          <CommentInput
            placeholder={`${t('comments.replyTo')} ${comment.author.full_name}...`}
            submitLabel={t('comments.reply')}
            isPending={isReplying}
            onSubmit={handleReplySubmit}
            onCancel={() => setShowReplyInput(false)}
            autoFocus
          />
        </div>
      )}

      {/* Nested Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-11 space-y-4 border-l-2 border-slate-100 pl-4 py-2">
          {comment.replies.map((reply) => (
            <CommentItem 
              key={reply.id} 
              comment={reply} 
              onReply={onReply} 
              isReplying={isReplying}
            />
          ))}
        </div>
      )}
    </div>
  );
};
