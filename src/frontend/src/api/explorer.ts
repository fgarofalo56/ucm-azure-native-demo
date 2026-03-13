import { apiClient } from "./client";
import type { ExplorerResponse } from "./types";

export async function browseExplorer(
  prefix = "",
): Promise<ExplorerResponse> {
  const { data } = await apiClient.get<ExplorerResponse>("/explorer/browse", {
    params: { prefix },
  });
  return data;
}

export async function downloadExplorerFile(path: string): Promise<Blob> {
  const { data } = await apiClient.get("/explorer/download", {
    params: { path },
    responseType: "blob",
  });
  return data;
}

export async function deleteExplorerFiles(
  paths: string[],
): Promise<{ deleted: number; errors: string[] }> {
  const { data } = await apiClient.delete("/explorer/files", {
    data: paths,
  });
  return data;
}
