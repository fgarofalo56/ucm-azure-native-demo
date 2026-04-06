import { apiClient } from "./client";
import type {
  CopyDocumentsResponse,
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

export async function downloadDocument(documentId: string): Promise<Blob> {
  const { data } = await apiClient.get(`/documents/${documentId}/download`, {
    responseType: "blob",
  });
  return data;
}

export async function downloadPdf(documentId: string): Promise<Blob> {
  const { data } = await apiClient.get(`/documents/${documentId}/pdf`, {
    responseType: "blob",
  });
  return data;
}

/** Admin-only: list all versions of a document. */
export async function getDocumentVersions(
  documentId: string,
): Promise<DocumentVersion[]> {
  const { data } = await apiClient.get<DocumentVersion[]>(
    `/admin/documents/${documentId}/versions`,
  );
  return data;
}

/** Admin-only: download a specific version. */
export async function downloadDocumentVersion(
  documentId: string,
  versionId: string,
): Promise<Blob> {
  const { data } = await apiClient.get(
    `/admin/documents/${documentId}/versions/${versionId}/download`,
    { responseType: "blob" },
  );
  return data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}

/** Merge documents into a single PDF. Uses document IDs (not file IDs).
 *  Backend sorts by document_type (rule-based order), not user order. */
export async function mergePdfs(
  recordId: string,
  documentIds: string[],
): Promise<Blob> {
  const { data } = await apiClient.post(
    `/investigations/${recordId}/merge-pdf`,
    { document_ids: documentIds },
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

export async function copyDocumentsToInvestigation(
  investigationId: string,
  documentIds: string[],
): Promise<CopyDocumentsResponse> {
  const { data } = await apiClient.post<CopyDocumentsResponse>(
    "/documents/copy-to-investigation",
    { investigation_id: investigationId, document_ids: documentIds },
  );
  return data;
}
