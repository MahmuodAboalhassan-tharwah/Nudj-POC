import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';

import { useLogin } from '@/features/auth/api/auth.api';
import { useAuthStore } from '@/features/auth/store/auth.store';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { SSOButtons } from './sso-buttons';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
  rememberMe: z.boolean().optional(),
});

type LoginFormData = z.infer<typeof loginSchema>;

export const LoginForm = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState<string | null>(null);
  
  const { mutate: login, isPending } = useLogin();
  const { setAuth } = useAuthStore();
  
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
        email: '',
        password: '',
        rememberMe: false,
    }
  });

  const onSubmit = (data: LoginFormData) => {
    setServerError(null);
    login(
      {
        email: data.email,
        password: data.password,
        remember_me: data.rememberMe || false,
      },
      {
        onSuccess: (response) => {
            if (response.requires_mfa && response.mfa_token) {
                // Redirect to MFA verify page with temp token
                navigate('/mfa-verify', { state: { mfaToken: response.mfa_token } });
            } else if (response.user && response.access_token && response.refresh_token) {
                // Complete login
                setAuth(response.user, response.access_token, response.refresh_token);
                navigate('/');
            }
        },
        onError: (error: any) => {
            const errorCode = error.response?.data?.error?.code;
            if (errorCode === 'ACCOUNT_LOCKED') {
                // Handle specific locked error
                setServerError(t('auth.errors.accountLocked', 'Account is locked. Please try again later.'));
            } else {
                setServerError(t('auth.errors.invalidCredentials', 'Invalid email or password'));
            }
        },
      }
    );
  };

  return (
    <div className="w-full max-w-md space-y-6">
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {serverError && (
            <Alert variant="destructive">
            <AlertDescription>{serverError}</AlertDescription>
            </Alert>
        )}

        <div className="space-y-2">
            <Label htmlFor="email">{t('auth.login.email', 'Email')}</Label>
            <Input id="email" type="email" {...register('email')} />
            {errors.email && <p className="text-sm text-destructive">{errors.email.message}</p>}
        </div>

        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <Label htmlFor="password">{t('auth.login.password', 'Password')}</Label>
                <Link to="/forgot-password" className="text-sm text-primary hover:underline">
                    {t('auth.login.forgotPassword', 'Forgot password?')}
                </Link>
            </div>
            <Input id="password" type="password" {...register('password')} />
            {errors.password && <p className="text-sm text-destructive">{errors.password.message}</p>}
        </div>

        <div className="flex items-center space-x-2">
            <Checkbox id="rememberMe" {...register('rememberMe')} />
            <Label htmlFor="rememberMe" className="text-sm font-normal">
                {t('auth.login.rememberMe', 'Remember me')}
            </Label>
        </div>

        <Button type="submit" className="w-full" disabled={isPending}>
            {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {t('auth.login.submit', 'Sign In')}
        </Button>
        </form>

        <div className="relative">
            <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-background px-2 text-muted-foreground">
                    {t('auth.login.orContinueWith', 'Or continue with')}
                </span>
            </div>
        </div>

        <SSOButtons />
    </div>
  );
};
