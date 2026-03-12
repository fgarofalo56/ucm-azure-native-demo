import { useQuery } from "@tanstack/react-query";
import { browseExplorer } from "../api/explorer";

export function useExplorer(prefix = "") {
  return useQuery({
    queryKey: ["explorer", prefix],
    queryFn: () => browseExplorer(prefix),
  });
}
