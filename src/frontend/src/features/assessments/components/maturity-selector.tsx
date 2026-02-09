import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';

interface MaturitySelectorProps {
  value: number | null;
  onChange: (value: number) => void;
  disabled?: boolean;
}

// LEVELS constant is replaced by dynamic translation in component

export const MaturitySelector = ({ value, onChange, disabled }: MaturitySelectorProps) => {
  const { t } = useTranslation();

  const levels = [1, 2, 3, 4].map(v => ({
    value: v,
    label: t(`assessments.maturityLevels.${v}.label`),
    description: t(`assessments.maturityLevels.${v}.description`)
  }));

  return (
    <RadioGroup
      value={value?.toString()}
      onValueChange={(val) => onChange(parseInt(val))}
      className="grid gap-2 sm:grid-cols-4"
      disabled={disabled}
    >
      {levels.map((level) => (
        <div key={level.value}>
          <RadioGroupItem
            value={level.value.toString()}
            id={`level-${level.value}`}
            className="peer sr-only"
          />
          <Label
            htmlFor={`level-${level.value}`}
            className={cn(
              "flex flex-col items-center justify-between rounded-xl border-2 border-slate-100 bg-white p-4 transition-all duration-300 shadow-sm h-full group cursor-pointer",
              "hover:border-primary/30 hover:shadow-md hover:-translate-y-0.5",
              "peer-data-[state=checked]:border-primary peer-data-[state=checked]:bg-primary/5 peer-data-[state=checked]:shadow-lg peer-data-[state=checked]:shadow-primary/10",
              disabled && "opacity-50 cursor-not-allowed grayscale"
            )}
          >
            <div className={cn(
              "w-10 h-10 rounded-full flex items-center justify-center mb-3 transition-colors",
              "bg-slate-50 group-hover:bg-primary/10 text-slate-400 group-hover:text-primary",
              "peer-data-[state=checked]:bg-primary peer-data-[state=checked]:text-white"
            )}>
              <span className="text-lg font-bold">{level.value}</span>
            </div>
            <span className={cn(
               "text-sm font-bold text-center transition-colors",
               "text-slate-700 peer-data-[state=checked]:text-primary"
            )}>
              {level.label}
            </span>
            <span className="text-[11px] font-medium text-slate-500 text-center mt-2 leading-tight">
              {level.description}
            </span>
          </Label>
        </div>
      ))}
    </RadioGroup>
  );
};
