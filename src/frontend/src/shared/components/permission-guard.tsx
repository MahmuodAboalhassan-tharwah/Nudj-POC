import { useAuth } from '@/shared/hooks/use-auth';

interface PermissionGuardProps {
  children: React.ReactNode;
  permission: string;
  fallback?: React.ReactNode;
}

export const PermissionGuard = ({ children, permission, fallback = null }: PermissionGuardProps) => {
  const { hasPermission } = useAuth();

  if (hasPermission(permission)) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
};
