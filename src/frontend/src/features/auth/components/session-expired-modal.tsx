import { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useTranslation } from 'react-i18next';
import { useLogin } from '@/features/auth/api/auth.api';

interface SessionExpiredModalProps {
    isOpen: boolean;
    onClose: () => void;
}

export const SessionExpiredModal = ({ isOpen, onClose }: SessionExpiredModalProps) => {
    const { t } = useTranslation();
    const { mutate: login } = useLogin(); // Could be used for re-auth if extended
    
    const handleLoginRedirect = () => {
        onClose();
        window.location.href = '/login';
    };

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>{t('auth.session.expiredTitle', 'Session Expired')}</DialogTitle>
                    <DialogDescription>
                        {t('auth.session.expiredMessage', 'Your session has expired due to inactivity. Please log in again to continue.')}
                    </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                    <Button onClick={handleLoginRedirect}>
                        {t('auth.session.loginAgain', 'Log In Again')}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
};
