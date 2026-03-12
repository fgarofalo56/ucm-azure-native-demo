import type { ReactNode } from "react";
import { usePermissions } from "../../hooks/usePermissions";

interface PermissionGateProps {
  permission?: string;
  role?: string;
  children: ReactNode;
  fallback?: ReactNode;
}

export function PermissionGate({
  permission,
  role,
  children,
  fallback = null,
}: PermissionGateProps) {
  const { hasPermission, hasRole, isLoading } = usePermissions();

  if (isLoading) return null;

  if (permission && !hasPermission(permission)) return <>{fallback}</>;
  if (role && !hasRole(role)) return <>{fallback}</>;

  return <>{children}</>;
}
