import { cn } from '@/lib/utils';
import { AssessmentDomain } from '../types/assessment.types';
import { Progress } from '@/components/ui/progress';
import { useTranslation } from 'react-i18next';

interface DomainNavProps {
  domains: AssessmentDomain[];
  activeDomainId: string | null;
  onSelectDomain: (domainId: string) => void;
}

export const DomainNav = ({ domains, activeDomainId, onSelectDomain }: DomainNavProps) => {
  const { t } = useTranslation();

  return (
    <nav className="space-y-1">
      {domains.map((domain) => {
        const isActive = activeDomainId === domain.id;
        const domainName = t(`assessments.domainNames.${domain.domainId}`) || `Domain ${domain.domainId}`; 
        
        return (
          <button
            key={domain.id}
            onClick={() => onSelectDomain(domain.id)}
            className={cn(
              "w-full text-left px-3 py-2 rounded-md transition-colors flex flex-col gap-1",
              isActive 
                ? "bg-primary/10 text-primary font-medium" 
                : "hover:bg-muted text-foreground"
            )}
          >
            <div className="flex justify-between items-center w-full">
              <span>{domainName}</span>
              <span className="text-xs text-muted-foreground">{domain.score ? `${Math.round(domain.score)}%` : '-'}</span>
            </div>
            {/* Show progress for domain if we calculate it locally or use score */}
             <Progress value={domain.score || 0} className="h-1" />
          </button>
        );
      })}
    </nav>
  );
};
