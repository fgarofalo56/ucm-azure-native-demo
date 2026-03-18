import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import {
  Upload,
  CheckCircle2,
  AlertCircle,
  Loader2,
  File,
  X,
} from "lucide-react";
import { clsx } from "clsx";
import { uploadDocument } from "../../api/documents";

interface FileProgress {
  name: string;
  progress: number; // 0-100
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
}

interface DocumentUploadProps {
  investigationId: string;
  onUploadComplete: () => void;
}

const MAX_CONCURRENT = 3;

export function DocumentUpload({
  investigationId,
  onUploadComplete,
}: DocumentUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileProgress, setFileProgress] = useState<FileProgress[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      setUploading(true);
      setError(null);

      const progress: FileProgress[] = acceptedFiles.map((f) => ({
        name: f.name,
        progress: 0,
        status: "pending" as const,
      }));
      setFileProgress([...progress]);

      // Process files with concurrency limit
      let idx = 0;
      const results: boolean[] = [];

      async function processNext(): Promise<void> {
        while (idx < acceptedFiles.length) {
          const currentIdx = idx++;
          const file = acceptedFiles[currentIdx]!;

          setFileProgress((prev) =>
            prev.map((p, i) =>
              i === currentIdx ? { ...p, status: "uploading", progress: 30 } : p,
            ),
          );

          try {
            await uploadDocument(investigationId, file);
            setFileProgress((prev) =>
              prev.map((p, i) =>
                i === currentIdx
                  ? { ...p, status: "done", progress: 100 }
                  : p,
              ),
            );
            results[currentIdx] = true;
          } catch (err) {
            const errorMsg =
              err instanceof Error ? err.message : "Upload failed";
            setFileProgress((prev) =>
              prev.map((p, i) =>
                i === currentIdx
                  ? { ...p, status: "error", progress: 0, error: errorMsg }
                  : p,
              ),
            );
            results[currentIdx] = false;
          }
        }
      }

      try {
        // Launch up to MAX_CONCURRENT workers
        const workers = Array.from(
          { length: Math.min(MAX_CONCURRENT, acceptedFiles.length) },
          () => processNext(),
        );
        await Promise.all(workers);

        const anySuccess = results.some(Boolean);
        if (anySuccess) {
          onUploadComplete();
        }

        // Clear progress after delay
        setTimeout(() => {
          setFileProgress([]);
        }, 3000);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [investigationId, onUploadComplete],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    maxSize: 500 * 1024 * 1024, // 500MB
  });

  const doneCount = fileProgress.filter((f) => f.status === "done").length;
  const totalCount = fileProgress.length;
  const allDone =
    totalCount > 0 && fileProgress.every((f) => f.status !== "pending" && f.status !== "uploading");

  return (
    <div className="space-y-3">
      <div
        {...getRootProps()}
        className={clsx(
          "cursor-pointer rounded-xl border-2 border-dashed p-6 text-center transition-all duration-200",
          isDragActive
            ? clsx(
                "border-primary-400 bg-primary-50/50 scale-[1.01]",
                "dark:border-primary-500 dark:bg-primary-500/5",
              )
            : clsx(
                "border-secondary-300 hover:border-primary-400 hover:bg-primary-50/30",
                "dark:border-secondary-600 dark:hover:border-primary-500 dark:hover:bg-primary-500/5",
              ),
          uploading && "pointer-events-none opacity-75",
        )}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
            <p className="text-sm font-medium text-primary-600 dark:text-primary-400">
              Uploading {doneCount} of {totalCount} files...
            </p>
          </div>
        ) : !uploading && allDone && doneCount > 0 ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle2 className="h-8 w-8 text-success-500" />
            <p className="text-sm font-medium text-success-600 dark:text-success-400">
              {doneCount} file{doneCount !== 1 ? "s" : ""} uploaded
              successfully
            </p>
          </div>
        ) : isDragActive ? (
          <div className="flex flex-col items-center gap-2">
            <Upload className="h-8 w-8 text-primary-500 animate-bounce" />
            <p className="text-sm font-medium text-primary-600 dark:text-primary-400">
              Drop files here
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-3">
              <File className="h-6 w-6 text-secondary-400 dark:text-secondary-500" />
            </div>
            <div>
              <p className="text-sm text-secondary-600 dark:text-secondary-400">
                Drag & drop files here, or{" "}
                <span className="font-medium text-primary-600 dark:text-primary-400">
                  browse
                </span>
              </p>
              <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
                Max 500MB per file. Supports all common document formats.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Per-file progress */}
      {fileProgress.length > 0 && (
        <div className="space-y-1.5">
          {fileProgress.map((fp) => (
            <div
              key={fp.name}
              className={clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm",
                "bg-secondary-50 dark:bg-secondary-800/50",
              )}
            >
              {fp.status === "done" ? (
                <CheckCircle2 className="h-4 w-4 text-success-500 shrink-0" />
              ) : fp.status === "error" ? (
                <X className="h-4 w-4 text-danger-500 shrink-0" />
              ) : fp.status === "uploading" ? (
                <Loader2 className="h-4 w-4 text-primary-500 animate-spin shrink-0" />
              ) : (
                <File className="h-4 w-4 text-secondary-400 shrink-0" />
              )}
              <span className="flex-1 truncate text-secondary-700 dark:text-secondary-300">
                {fp.name}
              </span>
              {fp.status === "uploading" && (
                <div className="w-16 bg-secondary-200 dark:bg-secondary-700 rounded-full h-1.5">
                  <div
                    className="bg-primary-500 h-full rounded-full transition-all"
                    style={{ width: `${fp.progress}%` }}
                  />
                </div>
              )}
              {fp.error && (
                <span className="text-xs text-danger-500 truncate max-w-32">
                  {fp.error}
                </span>
              )}
            </div>
          ))}
        </div>
      )}

      {error && (
        <div
          className={clsx(
            "flex items-center gap-2 rounded-lg px-4 py-3 text-sm",
            "bg-danger-50 text-danger-700 border border-danger-200",
            "dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
          )}
        >
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </div>
      )}
    </div>
  );
}
