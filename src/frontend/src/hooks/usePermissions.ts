import { useQuery } from "@tanstack/react-query";
import { getCurrentUser } from "../api/admin";

export function usePermissions() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["admin", "me"],
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });

  const hasPermission = (permission: string): boolean => {
    return data?.permissions.includes(permission) ?? false;
  };

  const hasRole = (role: string): boolean => {
    return data?.roles.includes(role) ?? false;
  };

  return {
    user: data,
    isLoading,
    error,
    hasPermission,
    hasRole,
    permissions: data?.permissions ?? [],
    roles: data?.roles ?? [],
  };
}
