import { useState } from "react";
import { Combine, X, Loader2, AlertCircle } from "lucide-react";
import { clsx } from "clsx";
import { mergePdfs } from "../../api/documents";

interface PdfMergeProps {
  recordId: string;
  selectedDocumentIds: string[];
  onClear: () => void;
}

export function PdfMerge({
  recordId,
  selectedDocumentIds,
  onClear,
}: PdfMergeProps) {
  const [merging, setMerging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMerge = async () => {
    if (selectedDocumentIds.length < 2) return;
    setMerging(true);
    setError(null);

    try {
      const blob = await mergePdfs(recordId, selectedDocumentIds);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${recordId}-merged.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      onClear();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Merge failed");
    } finally {
      setMerging(false);
    }
  };

  if (selectedDocumentIds.length === 0) return null;

  return (
    <div
      className={clsx(
        "sticky bottom-4 z-10",
        "flex items-center gap-3 rounded-xl p-4 shadow-lg",
        "bg-primary-600 text-white",
        "dark:bg-primary-700",
        "border border-primary-500 dark:border-primary-600",
      )}
    >
      <Combine className="h-5 w-5 shrink-0" />
      <span className="text-sm font-medium">
        {selectedDocumentIds.length} document{selectedDocumentIds.length !== 1 ? "s" : ""}{" "}
        selected
      </span>

      <div className="flex-1" />

      {error && (
        <span className="flex items-center gap-1.5 text-sm text-white/80">
          <AlertCircle className="h-4 w-4" />
          {error}
        </span>
      )}

      <button
        onClick={handleMerge}
        disabled={merging || selectedDocumentIds.length < 2}
        className={clsx(
          "inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium",
          "bg-white text-primary-700 shadow-sm",
          "hover:bg-primary-50",
          "disabled:opacity-50",
          "transition-colors",
        )}
      >
        {merging ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Merging...
          </>
        ) : (
          <>Merge PDFs</>
        )}
      </button>

      <button
        onClick={onClear}
        className="rounded-lg p-1.5 hover:bg-primary-500 transition-colors"
        aria-label="Clear selection"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}
