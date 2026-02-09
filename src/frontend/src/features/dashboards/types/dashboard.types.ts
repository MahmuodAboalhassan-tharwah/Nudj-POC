export interface AssessmentSummary {
    id: string;
    organization_name: string;
    status: string;
    score: number | null;
    deadline: string | null;
    updated_at: string;
}

export interface RecentActivity {
    id: string;
    type: string;
    description: string;
    timestamp: string;
    user_name: string;
}

export interface PortfolioStats {
    total_organizations: number;
    total_users: number;
    total_assessments: number;
    average_maturity_score: number;
    active_assessments_count: number;
    completed_assessments_count: number;
}

export interface PortfolioDashboardResponse {
    stats: PortfolioStats;
    recent_assessments: AssessmentSummary[];
}

export interface OrganizationStats {
    total_assessments: number;
    active_assessments: number;
    completed_assessments: number;
    average_score: number;
    next_deadline: string | null;
}

export interface ClientDashboardResponse {
    stats: OrganizationStats;
    active_assessments: AssessmentSummary[];
    recent_activity: RecentActivity[];
}
