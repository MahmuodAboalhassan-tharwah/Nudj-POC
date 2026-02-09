import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useTranslation } from 'react-i18next';
import { Loader2 } from 'lucide-react';

import { useRegister } from '@/features/auth/api/auth.api';
// Assuming UI components exist or using standard HTML for now
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { PasswordStrength } from './password-strength'; // We'll create this next

interface RegistrationFormProps {
  invitationToken: string;
  defaultEmail?: string;
  onSuccess: () => void;
}

const registerSchema = z.object({
  name_en: z.string().min(2, 'Name (English) is required'),
  name_ar: z.string().min(2, 'Name (Arabic) is required'),
  phone_sa: z.string().regex(/^\+966[0-9]{9}$/, 'Invalid Saudi phone number (+966...)').optional(),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

type RegisterFormData = z.infer<typeof registerSchema>;

export const RegistrationForm = ({ invitationToken, defaultEmail, onSuccess }: RegistrationFormProps) => {
  const { t } = useTranslation();
  const [serverError, setServerError] = useState<string | null>(null);
  
  const { mutate: register, isPending } = useRegister();
  
  const {
    register: registerField,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
        name_en: '',
        name_ar: '',
        phone_sa: '',
        password: '',
        confirmPassword: '',
    }
  });

  const password = watch('password');

  const onSubmit = (data: RegisterFormData) => {
    setServerError(null);
    register(
      {
        token: invitationToken,
        password: data.password,
        name_en: data.name_en,
        name_ar: data.name_ar,
        phone_sa: data.phone_sa, // Optional
      },
      {
        onSuccess: () => {
          onSuccess();
        },
        onError: (error: any) => {
          setServerError(error.response?.data?.error?.message_en || 'Registration failed');
        },
      }
    );
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {serverError && (
        <Alert variant="destructive">
          <AlertDescription>{serverError}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label>Email</Label>
        <Input value={defaultEmail} disabled className="bg-muted" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="name_en">Name (English)</Label>
          <Input id="name_en" {...registerField('name_en')} />
          {errors.name_en && <p className="text-sm text-destructive">{errors.name_en.message}</p>}
        </div>
        <div className="space-y-2">
          <Label htmlFor="name_ar">Name (Arabic)</Label>
          <Input id="name_ar" {...registerField('name_ar')} dir="rtl" />
          {errors.name_ar && <p className="text-sm text-destructive">{errors.name_ar.message}</p>}
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="phone_sa">Phone (Optional)</Label>
        <Input id="phone_sa" placeholder="+966..." {...registerField('phone_sa')} />
        {errors.phone_sa && <p className="text-sm text-destructive">{errors.phone_sa.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password</Label>
        <Input id="password" type="password" {...registerField('password')} />
        <PasswordStrength password={password} />
        {errors.password && <p className="text-sm text-destructive">{errors.password.message}</p>}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm Password</Label>
        <Input id="confirmPassword" type="password" {...registerField('confirmPassword')} />
        {errors.confirmPassword && <p className="text-sm text-destructive">{errors.confirmPassword.message}</p>}
      </div>

      <Button type="submit" className="w-full" disabled={isPending}>
        {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {t('auth.register.submit', 'Complete Registration')}
      </Button>
    </form>
  );
};
