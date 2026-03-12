import { apiClient } from "./client";
import type { SearchResponse } from "./types";

export async function searchAll(
  query: string,
  type?: "investigation" | "document",
): Promise<SearchResponse> {
  const params: Record<string, string> = { q: query };
  if (type) params.type = type;
  const { data } = await apiClient.get<SearchResponse>("/search", { params });
  return data;
}
