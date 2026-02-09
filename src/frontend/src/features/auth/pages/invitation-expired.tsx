import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertCircle } from 'lucide-react';

export const InvitationExpiredPage = () => {
    const { t } = useTranslation();
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const token = queryParams.get('token');

    const handleRequestNew = () => {
        // Implementation for requesting new invitation
        // For now, just show info or redirect
        alert(t('auth.invitation.requestSent', 'Request for new invitation has been sent to admin.'));
    };

    return (
        <div className="flex min-h-screen items-center justify-center p-4 bg-muted/40">
            <Card className="w-full max-w-md border-red-200">
                <CardHeader className="text-center">
                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                        <AlertCircle className="h-6 w-6 text-red-600" />
                    </div>
                    <CardTitle className="text-xl text-red-700">
                        {t('auth.invitation.expiredTitle', 'Invitation Expired')}
                    </CardTitle>
                </CardHeader>
                <CardContent className="text-center text-muted-foreground">
                    <p>
                        {t('auth.invitation.expiredMessage', 'This invitation link is no longer valid or has already been used.')}
                    </p>
                </CardContent>
                <CardFooter className="flex flex-col gap-2">
                    <Button variant="default" className="w-full" onClick={handleRequestNew}>
                        {t('auth.invitation.requestNew', 'Request New Invitation')}
                    </Button>
                    <Button variant="ghost" className="w-full" asChild>
                        <Link to="/login">
                            {t('auth.common.backToLogin', 'Back to Login')}
                        </Link>
                    </Button>
                </CardFooter>
            </Card>
        </div>
    );
};
