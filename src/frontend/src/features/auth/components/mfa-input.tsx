import { InputOTP, InputOTPGroup, InputOTPSlot } from '@/components/ui/input-otp';
import { Label } from '@/components/ui/label';

interface MFAInputProps {
    value: string;
    onChange: (value: string) => void;
    label?: string;
    error?: string;
}

export const MFAInput = ({ value, onChange, label, error }: MFAInputProps) => {
    return (
        <div className="space-y-2 flex flex-col items-center">
            {label && <Label>{label}</Label>}
             <InputOTP maxLength={6} value={value} onChange={onChange}>
                <InputOTPGroup>
                    <InputOTPSlot index={0} />
                    <InputOTPSlot index={1} />
                    <InputOTPSlot index={2} />
                    <InputOTPSlot index={3} />
                    <InputOTPSlot index={4} />
                    <InputOTPSlot index={5} />
                </InputOTPGroup>
            </InputOTP>
            {error && <p className="text-sm text-destructive">{error}</p>}
        </div>
    );
};
