import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listUsers, listRoles, assignUserRoles } from "../api/admin";

export function useUsers(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: ["admin", "users", page, pageSize],
    queryFn: () => listUsers(page, pageSize),
  });
}

export function useRoles() {
  return useQuery({
    queryKey: ["admin", "roles"],
    queryFn: listRoles,
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useAssignRoles() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ userId, roleNames }: { userId: string; roleNames: string[] }) =>
      assignUserRoles(userId, roleNames),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["admin", "users"] });
      queryClient.invalidateQueries({ queryKey: ["admin", "me"] });
    },
  });
}
