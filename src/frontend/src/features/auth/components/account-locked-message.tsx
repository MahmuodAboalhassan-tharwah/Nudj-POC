import { AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { useTranslation } from 'react-i18next';

interface AccountLockedMessageProps {
    lockedUntil?: string; // ISO date string
}

export const AccountLockedMessage = ({ lockedUntil }: AccountLockedMessageProps) => {
    const { t } = useTranslation();
    
    // Calculate waiting time if needed, or just show the time
    const formattedTime = lockedUntil 
        ? new Date(lockedUntil).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        : '';

    return (
        <Alert variant="destructive" className="border-red-600 bg-red-50 dark:bg-red-900/10">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{t('auth.accountLocked.title', 'Account Locked')}</AlertTitle>
            <AlertDescription>
                {t('auth.accountLocked.message', 'Your account has been temporarily locked due to multiple failed login attempts.')}
                {lockedUntil && (
                    <div className="mt-2 font-semibold">
                        {t('auth.accountLocked.tryAgainAfter', 'Please try again after {{time}}', { time: formattedTime })}
                    </div>
                )}
            </AlertDescription>
        </Alert>
    );
};
