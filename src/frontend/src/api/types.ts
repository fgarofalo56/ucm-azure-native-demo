/** TypeScript types for API responses. */

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

export interface Document {
  id: string;
  investigation_id: string;
  file_id: string;
  original_filename: string;
  content_type: string | null;
  file_size_bytes: number;
  pdf_conversion_status:
    | "pending"
    | "processing"
    | "completed"
    | "failed"
    | "not_required";
  pdf_conversion_error: string | null;
  pdf_converted_at: string | null;
  checksum_sha256: string;
  uploaded_by: string;
  uploaded_by_name: string | null;
  uploaded_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  version_id: string;
  last_modified: string;
  content_length: number;
  is_current: boolean;
}

export interface DocumentUploadResponse {
  id: string;
  file_id: string;
  original_filename: string;
  file_size_bytes: number;
  checksum_sha256: string;
  pdf_conversion_status: string;
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
  file_id: string | null;
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
  results: { document_id: string; success: boolean; new_file_id: string | null; error: string | null }[];
  total: number;
  succeeded: number;
  failed: number;
}

// Batch upload types
export interface BatchUploadResult {
  filename: string;
  success: boolean;
  file_id: string | null;
  error: string | null;
}
