import { useState, useRef, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  Search,
  FolderSearch,
  FileText,
  Loader2,
  FolderPlus,
} from "lucide-react";
import { clsx } from "clsx";
import { useSearch } from "../hooks/useSearch";
import { copyDocumentsToInvestigation } from "../api/documents";
import InvestigationPicker from "../components/ui/InvestigationPicker";

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(initialQuery);
  const [typeFilter, setTypeFilter] = useState<
    "investigation" | "document" | undefined
  >(undefined);

  const { data, isLoading } = useSearch(query, typeFilter);
  const results = data?.results ?? [];

  // Add-to-investigation state
  const [selectedDocIds, setSelectedDocIds] = useState<Set<string>>(new Set());
  const [showPicker, setShowPicker] = useState(false);
  const [addingToInvestigation, setAddingToInvestigation] = useState(false);
  const [toast, setToast] = useState<{
    type: "success" | "error";
    message: string;
  } | null>(null);
  const toastTimerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) clearTimeout(toastTimerRef.current);
    };
  }, []);

  const handleSearch = (value: string) => {
    setQuery(value);
    if (value.length >= 2) {
      setSearchParams({ q: value });
    }
  };

  const investigationResults = results.filter(
    (r) => r.type === "investigation",
  );
  const documentResults = results.filter((r) => r.type === "document");

  const toggleDocSelect = (id: string) => {
    setSelectedDocIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleAddToInvestigation = async (investigationId: string) => {
    setAddingToInvestigation(true);
    try {
      const result = await copyDocumentsToInvestigation(
        investigationId,
        Array.from(selectedDocIds),
      );
      setShowPicker(false);
      setSelectedDocIds(new Set());
      if (result.failed > 0) {
        setToast({
          type: "error",
          message: `Copied ${result.succeeded} document(s), ${result.failed} failed`,
        });
      } else {
        setToast({
          type: "success",
          message: `Copied ${result.succeeded} document(s) to investigation`,
        });
      }
      toastTimerRef.current = setTimeout(() => setToast(null), 4000);
    } catch {
      setToast({ type: "error", message: "Failed to copy documents" });
      toastTimerRef.current = setTimeout(() => setToast(null), 4000);
    } finally {
      setAddingToInvestigation(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="page-header mb-1">Search</h2>
          <p className="page-subtitle">
            Search across investigations and documents
          </p>
        </div>
        {selectedDocIds.size > 0 && (
          <button
            onClick={() => setShowPicker(true)}
            className={clsx(
              "inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium",
              "bg-primary-600 text-white hover:bg-primary-700",
              "dark:bg-primary-500 dark:hover:bg-primary-600",
              "shadow-sm transition-colors",
            )}
          >
            <FolderPlus className="h-4 w-4" />
            Add {selectedDocIds.size} to Investigation
          </button>
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

      {/* Search input */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-secondary-400" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search by title, filename, record ID..."
          className={clsx(
            "w-full rounded-xl border py-3.5 pl-12 pr-4 text-sm",
            "bg-white border-secondary-300 placeholder-secondary-400",
            "focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 focus:outline-none",
            "dark:bg-secondary-900 dark:border-secondary-600 dark:text-secondary-100",
            "dark:placeholder-secondary-500 dark:focus:border-primary-500",
          )}
          autoFocus
        />
      </div>

      {/* Type filter tabs */}
      <div className="flex gap-2">
        {(
          [
            { label: "All", value: undefined },
            { label: "Investigations", value: "investigation" as const },
            { label: "Documents", value: "document" as const },
          ] as const
        ).map((tab) => (
          <button
            key={tab.label}
            onClick={() => setTypeFilter(tab.value)}
            className={clsx(
              "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              typeFilter === tab.value
                ? "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300"
                : "text-secondary-600 hover:bg-secondary-100 dark:text-secondary-400 dark:hover:bg-secondary-800",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
        </div>
      ) : query.length < 2 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Search className="h-12 w-12 text-secondary-300 dark:text-secondary-600" />
          <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
            Type at least 2 characters to search
          </p>
        </div>
      ) : results.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16">
          <Search className="h-12 w-12 text-secondary-300 dark:text-secondary-600" />
          <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
            No results found for &quot;{query}&quot;
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Investigation results */}
          {investigationResults.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100 mb-3">
                Investigations ({investigationResults.length})
              </h3>
              <div className="space-y-2">
                {investigationResults.map((item) => (
                  <Link
                    key={item.id}
                    to={item.url}
                    className={clsx(
                      "flex items-start gap-3 rounded-xl p-4 transition-colors",
                      "bg-white border border-secondary-200 hover:border-primary-300 hover:bg-primary-50/30",
                      "dark:bg-secondary-900 dark:border-secondary-700 dark:hover:border-primary-500/50 dark:hover:bg-primary-500/5",
                    )}
                  >
                    <FolderSearch className="h-5 w-5 mt-0.5 text-primary-500 shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                        {item.title}
                      </p>
                      <p className="text-xs text-secondary-500 dark:text-secondary-400">
                        {item.subtitle}
                      </p>
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Document results */}
          {documentResults.length > 0 && (
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100 mb-3">
                Documents ({documentResults.length})
              </h3>
              <div className="space-y-2">
                {documentResults.map((item) => (
                  <div
                    key={item.id}
                    className={clsx(
                      "flex items-start gap-3 rounded-xl p-4 transition-colors",
                      "bg-white border hover:bg-primary-50/30",
                      "dark:bg-secondary-900 dark:hover:bg-primary-500/5",
                      selectedDocIds.has(item.id)
                        ? "border-primary-300 bg-primary-50/30 dark:border-primary-500/50 dark:bg-primary-500/5"
                        : "border-secondary-200 hover:border-primary-300 dark:border-secondary-700 dark:hover:border-primary-500/50",
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={selectedDocIds.has(item.id)}
                      onChange={() => toggleDocSelect(item.id)}
                      className="mt-1 rounded border-secondary-300 text-primary-600 focus:ring-primary-500 dark:border-secondary-600 dark:bg-secondary-800"
                    />
                    <Link to={item.url} className="flex items-start gap-3 min-w-0 flex-1">
                      <FileText className="h-5 w-5 mt-0.5 text-purple-500 shrink-0" />
                      <div>
                        <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                          {item.title}
                        </p>
                        <p className="text-xs text-secondary-500 dark:text-secondary-400">
                          {item.subtitle}
                        </p>
                      </div>
                    </Link>
                  </div>
                ))}
              </div>
            </div>
          )}
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
