import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2 } from 'lucide-react';

interface CommentInputProps {
  placeholder?: string;
  submitLabel?: string;
  isPending?: boolean;
  onSubmit: (content: string) => void;
  autoFocus?: boolean;
  onCancel?: () => void;
}

export const CommentInput = ({
  placeholder = "Write a comment...",
  submitLabel = "Post",
  isPending = false,
  onSubmit,
  autoFocus = false,
  onCancel
}: CommentInputProps) => {
  const { t } = useTranslation();
  const [content, setContent] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (content.trim()) {
      onSubmit(content);
      setContent('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <Textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        disabled={isPending}
        className="min-h-[80px] resize-none border-slate-200 focus:ring-primary/20 transition-all rounded-xl text-sm"
      />
      <div className="flex justify-end gap-2">
        {onCancel && (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onCancel}
            disabled={isPending}
            className="text-slate-500 font-medium"
          >
            {t('common.cancel')}
          </Button>
        )}
        <Button
          type="submit"
          size="sm"
          disabled={!content.trim() || isPending}
          className="shadow-md shadow-primary/10"
        >
          {isPending ? (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          ) : (
            <Send className="h-4 w-4 mr-2" />
          )}
          {submitLabel}
        </Button>
      </div>
    </form>
  );
};
