import { Card, CardContent } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function StatsCard({ title, value, description, icon, className }: StatsCardProps) {
  return (
    <Card className={cn(
      "overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 border-l-4 border-l-primary/50", 
      className
    )}>
      <CardContent className="p-6">
        <div className="flex items-center justify-between space-y-0 pb-2">
          <p className="text-sm font-medium text-muted-foreground uppercase tracking-wider">{title}</p>
          {icon && <div className="text-primary/70">{icon}</div>}
        </div>
        <div className="text-3xl font-bold tracking-tight">{value}</div>
        {description && (
          <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
            <span className="inline-block h-1 w-1 rounded-full bg-primary/40" />
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
