import { apiClient } from "./client";
import type { Investigation, PaginatedResponse } from "./types";

export async function createInvestigation(params: {
  record_id: string;
  title: string;
  description?: string;
}): Promise<Investigation> {
  const { data } = await apiClient.post<Investigation>(
    "/investigations/",
    params,
  );
  return data;
}

export async function getInvestigation(id: string): Promise<Investigation> {
  const { data } = await apiClient.get<Investigation>(
    `/investigations/${id}`,
  );
  return data;
}

export async function listInvestigations(
  status?: string,
  page = 1,
  pageSize = 20,
): Promise<PaginatedResponse<Investigation>> {
  const { data } = await apiClient.get<PaginatedResponse<Investigation>>(
    "/investigations/",
    { params: { status, page, page_size: pageSize } },
  );
  return data;
}

export async function updateInvestigation(
  id: string,
  params: {
    title?: string;
    description?: string;
    status?: string;
  },
): Promise<Investigation> {
  const { data } = await apiClient.patch<Investigation>(
    `/investigations/${id}`,
    params,
  );
  return data;
}
