import { useEffect, useState } from "react";
import { getDocumentVersions, downloadDocumentVersion } from "../../api/documents";
import type { DocumentVersion } from "../../api/types";
import { Download, X, History, Loader2, CheckCircle2 } from "lucide-react";
import { clsx } from "clsx";
import { format } from "date-fns";

interface VersionHistoryProps {
  documentId: string;
  onClose: () => void;
}

export function VersionHistory({ documentId, onClose }: VersionHistoryProps) {
  const [versions, setVersions] = useState<DocumentVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocumentVersions(documentId)
      .then(setVersions)
      .catch((err) => {
        // Non-admin users won't have access to version history
        const status = err?.response?.status;
        if (status === 403) {
          setError("Admin access required to view version history.");
        } else {
          setError("Failed to load version history.");
        }
      })
      .finally(() => setLoading(false));
  }, [documentId]);

  const handleDownloadVersion = async (versionId: string, filename: string) => {
    const blob = await downloadDocumentVersion(documentId, versionId);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="card">
      <div className="mb-5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary-50 dark:bg-primary-500/10">
            <History className="h-4 w-4 text-primary-600 dark:text-primary-400" />
          </div>
          <h3 className="font-semibold text-secondary-900 dark:text-secondary-50">
            Version History
          </h3>
        </div>
        <button
          onClick={onClose}
          className={clsx(
            "rounded-lg p-1.5 transition-colors",
            "text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100",
            "dark:text-secondary-500 dark:hover:text-secondary-300 dark:hover:bg-secondary-800",
          )}
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
        </div>
      ) : error ? (
        <p className="py-8 text-center text-sm text-secondary-500 dark:text-secondary-400">
          {error}
        </p>
      ) : versions.length === 0 ? (
        <p className="py-8 text-center text-sm text-secondary-500 dark:text-secondary-400">
          No version history available.
        </p>
      ) : (
        <div className="space-y-2">
          {versions.map((v) => (
            <div
              key={v.id}
              className={clsx(
                "flex items-center justify-between rounded-lg border p-3",
                "border-secondary-200 dark:border-secondary-700",
                v.is_latest && "bg-success-50/50 border-success-200 dark:bg-success-500/5 dark:border-success-500/20",
              )}
            >
              <div className="flex items-center gap-3">
                <div
                  className={clsx(
                    "flex h-8 w-8 items-center justify-center rounded-full text-xs font-semibold",
                    v.is_latest
                      ? "bg-success-100 text-success-700 dark:bg-success-500/20 dark:text-success-400"
                      : "bg-secondary-100 text-secondary-500 dark:bg-secondary-800 dark:text-secondary-400",
                  )}
                >
                  v{v.version_number}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-secondary-700 dark:text-secondary-300">
                      {v.original_filename}
                    </span>
                    {v.is_latest && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-success-100 px-2 py-0.5 text-xs font-medium text-success-700 dark:bg-success-500/20 dark:text-success-400">
                        <CheckCircle2 className="h-3 w-3" />
                        Latest
                      </span>
                    )}
                  </div>
                  <div className="flex gap-3 text-xs text-secondary-400 dark:text-secondary-500">
                    <span>{format(new Date(v.uploaded_at), "PPp")}</span>
                    <span>{formatSize(v.file_size_bytes)}</span>
                    {v.uploaded_by_name && <span>by {v.uploaded_by_name}</span>}
                  </div>
                </div>
              </div>
              <button
                onClick={() => handleDownloadVersion(v.id, v.original_filename)}
                className={clsx(
                  "flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
                  "text-primary-600 hover:bg-primary-50",
                  "dark:text-primary-400 dark:hover:bg-primary-500/10",
                )}
              >
                <Download className="h-4 w-4" />
                Download
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
