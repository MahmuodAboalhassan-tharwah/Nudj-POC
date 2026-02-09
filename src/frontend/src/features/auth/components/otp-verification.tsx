import { useState, useEffect } from 'react';
import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';

interface OTPVerificationProps {
    onVerify: (code: string) => void;
    isLoading: boolean;
    length?: number;
}

export const OTPVerification = ({ onVerify, isLoading, length = 6 }: OTPVerificationProps) => {
    const { t } = useTranslation();
    const [code, setCode] = useState('');

    const handleComplete = (value: string) => {
        onVerify(value);
    };

    return (
        <div className="space-y-4 flex flex-col items-center">
            <p className="text-sm text-muted-foreground text-center">
                {t('auth.otp.instruction', 'Enter the 6-digit code from your authenticator app')}
            </p>
            
            <InputOTP maxLength={length} value={code} onChange={setCode} onComplete={handleComplete}>
                <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                </InputOTPGroup>
            </InputOTP>

            <Button 
                onClick={() => onVerify(code)} 
                disabled={code.length !== length || isLoading}
                className="w-full"
            >
                {isLoading ? t('common.verifying', 'Verifying...') : t('auth.otp.verify', 'Verify Code')}
            </Button>
        </div>
    );
};
