import { useState, useRef, useEffect } from "react";
import type { Document } from "../../api/types";
import {
  downloadDocument,
  downloadPdf,
  deleteDocument,
} from "../../api/documents";
import { ConversionStatus } from "./ConversionStatus";
import {
  FileText,
  Image,
  FileSpreadsheet,
  File,
  Download,
  FileDown,
  Trash2,
  History,
  MoreHorizontal,
  Inbox,
  Eye,
} from "lucide-react";
import { clsx } from "clsx";
import { formatDistanceToNow } from "date-fns";

interface DocumentListProps {
  documents: Document[];
  onRefresh: () => void;
  onSelectForMerge?: (fileId: string, selected: boolean) => void;
  selectedForMerge?: Set<string>;
  onViewDetails?: (doc: Document) => void;
  onViewVersions?: (doc: Document) => void;
}

function getFileIcon(contentType: string | null) {
  if (!contentType) return File;
  if (contentType.startsWith("image/")) return Image;
  if (
    contentType.includes("spreadsheet") ||
    contentType.includes("excel") ||
    contentType.includes("csv")
  )
    return FileSpreadsheet;
  if (
    contentType.includes("pdf") ||
    contentType.includes("word") ||
    contentType.includes("document") ||
    contentType.includes("text")
  )
    return FileText;
  return File;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ActionsDropdown({
  doc,
  onDownload,
  onDownloadPdf,
  onDelete,
  onViewDetails,
  onViewVersions,
  loading,
}: {
  doc: Document;
  onDownload: () => void;
  onDownloadPdf: () => void;
  onDelete: () => void;
  onViewDetails?: () => void;
  onViewVersions?: () => void;
  loading: boolean;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const pdfReady =
    doc.pdf_conversion_status === "completed" ||
    doc.pdf_conversion_status === "not_required";

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        disabled={loading}
        className={clsx(
          "rounded-lg p-1.5 transition-colors",
          "text-secondary-400 hover:bg-secondary-100 hover:text-secondary-600",
          "dark:text-secondary-500 dark:hover:bg-secondary-800 dark:hover:text-secondary-300",
          loading && "opacity-50",
        )}
      >
        <MoreHorizontal className="h-4 w-4" />
      </button>

      {open && (
        <div
          className={clsx(
            "absolute right-0 top-full mt-1 w-48 z-20",
            "rounded-lg border bg-white shadow-lg py-1",
            "dark:bg-secondary-900 dark:border-secondary-700",
            "border-secondary-200",
          )}
        >
          <button
            onClick={() => {
              onDownload();
              setOpen(false);
            }}
            className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50 dark:text-secondary-300 dark:hover:bg-secondary-800"
          >
            <Download className="h-4 w-4 text-secondary-400" />
            Download Original
          </button>
          {pdfReady && (
            <button
              onClick={() => {
                onDownloadPdf();
                setOpen(false);
              }}
              className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50 dark:text-secondary-300 dark:hover:bg-secondary-800"
            >
              <FileDown className="h-4 w-4 text-secondary-400" />
              Download PDF
            </button>
          )}
          {onViewDetails && (
            <button
              onClick={() => {
                onViewDetails();
                setOpen(false);
              }}
              className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50 dark:text-secondary-300 dark:hover:bg-secondary-800"
            >
              <Eye className="h-4 w-4 text-secondary-400" />
              View Details
            </button>
          )}
          {onViewVersions && (
            <button
              onClick={() => {
                onViewVersions();
                setOpen(false);
              }}
              className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-secondary-700 hover:bg-secondary-50 dark:text-secondary-300 dark:hover:bg-secondary-800"
            >
              <History className="h-4 w-4 text-secondary-400" />
              Version History
            </button>
          )}
          <div className="my-1 border-t border-secondary-100 dark:border-secondary-800" />
          <button
            onClick={() => {
              onDelete();
              setOpen(false);
            }}
            className="flex w-full items-center gap-2.5 px-3 py-2 text-sm text-danger-600 hover:bg-danger-50 dark:text-danger-400 dark:hover:bg-danger-500/10"
          >
            <Trash2 className="h-4 w-4" />
            Delete
          </button>
        </div>
      )}
    </div>
  );
}

export function DocumentList({
  documents,
  onRefresh,
  onSelectForMerge,
  selectedForMerge,
  onViewDetails,
  onViewVersions,
}: DocumentListProps) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDownload = async (doc: Document) => {
    setLoading(doc.id);
    try {
      const blob = await downloadDocument(doc.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = doc.original_filename;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(null);
    }
  };

  const handleDownloadPdf = async (doc: Document) => {
    setLoading(doc.id);
    try {
      const blob = await downloadPdf(doc.id);
      const baseName = doc.original_filename.replace(/\.[^.]+$/, "");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${baseName}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setLoading(null);
    }
  };

  const handleDelete = async (doc: Document) => {
    if (!confirm(`Delete "${doc.original_filename}"?`)) return;
    setError(null);
    try {
      await deleteDocument(doc.id);
      onRefresh();
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : `Failed to delete "${doc.original_filename}"`,
      );
    }
  };

  if (documents.length === 0) {
    return (
      <div className="card">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
            <Inbox className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
          </div>
          <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
            No documents yet
          </p>
          <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
            Upload files to get started
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {error && (
        <div
          className={clsx(
            "flex items-center gap-2 rounded-lg px-4 py-3 text-sm",
            "bg-danger-50 text-danger-700 border border-danger-200",
            "dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
          )}
        >
          {error}
        </div>
      )}
      <div className="table-wrapper">
        <table className="min-w-full divide-y divide-secondary-200 dark:divide-secondary-700">
          <thead className="table-header">
            <tr>
              {onSelectForMerge && (
                <th className="w-10 px-4 py-3.5" />
              )}
              <th className="table-header-cell">File</th>
              <th className="table-header-cell">Size</th>
              <th className="table-header-cell">PDF Status</th>
              <th className="table-header-cell">Uploaded</th>
              <th className="table-header-cell w-12">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="table-body">
            {documents.map((doc) => {
              const FileIcon = getFileIcon(doc.content_type);
              return (
                <tr key={doc.id} className="table-row">
                  {onSelectForMerge && (
                    <td className="px-4 py-3.5">
                      <input
                        type="checkbox"
                        checked={selectedForMerge?.has(doc.file_id) ?? false}
                        onChange={(e) =>
                          onSelectForMerge(doc.file_id, e.target.checked)
                        }
                        disabled={
                          doc.pdf_conversion_status !== "completed" &&
                          doc.pdf_conversion_status !== "not_required"
                        }
                        className={clsx(
                          "h-4 w-4 rounded border-secondary-300 text-primary-600 focus:ring-primary-500",
                          "dark:border-secondary-600 dark:bg-secondary-800",
                          "disabled:opacity-40",
                        )}
                      />
                    </td>
                  )}
                  <td className="table-cell">
                    <div className="flex items-center gap-3">
                      <div
                        className={clsx(
                          "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg",
                          "bg-primary-50 dark:bg-primary-500/10",
                        )}
                      >
                        <FileIcon className="h-4.5 w-4.5 text-primary-500 dark:text-primary-400" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100 truncate">
                          {doc.original_filename}
                        </p>
                        <p className="text-xs text-secondary-400 dark:text-secondary-500 truncate">
                          {doc.content_type ?? "Unknown type"}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="table-cell whitespace-nowrap">
                    <span className="text-sm text-secondary-500 dark:text-secondary-400">
                      {formatSize(doc.file_size_bytes)}
                    </span>
                  </td>
                  <td className="table-cell">
                    <ConversionStatus status={doc.pdf_conversion_status} />
                  </td>
                  <td className="table-cell whitespace-nowrap">
                    <div>
                      <p className="text-sm text-secondary-500 dark:text-secondary-400">
                        {formatDistanceToNow(new Date(doc.uploaded_at), {
                          addSuffix: true,
                        })}
                      </p>
                      {doc.uploaded_by_name && (
                        <p className="text-xs text-secondary-400 dark:text-secondary-500">
                          by {doc.uploaded_by_name}
                        </p>
                      )}
                    </div>
                  </td>
                  <td className="table-cell">
                    <ActionsDropdown
                      doc={doc}
                      onDownload={() => handleDownload(doc)}
                      onDownloadPdf={() => handleDownloadPdf(doc)}
                      onDelete={() => handleDelete(doc)}
                      onViewDetails={
                        onViewDetails ? () => onViewDetails(doc) : undefined
                      }
                      onViewVersions={
                        onViewVersions ? () => onViewVersions(doc) : undefined
                      }
                      loading={loading === doc.id}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
