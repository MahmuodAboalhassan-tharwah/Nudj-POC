import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/shared/hooks/use-auth';
import { Role } from '@/features/auth/types/auth.types';

interface RoleGuardProps {
  children: React.ReactNode;
  roles?: Role[];
}

export const RoleGuard = ({ children, roles }: RoleGuardProps) => {
  const { isAuthenticated, isLoading, hasRole } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center">Loading...</div>; // TODO: Replace with Spinner component
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (roles && !hasRole(roles as any)) { // Cast to any because Role[] vs Role | Role[] mismatch potentially
      // Redirect to dashboard if unauthorized but logged in
      return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
