import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { Search, FolderSearch, FileText, Loader2 } from "lucide-react";
import { clsx } from "clsx";
import { useSearch } from "../hooks/useSearch";

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(initialQuery);
  const [typeFilter, setTypeFilter] = useState<
    "investigation" | "document" | undefined
  >(undefined);

  const { data, isLoading } = useSearch(query, typeFilter);
  const results = data?.results ?? [];

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

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-header mb-1">Search</h2>
        <p className="page-subtitle">
          Search across investigations and documents
        </p>
      </div>

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
                  <Link
                    key={item.id}
                    to={item.url}
                    className={clsx(
                      "flex items-start gap-3 rounded-xl p-4 transition-colors",
                      "bg-white border border-secondary-200 hover:border-primary-300 hover:bg-primary-50/30",
                      "dark:bg-secondary-900 dark:border-secondary-700 dark:hover:border-primary-500/50 dark:hover:bg-primary-500/5",
                    )}
                  >
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
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
