import { useTranslation } from 'react-i18next';
import { LoginForm } from '@/features/auth/components/login-form';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/shared/hooks/use-auth';
import { Navigate } from 'react-router-dom';

export const LoginPage = () => {
    const { t } = useTranslation();
    const { isAuthenticated } = useAuth();

    if (isAuthenticated) {
        return <Navigate to="/" replace />;
    }

    return (
        <div className="flex min-h-screen items-center justify-center p-4 bg-muted/40">
            <Card className="w-full max-w-md">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">
                        {t('auth.login.title', 'Welcome Back')}
                    </CardTitle>
                    <CardDescription>
                        {t('auth.login.subtitle', 'Sign in to access your dashboard')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <LoginForm />
                </CardContent>
            </Card>
        </div>
    );
};
