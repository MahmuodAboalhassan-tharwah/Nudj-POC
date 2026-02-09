import { useAuth } from "@/features/auth/hooks/use-auth";
import { useClientDashboard } from "../api/dashboards.api";
import { StatsCard } from "../components/stats-card";
import { RecentAssessments } from "@/features/dashboards/components/recent-assessments";
import { Loader2 } from "lucide-react";
import { format } from "date-fns";

export function ClientDashboard() {
  const { user } = useAuth();
  const { data, isLoading, error } = useClientDashboard(user?.organization_id);

  if (isLoading) {
     return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 text-center text-destructive">
        Error loading dashboard data.
      </div>
    );
  }

  const stats = data?.stats || {
    total_assessments: 0,
    active_assessments: 0,
    completed_assessments: 0,
    average_score: 0,
    next_deadline: null
  };
  
  const active_assessments = data?.active_assessments || [];

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Organization Dashboard</h2>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Active Assessments"
          value={stats.active_assessments}
          description="Ongoing"
        />
        <StatsCard
          title="Completed Assessments"
          value={stats.completed_assessments}
          description="Past assessments"
        />
        <StatsCard
          title="Avg. Maturity Score"
          value={`${stats.average_score}%`}
          description="Of completed assessments"
        />
        <StatsCard
          title="Next Deadline"
          value={stats.next_deadline ? format(new Date(stats.next_deadline), "MMM d") : "None"}
          description="Upcoming due date"
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4">
           {/* Chart placeholder */}
            <div className="rounded-xl border bg-card text-card-foreground shadow h-[300px] flex items-center justify-center text-muted-foreground p-6">
                <div className="text-center">
                    <p className="font-semibold">Domain Performance</p>
                    <p className="text-sm">Radar chart coming soon</p>
                </div>
            </div>
        </div>
        <div className="col-span-3">
            <RecentAssessments assessments={active_assessments} role="client_admin" />
        </div>
      </div>
    </div>
  );
}
