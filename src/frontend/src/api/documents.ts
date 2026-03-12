import { apiClient } from "./client";
import type {
  Document,
  DocumentUploadResponse,
  DocumentVersion,
  PaginatedResponse,
} from "./types";

export async function uploadDocument(
  investigationId: string,
  file: File,
): Promise<DocumentUploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await apiClient.post<DocumentUploadResponse>(
    `/documents/upload/${investigationId}`,
    formData,
    { headers: { "Content-Type": "multipart/form-data" } },
  );
  return data;
}

export async function getDocument(documentId: string): Promise<Document> {
  const { data } = await apiClient.get<Document>(`/documents/${documentId}`);
  return data;
}

export async function downloadDocument(
  documentId: string,
  version?: string,
): Promise<Blob> {
  const params = version ? { version } : {};
  const { data } = await apiClient.get(`/documents/${documentId}/download`, {
    responseType: "blob",
    params,
  });
  return data;
}

export async function downloadPdf(documentId: string): Promise<Blob> {
  const { data } = await apiClient.get(`/documents/${documentId}/pdf`, {
    responseType: "blob",
  });
  return data;
}

export async function getDocumentVersions(
  documentId: string,
): Promise<DocumentVersion[]> {
  const { data } = await apiClient.get<DocumentVersion[]>(
    `/documents/${documentId}/versions`,
  );
  return data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}

export async function mergePdfs(
  recordId: string,
  fileIds: string[],
): Promise<Blob> {
  const { data } = await apiClient.post(
    `/investigations/${recordId}/merge-pdf`,
    { file_ids: fileIds },
    { responseType: "blob" },
  );
  return data;
}

export async function listInvestigationDocuments(
  investigationId: string,
  page = 1,
  pageSize = 50,
): Promise<PaginatedResponse<Document>> {
  const { data } = await apiClient.get<PaginatedResponse<Document>>(
    `/investigations/${investigationId}/documents`,
    { params: { page, page_size: pageSize } },
  );
  return data;
}
