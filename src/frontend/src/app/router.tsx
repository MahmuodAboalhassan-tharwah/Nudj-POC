import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { LoginPage, RegisterPage, InvitationExpiredPage, SSOCallbackPage } from '@/features/auth/pages';
import { UsersListPage, AuditLogsPage, FrameworkConfigPage } from '@/features/admin/pages';
import { AssessmentsPage } from '@/features/assessments/pages/assessments-page';
import { AssessmentDetailPage } from '@/features/assessments/pages/assessment-detail-page';
import { OrganizationsPage } from '@/features/organizations/pages/organizations-page';
import { OrganizationDetailPage } from '@/features/organizations/pages/organization-detail-page';
import { SuperAdminDashboard } from '@/features/dashboards/pages/super-admin-dashboard';
import { ClientDashboard } from '@/features/dashboards/pages/client-dashboard';
import { RoleGuard } from '@/shared/components/role-guard';
import { MainLayout } from '@/shared/layouts/main-layout'; // Assuming this exists or I'll generic it
import { AuthLayout } from '@/features/auth/layouts/auth-layout'; // Create this simple wrapper
import { useAuth } from '@/features/auth/hooks/use-auth';

// Component to route to correct dashboard based on role
const DashboardRouter = () => {
    const { user } = useAuth();
    if (user?.role === 'super_admin') {
        return <SuperAdminDashboard />;
    }
    return <ClientDashboard />;
};

export const AppRouter = () => {
    return (
        <Routes>
            {/* Public Auth Routes */}
            <Route element={<AuthLayout />}>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/invitation-expired" element={<InvitationExpiredPage />} />
                <Route path="/sso/callback" element={<SSOCallbackPage />} />
            </Route>

            {/* Protected Routes */}
            <Route path="/" element={<RoleGuard><MainLayout /></RoleGuard>}>
                <Route index element={<DashboardRouter />} />
                <Route path="dashboard" element={<DashboardRouter />} />

                {/* Assessment Routes */}
                <Route path="assessments">
                    <Route index element={<AssessmentsPage />} />
                    <Route path=":id" element={<AssessmentDetailPage />} />
                </Route>

                {/* Admin Routes */}
                <Route path="admin">
                    <Route path="organizations">
                        <Route index element={<OrganizationsPage />} />
                        <Route path="new" element={<OrganizationDetailPage />} />
                        <Route path=":id" element={<OrganizationDetailPage />} />
                    </Route>
                    <Route 
                        path="users" 
                        element={
                            <RoleGuard roles={['super_admin', 'client_admin']}>
                                <UsersListPage />
                            </RoleGuard>
                        } 
                    />
                    <Route 
                        path="audit-logs" 
                        element={
                            <RoleGuard roles={['super_admin']}>
                                <AuditLogsPage />
                            </RoleGuard>
                        } 
                    />
                    <Route 
                        path="framework" 
                        element={
                            <RoleGuard roles={['super_admin']}>
                                <FrameworkConfigPage />
                            </RoleGuard>
                        } 
                    />
                </Route>
            </Route>

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
};
