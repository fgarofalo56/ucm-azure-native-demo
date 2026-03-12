import { useCallback } from "react";
import { useDropzone, type Accept } from "react-dropzone";
import { Upload, FileWarning } from "lucide-react";
import { clsx } from "clsx";

interface FileDropzoneProps {
  onFilesSelected: (files: File[]) => void;
  accept?: Accept;
  maxSize?: number;
  multiple?: boolean;
  disabled?: boolean;
  compact?: boolean;
}

export default function FileDropzone({
  onFilesSelected,
  accept,
  maxSize = 500 * 1024 * 1024,
  multiple = true,
  disabled = false,
  compact = false,
}: FileDropzoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFilesSelected(acceptedFiles);
      }
    },
    [onFilesSelected],
  );

  const { getRootProps, getInputProps, isDragActive, isDragReject } =
    useDropzone({
      onDrop,
      accept,
      maxSize,
      multiple,
      disabled,
    });

  return (
    <div
      {...getRootProps()}
      className={clsx(
        "border-2 border-dashed rounded-xl text-center transition-all duration-200 cursor-pointer",
        compact ? "p-4" : "p-8",
        disabled && "opacity-50 cursor-not-allowed bg-secondary-50 dark:bg-secondary-800/50",
        isDragActive && !isDragReject && clsx(
          "border-primary-400 bg-primary-50/50 scale-[1.01]",
          "dark:border-primary-500 dark:bg-primary-500/5",
        ),
        isDragReject && clsx(
          "border-danger-400 bg-danger-50/50",
          "dark:border-danger-500 dark:bg-danger-500/5",
        ),
        !isDragActive && !disabled && clsx(
          "border-secondary-300 hover:border-primary-400 hover:bg-primary-50/30",
          "dark:border-secondary-600 dark:hover:border-primary-500 dark:hover:bg-primary-500/5",
        ),
      )}
    >
      <input {...getInputProps()} />
      {isDragReject ? (
        <div className="flex flex-col items-center">
          <div className={clsx(
            "rounded-xl p-3",
            "bg-danger-100 dark:bg-danger-500/10",
          )}>
            <FileWarning className="h-8 w-8 text-danger-500" />
          </div>
          <p className="mt-3 text-sm font-medium text-danger-600 dark:text-danger-400">
            File type not accepted
          </p>
        </div>
      ) : isDragActive ? (
        <div className="flex flex-col items-center">
          <div className={clsx(
            "rounded-xl p-3",
            "bg-primary-100 dark:bg-primary-500/10",
          )}>
            <Upload className="h-8 w-8 text-primary-500 animate-bounce" />
          </div>
          <p className="mt-3 text-sm font-medium text-primary-600 dark:text-primary-400">
            Drop files here...
          </p>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <div className={clsx(
            "rounded-xl p-3",
            "bg-secondary-100 dark:bg-secondary-800",
          )}>
            <Upload className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
          </div>
          <p className="mt-3 text-sm text-secondary-600 dark:text-secondary-400">
            Drag and drop files here, or{" "}
            <span className="font-medium text-primary-600 dark:text-primary-400">
              browse
            </span>
          </p>
          <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
            Max file size: {Math.round(maxSize / (1024 * 1024))}MB
          </p>
        </div>
      )}
    </div>
  );
}
