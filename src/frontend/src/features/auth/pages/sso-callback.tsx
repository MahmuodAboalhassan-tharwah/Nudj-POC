import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '@/features/auth/store/auth.store';
import { Loader2 } from 'lucide-react';

export const SSOCallbackPage = () => {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const location = useLocation();
    const { setAuth } = useAuthStore();

    useEffect(() => {
        const handleCallback = async () => {
             // Mock implementation since backend SSO is stubbed
             // In real imp, we would parse params (code, state) and call backend
             // const params = new URLSearchParams(location.search);
             // const code = params.get('code');
             
             // Simulate API call delay
             setTimeout(() => {
                 // Mock success
                 console.log("SSO Callback processed");
                 navigate('/');
             }, 1000);
        };

        handleCallback();
    }, [location, navigate, setAuth]);

    return (
        <div className="flex min-h-screen items-center justify-center bg-muted/40">
            <div className="flex flex-col items-center space-y-4">
                <Loader2 className="h-10 w-10 animate-spin text-primary" />
                <p className="text-lg font-medium text-muted-foreground">
                    {t('auth.sso.processing', 'Signing in with SSO...')}
                </p>
            </div>
        </div>
    );
};
