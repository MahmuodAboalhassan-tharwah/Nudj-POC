import { usePortfolioDashboard } from "../api/dashboards.api";
import { StatsCard } from "../components/stats-card";
import { RecentAssessments } from "@/features/dashboards/components/recent-assessments";
import { Loader2 } from "lucide-react";

export function SuperAdminDashboard() {
  const { data, isLoading, error } = usePortfolioDashboard();

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

  // Ensure data exists before destructuring
  const stats = data?.stats || {
    total_organizations: 0,
    total_users: 0,
    total_assessments: 0,
    average_maturity_score: 0,
    active_assessments_count: 0,
    completed_assessments_count: 0
  };
  
  const recent_assessments = data?.recent_assessments || [];

  return (
    <div className="flex-1 space-y-4 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="Total Organizations"
          value={stats.total_organizations}
          description="Active on platform"
        />
        <StatsCard
          title="Active Assessments"
          value={stats.active_assessments_count}
          description="In progress"
        />
        <StatsCard
          title="Completed Assessments"
          value={stats.completed_assessments_count}
          description="Total completed"
        />
        <StatsCard
          title="Avg. Maturity Score"
          value={`${stats.average_maturity_score}%`}
          description="Across all organizations"
        />
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4">
            {/* Chart placeholder */}
            <div className="rounded-xl border bg-card text-card-foreground shadow h-[300px] flex items-center justify-center text-muted-foreground p-6">
                <div className="text-center">
                    <p className="font-semibold">Maturity Distribution</p>
                    <p className="text-sm">Chart visualization coming soon</p>
                </div>
            </div>
        </div>
        <div className="col-span-3">
             <RecentAssessments assessments={recent_assessments} role="super_admin" />
        </div>
      </div>
    </div>
  );
}
