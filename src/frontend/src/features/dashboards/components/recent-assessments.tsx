import { Link } from "react-router-dom";
import { format } from "date-fns";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { AssessmentSummary } from "../types/dashboard.types";

interface RecentAssessmentsProps {
  assessments: AssessmentSummary[];
  role: 'super_admin' | 'client_admin';
}

export function RecentAssessments({ assessments, role }: RecentAssessmentsProps) {
  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-3">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Recent Assessments</CardTitle>
        <Button variant="outline" size="sm" asChild>
          <Link to="/assessments">View All</Link>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {assessments.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No recent assessments found.
            </p>
          ) : (
            assessments.map((assessment) => (
              <div
                key={assessment.id}
                className="group flex items-center justify-between p-3 rounded-lg border border-transparent transition-all duration-200 hover:bg-slate-50 hover:border-slate-100"
              >
                <div className="space-y-1">
                  <p className="text-sm font-semibold leading-none group-hover:text-primary transition-colors">
                    {role === 'super_admin' ? assessment.organization_name : 'Assessment'}
                  </p>
                  <p className="text-[11px] text-muted-foreground">
                    Updated {format(new Date(assessment.updated_at), "MMM d, yyyy")}
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <Badge variant={assessment.status === "completed" ? "default" : "secondary"} className="capitalize">
                    {assessment.status}
                  </Badge>
                  <div className="text-sm font-bold w-12 text-right text-slate-700">
                    {assessment.score ? `${assessment.score}%` : "-"}
                  </div>
                  <Button variant="ghost" size="sm" asChild className="opacity-0 group-hover:opacity-100 transition-opacity">
                     <Link to={`/assessments/${assessment.id}`}>View</Link>
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
