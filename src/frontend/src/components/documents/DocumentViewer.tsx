import type { Document } from "../../api/types";
import { ConversionStatus } from "./ConversionStatus";
import {
  FileText,
  User,
  Calendar,
  HardDrive,
  Hash,
  X,
  Shield,
} from "lucide-react";
import { clsx } from "clsx";
import { format } from "date-fns";

interface DocumentViewerProps {
  document: Document;
  onClose: () => void;
}

export function DocumentViewer({
  document: doc,
  onClose,
}: DocumentViewerProps) {
  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="card">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary-900 dark:text-secondary-50">
          Document Details
        </h3>
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

      <dl className="space-y-4">
        <DetailRow
          icon={<FileText className="h-4 w-4" />}
          label="Filename"
          value={doc.original_filename}
        />
        <DetailRow
          icon={<FileText className="h-4 w-4" />}
          label="Content Type"
          value={doc.content_type ?? "Unknown"}
        />
        <DetailRow
          icon={<HardDrive className="h-4 w-4" />}
          label="Size"
          value={formatSize(doc.file_size_bytes)}
        />
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800">
            <FileText className="h-4 w-4 text-secondary-500" />
          </div>
          <div>
            <dt className="text-xs font-medium text-secondary-500 dark:text-secondary-400">
              PDF Status
            </dt>
            <dd className="mt-1">
              <ConversionStatus status={doc.pdf_conversion_status} />
            </dd>
          </div>
        </div>
        <DetailRow
          icon={<Shield className="h-4 w-4" />}
          label="SHA-256"
          value={
            <span className="break-all font-mono text-xs">
              {doc.checksum_sha256}
            </span>
          }
        />
        <DetailRow
          icon={<User className="h-4 w-4" />}
          label="Uploaded By"
          value={doc.uploaded_by_name ?? doc.uploaded_by}
        />
        <DetailRow
          icon={<Calendar className="h-4 w-4" />}
          label="Uploaded At"
          value={format(new Date(doc.uploaded_at), "PPpp")}
        />
        {doc.pdf_converted_at && (
          <DetailRow
            icon={<Hash className="h-4 w-4" />}
            label="Converted At"
            value={format(new Date(doc.pdf_converted_at), "PPpp")}
          />
        )}
      </dl>
    </div>
  );
}

function DetailRow({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800">
        <span className="text-secondary-500">{icon}</span>
      </div>
      <div className="min-w-0">
        <dt className="text-xs font-medium text-secondary-500 dark:text-secondary-400">
          {label}
        </dt>
        <dd className="mt-0.5 text-sm text-secondary-900 dark:text-secondary-100">
          {value}
        </dd>
      </div>
    </div>
  );
}
