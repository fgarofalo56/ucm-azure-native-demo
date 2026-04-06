import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listInvestigations,
  getInvestigation,
  createInvestigation,
  updateInvestigation,
} from "../api/investigations";

export function useInvestigations(status?: string, page = 1, search?: string) {
  return useQuery({
    queryKey: ["investigations", status, page, search],
    queryFn: () => listInvestigations(status, page, 20, search),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
}

export function useInvestigation(id: string) {
  return useQuery({
    queryKey: ["investigation", id],
    queryFn: () => getInvestigation(id),
    enabled: !!id,
  });
}

export function useCreateInvestigation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createInvestigation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });
}

export function useUpdateInvestigation(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (params: {
      title?: string;
      description?: string;
      status?: string;
    }) => updateInvestigation(id, params),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["investigation", id] });
      queryClient.invalidateQueries({ queryKey: ["investigations"] });
    },
  });
}
