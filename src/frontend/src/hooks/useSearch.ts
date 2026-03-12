import { useQuery } from "@tanstack/react-query";
import { searchAll } from "../api/search";

export function useSearch(query: string, type?: "investigation" | "document") {
  return useQuery({
    queryKey: ["search", query, type],
    queryFn: () => searchAll(query, type),
    enabled: query.length >= 2,
    staleTime: 30 * 1000, // 30 seconds
  });
}
