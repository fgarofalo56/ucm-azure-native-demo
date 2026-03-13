import { useState, useRef, useEffect } from "react";
import {
  Folder,
  FileText,
  ChevronRight,
  Home,
  Loader2,
  Download,
  Trash2,
  FolderPlus,
} from "lucide-react";
import { clsx } from "clsx";
import { useExplorer } from "../hooks/useExplorer";
import { downloadExplorerFile, addFilesToInvestigation } from "../api/explorer";
import { formatDistanceToNow } from "date-fns";
import Button from "../components/ui/Button";
import InvestigationPicker from "../components/ui/InvestigationPicker";

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
}

export function FileExplorerPage() {
  const [prefix, setPrefix] = useState("");
  const { data, isLoading } = useExplorer(prefix);

  const [downloading, setDownloading] = useState<string | null>(null);
  const [selectedPaths, setSelectedPaths] = useState<Set<string>>(new Set());
  const [showPicker, setShowPicker] = useState(false);
  const [addingToInvestigation, setAddingToInvestigation] = useState(false);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  const items = data?.items ?? [];
  const fileItems = items.filter((i) => i.type === "file");

  const handleDownload = async (path: string, name: string) => {
    setDownloading(path);
    try {
      const blob = await downloadExplorerFile(path);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = name;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      // silently fail
    } finally {
      setDownloading(null);
    }
  };

  const toggleSelect = (path: string) => {
    setSelectedPaths((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedPaths.size === fileItems.length) {
      setSelectedPaths(new Set());
    } else {
      setSelectedPaths(new Set(fileItems.map((f) => f.path)));
    }
  };

  const handleAddToInvestigation = async (investigationId: string) => {
    setAddingToInvestigation(true);
    try {
      const result = await addFilesToInvestigation(
        investigationId,
        Array.from(selectedPaths),
      );
      setShowPicker(false);
      setSelectedPaths(new Set());
      if (result.failed > 0) {
        setToast({
          type: "error",
          message: `Added ${result.succeeded} file(s), ${result.failed} failed`,
        });
      } else {
        setToast({
          type: "success",
          message: `Added ${result.succeeded} file(s) to investigation`,
        });
      }
      toastTimerRef.current = setTimeout(() => setToast(null), 4000);
    } catch {
      setToast({ type: "error", message: "Failed to add files to investigation" });
      toastTimerRef.current = setTimeout(() => setToast(null), 4000);
    } finally {
      setAddingToInvestigation(false);
    }
  };

  // Reset selection when navigating
  const navigateTo = (path: string) => {
    setPrefix(path);
    setSelectedPaths(new Set());
  };

  // Build breadcrumb from prefix
  const parts = prefix.split("/").filter(Boolean);
  const breadcrumbs = [
    { label: "Root", path: "" },
    ...parts.map((part, idx) => ({
      label: part,
      path: parts.slice(0, idx + 1).join("/") + "/",
    })),
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="page-header mb-1">File Explorer</h2>
          <p className="page-subtitle">
            Browse investigation folders and document files
          </p>
        </div>
        {selectedPaths.size > 0 && (
          <Button
            icon={<FolderPlus className="h-4 w-4" />}
            onClick={() => setShowPicker(true)}
          >
            Add {selectedPaths.size} file{selectedPaths.size > 1 ? "s" : ""} to
            Investigation
          </Button>
        )}
      </div>

      {/* Toast notification */}
      {toast && (
        <div
          className={clsx(
            "flex items-center gap-2 rounded-lg px-4 py-3 text-sm",
            toast.type === "success"
              ? "bg-success-50 text-success-700 border border-success-200 dark:bg-success-500/10 dark:text-success-400 dark:border-success-500/20"
              : "bg-danger-50 text-danger-700 border border-danger-200 dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
          )}
        >
          {toast.message}
        </div>
      )}

      {/* Breadcrumb */}
      <nav className="flex items-center gap-1 text-sm">
        {breadcrumbs.map((crumb, idx) => (
          <span key={crumb.path} className="flex items-center gap-1">
            {idx > 0 && (
              <ChevronRight className="h-3.5 w-3.5 text-secondary-400" />
            )}
            <button
              onClick={() => navigateTo(crumb.path)}
              className={clsx(
                "flex items-center gap-1.5 rounded-md px-2 py-1 transition-colors",
                idx === breadcrumbs.length - 1
                  ? "font-medium text-secondary-900 dark:text-secondary-100"
                  : "text-secondary-500 hover:text-secondary-700 hover:bg-secondary-100 dark:text-secondary-400 dark:hover:text-secondary-200 dark:hover:bg-secondary-800",
              )}
            >
              {idx === 0 && <Home className="h-3.5 w-3.5" />}
              {crumb.label}
            </button>
          </span>
        ))}
      </nav>

      {/* File list */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Folder className="h-12 w-12 text-secondary-300 dark:text-secondary-600" />
          <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
            This folder is empty
          </p>
        </div>
      ) : (
        <div className="card overflow-hidden p-0">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-secondary-200 dark:border-secondary-700">
                <th className="px-4 py-3 text-left w-10">
                  {fileItems.length > 0 && (
                    <input
                      type="checkbox"
                      checked={
                        selectedPaths.size === fileItems.length &&
                        fileItems.length > 0
                      }
                      onChange={toggleSelectAll}
                      className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500 dark:border-secondary-600 dark:bg-secondary-800"
                    />
                  )}
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Name
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Size
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Modified
                </th>
                <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr
                  key={item.path}
                  className={clsx(
                    "border-b border-secondary-100 dark:border-secondary-800 last:border-0",
                    item.type === "folder" && "cursor-pointer",
                    "hover:bg-secondary-50 dark:hover:bg-secondary-800/50 transition-colors",
                    selectedPaths.has(item.path) &&
                      "bg-primary-50/50 dark:bg-primary-500/5",
                  )}
                  onClick={
                    item.type === "folder"
                      ? () => navigateTo(item.path)
                      : undefined
                  }
                >
                  <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                    {item.type === "file" && (
                      <input
                        type="checkbox"
                        checked={selectedPaths.has(item.path)}
                        onChange={() => toggleSelect(item.path)}
                        className="rounded border-secondary-300 text-primary-600 focus:ring-primary-500 dark:border-secondary-600 dark:bg-secondary-800"
                      />
                    )}
                  </td>
                  <td className="px-6 py-3">
                    <div className="flex items-center gap-3">
                      {item.type === "folder" ? (
                        <Folder className="h-5 w-5 text-warning-500 shrink-0" />
                      ) : (
                        <FileText className="h-5 w-5 text-primary-500 shrink-0" />
                      )}
                      <span className="text-sm font-medium text-secondary-900 dark:text-secondary-100 truncate max-w-md">
                        {item.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <span className="text-sm text-secondary-500 dark:text-secondary-400">
                      {item.size != null ? formatBytes(item.size) : "--"}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    <span className="text-xs text-secondary-400 dark:text-secondary-500">
                      {item.last_modified
                        ? formatDistanceToNow(new Date(item.last_modified), {
                            addSuffix: true,
                          })
                        : "--"}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-right">
                    {item.type === "file" && (
                      <div
                        className="flex items-center justify-end gap-1"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <button
                          onClick={() => handleDownload(item.path, item.name)}
                          disabled={downloading === item.path}
                          className={clsx(
                            "rounded-lg p-1.5",
                            "text-secondary-400 hover:text-primary-600 hover:bg-primary-50",
                            "dark:hover:text-primary-400 dark:hover:bg-primary-500/10",
                            "disabled:opacity-50",
                          )}
                          title="Download"
                        >
                          {downloading === item.path ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            <Download className="h-4 w-4" />
                          )}
                        </button>
                        <button
                          className={clsx(
                            "rounded-lg p-1.5",
                            "text-secondary-400 hover:text-danger-600 hover:bg-danger-50",
                            "dark:hover:text-danger-400 dark:hover:bg-danger-500/10",
                          )}
                          title="Delete"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Investigation Picker Modal */}
      <InvestigationPicker
        isOpen={showPicker}
        onClose={() => setShowPicker(false)}
        onSelect={handleAddToInvestigation}
        loading={addingToInvestigation}
      />
    </div>
  );
}
