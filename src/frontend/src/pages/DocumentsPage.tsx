import { Link } from "react-router-dom";
import { useInvestigations } from "../hooks/useInvestigations";
import {
  FileText,
  FolderSearch,
  ArrowRight,
  Loader2,
  Inbox,
} from "lucide-react";
import { clsx } from "clsx";
import StatusBadge from "../components/ui/StatusBadge";

export function DocumentsPage() {
  const { data, isLoading } = useInvestigations();

  const investigations = data?.data ?? [];
  const totalDocs = investigations.reduce(
    (sum, i) => sum + i.document_count,
    0,
  );

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="page-header mb-1">Documents</h2>
        <p className="page-subtitle">
          Browse documents across all investigations.{" "}
          {totalDocs > 0 && (
            <span className="font-medium text-secondary-600 dark:text-secondary-300">
              {totalDocs} total documents
            </span>
          )}
        </p>
      </div>

      {isLoading ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
            <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
              Loading...
            </p>
          </div>
        </div>
      ) : investigations.length === 0 ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
              <Inbox className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
            </div>
            <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
              No documents found
            </p>
            <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
              Documents are organized within investigations. Create an
              investigation first.
            </p>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {investigations
            .filter((inv) => inv.document_count > 0)
            .sort((a, b) => b.document_count - a.document_count)
            .map((inv) => (
              <Link
                key={inv.id}
                to={`/investigations/${inv.id}`}
                className="card-hover group"
              >
                <div className="flex items-start justify-between">
                  <div
                    className={clsx(
                      "flex h-10 w-10 items-center justify-center rounded-xl",
                      "bg-primary-50 dark:bg-primary-500/10",
                    )}
                  >
                    <FolderSearch className="h-5 w-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <ArrowRight
                    className={clsx(
                      "h-4 w-4 text-secondary-300 dark:text-secondary-600",
                      "group-hover:text-primary-500 group-hover:translate-x-0.5 transition-all",
                    )}
                  />
                </div>
                <div className="mt-3">
                  <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    {inv.title}
                  </h3>
                  <p className="mt-0.5 text-xs text-secondary-400 dark:text-secondary-500">
                    {inv.record_id}
                  </p>
                </div>
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-sm text-secondary-500 dark:text-secondary-400">
                    <FileText className="h-3.5 w-3.5" />
                    <span className="font-medium">
                      {inv.document_count}
                    </span>{" "}
                    document{inv.document_count !== 1 ? "s" : ""}
                  </div>
                  <StatusBadge
                    variant={
                      inv.status === "active"
                        ? "success"
                        : inv.status === "closed"
                          ? "neutral"
                          : "warning"
                    }
                    label={inv.status}
                    dot
                  />
                </div>
              </Link>
            ))}

          {/* Investigations with no documents */}
          {investigations.some((inv) => inv.document_count === 0) && (
            <div className="sm:col-span-2 lg:col-span-3">
              <p className="text-xs font-medium text-secondary-400 dark:text-secondary-500 uppercase tracking-wider mt-4 mb-3">
                Investigations without documents
              </p>
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {investigations
                  .filter((inv) => inv.document_count === 0)
                  .map((inv) => (
                    <Link
                      key={inv.id}
                      to={`/investigations/${inv.id}`}
                      className={clsx(
                        "flex items-center gap-3 rounded-xl border px-4 py-3 transition-all",
                        "border-secondary-200 hover:border-primary-300 hover:bg-primary-50/30",
                        "dark:border-secondary-700 dark:hover:border-primary-500/30 dark:hover:bg-primary-500/5",
                      )}
                    >
                      <FolderSearch className="h-4 w-4 text-secondary-400" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-secondary-700 dark:text-secondary-300 truncate">
                          {inv.title}
                        </p>
                        <p className="text-xs text-secondary-400 dark:text-secondary-500">
                          {inv.record_id}
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
