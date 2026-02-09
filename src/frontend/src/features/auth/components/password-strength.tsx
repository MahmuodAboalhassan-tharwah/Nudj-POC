import { Progress } from '@/components/ui/progress';

interface PasswordStrengthProps {
  password?: string;
}

export const PasswordStrength = ({ password = '' }: PasswordStrengthProps) => {
  const calculateStrength = (pwd: string) => {
    if (!pwd) return 0;
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (/[A-Z]/.test(pwd)) strength += 25;
    if (/[0-9]/.test(pwd)) strength += 25;
    if (/[^A-Za-z0-9]/.test(pwd)) strength += 25;
    return strength;
  };

  const strength = calculateStrength(password);

  const getColor = (score: number) => {
    if (score < 50) return 'bg-destructive';
    if (score < 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-1 mt-2">
      <Progress value={strength} className={`h-1 ${getColor(strength)}`} />
      <p className="text-xs text-muted-foreground text-right w-full">
        {strength < 50 ? 'Weak' : strength < 75 ? 'Medium' : 'Strong'}
      </p>
    </div>
  );
};
