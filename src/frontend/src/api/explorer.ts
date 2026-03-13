import { apiClient } from "./client";
import type { AddToInvestigationResponse, ExplorerResponse } from "./types";

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

export async function addFilesToInvestigation(
  investigationId: string,
  blobPaths: string[],
): Promise<AddToInvestigationResponse> {
  const { data } = await apiClient.post<AddToInvestigationResponse>(
    "/explorer/add-to-investigation",
    { investigation_id: investigationId, blob_paths: blobPaths },
  );
  return data;
}
