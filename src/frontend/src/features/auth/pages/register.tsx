import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useInvitationToken } from '@/features/auth/hooks/use-invitation-token';
import { RegistrationForm } from '@/features/auth/components/registration-form';
import { OTPVerification } from '@/features/auth/components/otp-verification';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';

export const RegisterPage = () => {
    const { t } = useTranslation();
    const location = useLocation();
    const navigate = useNavigate();
    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get('token');

    const [step, setStep] = useState<'form' | 'otp' | 'complete'>('form');
    
    // Validate token
    const { data: invitation, isLoading, error } = useInvitationToken(token);

    useEffect(() => {
        if (!token) {
             // No token provided
            navigate('/login');
        } else if (error || (invitation && !invitation.is_valid)) {
            // Token invalid or expired
            navigate(`/invitation-expired?token=${token}`);
        }
    }, [token, invitation, error, navigate]);

    const handleRegistrationSuccess = () => {
        setStep('otp');
    };

    if (isLoading) {
        return (
            <div className="flex bg-background h-screen items-center justify-center">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    if (!invitation?.is_valid) return null; // Will redirect via useEffect

    return (
        <div className="flex min-h-screen items-center justify-center p-4 bg-muted/40">
            <Card className="w-full max-w-lg">
                <CardHeader className="text-center">
                    <CardTitle className="text-2xl font-bold">
                        {step === 'form' 
                            ? t('auth.register.title', 'Create Account') 
                            : t('auth.otp.title', 'Verify Phone')}
                    </CardTitle>
                    <CardDescription>
                        {step === 'form' 
                            ? t('auth.register.subtitle', 'Complete your registration to join {{org}}', { org: invitation.organization_name || 'Nudj' })
                            : t('auth.otp.subtitle', 'We sent a verification code to your phone')}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {step === 'form' ? (
                        <RegistrationForm 
                            invitationToken={token!} 
                            defaultEmail={invitation.email}
                            onSuccess={handleRegistrationSuccess}
                        />
                    ) : (
                        <OTPVerification 
                            onVerify={(code) => {
                                // TODO: Implement OTP verify mutation
                                console.log('Verify OTP', code);
                                navigate('/');
                            }} 
                            isLoading={false} 
                        />
                    )}
                </CardContent>
            </Card>
        </div>
    );
};
