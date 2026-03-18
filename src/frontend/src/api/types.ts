/** TypeScript types for API responses — version-aware document model. */

export interface Investigation {
  id: string;
  record_id: string;
  title: string;
  description: string | null;
  status: "active" | "closed" | "archived";
  created_by: string;
  created_by_name: string | null;
  created_at: string;
  updated_at: string;
  document_count: number;
}

export type DocumentType =
  | "investigation_report"
  | "inspection_form"
  | "laboratory_result"
  | "correspondence"
  | "supporting_evidence"
  | "legal_document"
  | "other";

export type PdfConversionStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "not_required";

/** Logical document with latest version metadata inlined. */
export interface Document {
  id: string;
  investigation_id: string;
  document_type: DocumentType;
  title: string | null;
  created_by: string;
  created_by_name: string | null;
  created_at: string;
  updated_at: string;

  // Latest version fields (inlined)
  current_version_id: string | null;
  version_number: number | null;
  original_filename: string | null;
  mime_type: string | null;
  file_size_bytes: number | null;
  checksum: string | null;
  pdf_conversion_status: PdfConversionStatus | null;
  uploaded_by: string | null;
  uploaded_by_name: string | null;
  uploaded_at: string | null;
}

/** Physical document version — admin-visible only for non-latest. */
export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  original_filename: string;
  mime_type: string | null;
  file_size_bytes: number;
  checksum: string;
  is_latest: boolean;
  pdf_conversion_status: PdfConversionStatus;
  pdf_conversion_error: string | null;
  pdf_converted_at: string | null;
  scan_status: string;
  scanned_at: string | null;
  uploaded_by: string;
  uploaded_by_name: string | null;
  uploaded_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  version_id: string;
  version_number: number;
  original_filename: string;
  file_size_bytes: number;
  checksum: string;
  document_type: DocumentType;
  pdf_conversion_status: PdfConversionStatus;
  blob_path: string;
}

export interface AuditLogEntry {
  id: number;
  event_type: string;
  event_timestamp: string;
  user_id: string;
  user_principal_name: string | null;
  ip_address: string | null;
  resource_type: string | null;
  resource_id: string | null;
  action: string;
  result: string;
  details: string | null;
  correlation_id: string | null;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: {
    page: number;
    page_size: number;
    total: number;
    status_counts?: Record<string, number>;
  };
}

export interface HealthResponse {
  status: string;
  environment: string;
  version: string;
}

// RBAC types
export interface PermissionInfo {
  id: number;
  resource: string;
  action: string;
  description: string | null;
}

export interface RoleInfo {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  is_system: boolean;
  permissions: PermissionInfo[];
}

export interface AppUser {
  id: string;
  entra_oid: string;
  display_name: string;
  email: string | null;
  is_active: boolean;
  created_at: string;
  last_login_at: string | null;
  roles: RoleInfo[];
}

export interface CurrentUser {
  id: string;
  entra_oid: string;
  display_name: string;
  email: string | null;
  roles: string[];
  permissions: string[];
}

// Search types
export interface SearchResultItem {
  type: "investigation" | "document";
  id: string;
  title: string;
  subtitle: string | null;
  url: string;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
  total: number;
}

// Explorer types
export interface ExplorerItem {
  name: string;
  type: "folder" | "file";
  path: string;
  size: number | null;
  last_modified: string | null;
  content_type: string | null;
}

export interface ExplorerResponse {
  prefix: string;
  items: ExplorerItem[];
}

// Add to Investigation types
export interface AddToInvestigationResult {
  blob_path: string;
  success: boolean;
  document_id: string | null;
  error: string | null;
}

export interface AddToInvestigationResponse {
  investigation_id: string;
  results: AddToInvestigationResult[];
  total: number;
  succeeded: number;
  failed: number;
}

// Copy documents types
export interface CopyDocumentsResponse {
  investigation_id: string;
  results: { document_id: string; success: boolean; new_document_id: string | null; error: string | null }[];
  total: number;
  succeeded: number;
  failed: number;
}

// Batch upload types
export interface BatchUploadResult {
  filename: string;
  success: boolean;
  document_id: string | null;
  version_id: string | null;
  error: string | null;
}

// Admin types
export interface RollbackResponse {
  document_id: string;
  rolled_back_version: number;
  promoted_version: number;
  new_current_version_id: string;
}
