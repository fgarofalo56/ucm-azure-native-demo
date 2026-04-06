import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  useInvestigations,
  useCreateInvestigation,
} from "../hooks/useInvestigations";
import {
  Plus,
  Search,
  FolderSearch,
  FileText,
  Loader2,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
} from "lucide-react";
import { clsx } from "clsx";
import { formatDistanceToNow } from "date-fns";
import StatusBadge from "../components/ui/StatusBadge";
import Button from "../components/ui/Button";
import Modal from "../components/ui/Modal";

type StatusFilter = "all" | "active" | "closed" | "archived";

export function InvestigationsListPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [recordId, setRecordId] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [page, setPage] = useState(1);

  // Debounce search query to avoid excessive API calls
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery.trim());
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const { data, isLoading, error } = useInvestigations(
    statusFilter === "all" ? undefined : statusFilter,
    page,
    debouncedSearch || undefined,
  );
  const createMutation = useCreateInvestigation();

  const investigations = data?.data ?? [];
  const total = data?.meta.total ?? 0;
  const pageSize = data?.meta.page_size ?? 20;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const statusCounts = data?.meta.status_counts ?? {};

  // Use global status counts from backend
  const allCount = Object.values(statusCounts).reduce((a, b) => a + b, 0);
  const activeCount = statusCounts["active"] ?? 0;
  const closedCount = statusCounts["closed"] ?? 0;
  const archivedCount = statusCounts["archived"] ?? 0;

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recordId || !title) return;
    if (!/^INVESTIGATION-\d+$/.test(recordId)) return;
    await createMutation.mutateAsync({
      record_id: recordId,
      title,
      description: description || undefined,
    });
    setShowCreate(false);
    setRecordId("");
    setTitle("");
    setDescription("");
  };

  const statusTabs: {
    key: StatusFilter;
    label: string;
    count: number;
  }[] = [
    { key: "all", label: "All", count: allCount },
    { key: "active", label: "Active", count: activeCount },
    { key: "closed", label: "Closed", count: closedCount },
    { key: "archived", label: "Archived", count: archivedCount },
  ];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="page-header mb-1">Investigations</h2>
          <p className="page-subtitle">
            Manage and track investigation cases and their documents
          </p>
        </div>
        <Button
          icon={<Plus className="h-4 w-4" />}
          onClick={() => setShowCreate(true)}
        >
          New Investigation
        </Button>
      </div>

      {/* Filters bar */}
      <div className="card !p-4">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          {/* Status tabs */}
          <div className="flex gap-1 rounded-lg bg-secondary-100 dark:bg-secondary-800 p-1">
            {statusTabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => {
                  setStatusFilter(tab.key);
                  setPage(1);
                }}
                className={clsx(
                  "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-all",
                  statusFilter === tab.key
                    ? "bg-white text-secondary-900 shadow-sm dark:bg-secondary-700 dark:text-secondary-100"
                    : "text-secondary-500 hover:text-secondary-700 dark:text-secondary-400 dark:hover:text-secondary-200",
                )}
              >
                {tab.label}
                <span
                  className={clsx(
                    "inline-flex min-w-[20px] items-center justify-center rounded-full px-1.5 py-0.5 text-xs",
                    statusFilter === tab.key
                      ? "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300"
                      : "bg-secondary-200 text-secondary-500 dark:bg-secondary-700 dark:text-secondary-400",
                  )}
                >
                  {tab.count}
                </span>
              </button>
            ))}
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-secondary-400" />
            <input
              type="text"
              placeholder="Search by title or record ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={clsx(
                "form-input pl-9 w-full sm:w-72",
              )}
            />
          </div>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div
          className={clsx(
            "flex items-center gap-3 rounded-xl px-4 py-3",
            "bg-danger-50 text-danger-700 border border-danger-200",
            "dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
          )}
        >
          <AlertCircle className="h-5 w-5 shrink-0" />
          <p className="text-sm">
            Failed to load investigations. Please try again.
          </p>
        </div>
      )}

      {/* Table */}
      {isLoading ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
            <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
              Loading investigations...
            </p>
          </div>
        </div>
      ) : investigations.length === 0 ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
              <FolderSearch className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
            </div>
            <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
              {searchQuery
                ? "No investigations match your search"
                : "No investigations yet"}
            </p>
            <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
              {searchQuery
                ? "Try adjusting your search terms"
                : 'Click "New Investigation" to create one'}
            </p>
          </div>
        </div>
      ) : (
        <div className="table-wrapper">
          <table className="min-w-full divide-y divide-secondary-200 dark:divide-secondary-700">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell">Record ID</th>
                <th className="table-header-cell">Title</th>
                <th className="table-header-cell">Status</th>
                <th className="table-header-cell">Documents</th>
                <th className="table-header-cell">Created By</th>
                <th className="table-header-cell">Created</th>
              </tr>
            </thead>
            <tbody className="table-body">
              {investigations.map((inv) => (
                <tr key={inv.id} className="table-row group">
                  <td className="table-cell">
                    <Link
                      to={`/investigations/${inv.id}`}
                      className="text-sm font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                    >
                      {inv.record_id}
                    </Link>
                  </td>
                  <td className="table-cell">
                    <Link
                      to={`/investigations/${inv.id}`}
                      className="text-sm text-secondary-900 dark:text-secondary-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors"
                    >
                      {inv.title}
                    </Link>
                  </td>
                  <td className="table-cell">
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
                  </td>
                  <td className="table-cell">
                    <div className="flex items-center gap-1.5">
                      <FileText className="h-3.5 w-3.5 text-secondary-400" />
                      <span className="text-sm text-secondary-500 dark:text-secondary-400">
                        {inv.document_count}
                      </span>
                    </div>
                  </td>
                  <td className="table-cell">
                    <span className="text-sm text-secondary-500 dark:text-secondary-400">
                      {inv.created_by_name ?? "Unknown"}
                    </span>
                  </td>
                  <td className="table-cell whitespace-nowrap">
                    <span className="text-sm text-secondary-400 dark:text-secondary-500">
                      {formatDistanceToNow(new Date(inv.created_at), {
                        addSuffix: true,
                      })}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {!isLoading && total > 0 && (
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-sm text-secondary-500 dark:text-secondary-400">
            Showing{" "}
            <span className="font-medium text-secondary-700 dark:text-secondary-300">
              {investigations.length}
            </span>{" "}
            of{" "}
            <span className="font-medium text-secondary-700 dark:text-secondary-300">
              {total}
            </span>{" "}
            investigations
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className={clsx(
                "rounded-lg p-2 transition-colors",
                "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
                "dark:text-secondary-400 dark:hover:bg-secondary-800",
                "disabled:opacity-40 disabled:pointer-events-none",
              )}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (page <= 3) {
                pageNum = i + 1;
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = page - 2 + i;
              }
              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={clsx(
                    "flex h-8 w-8 items-center justify-center rounded-lg text-sm font-medium transition-colors",
                    page === pageNum
                      ? "bg-primary-600 text-white dark:bg-primary-500"
                      : clsx(
                          "text-secondary-600 hover:bg-secondary-100",
                          "dark:text-secondary-400 dark:hover:bg-secondary-800",
                        ),
                  )}
                >
                  {pageNum}
                </button>
              );
            })}
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className={clsx(
                "rounded-lg p-2 transition-colors",
                "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
                "dark:text-secondary-400 dark:hover:bg-secondary-800",
                "disabled:opacity-40 disabled:pointer-events-none",
              )}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Create Modal */}
      <Modal
        isOpen={showCreate}
        onClose={() => setShowCreate(false)}
        title="New Investigation"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => setShowCreate(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              form="create-investigation-form"
              loading={createMutation.isPending}
              disabled={!recordId || !title}
              icon={<Plus className="h-4 w-4" />}
            >
              Create Investigation
            </Button>
          </>
        }
      >
        <form
          id="create-investigation-form"
          onSubmit={handleCreate}
          className="space-y-4"
        >
          <div>
            <label className="form-label">Record ID</label>
            <input
              type="text"
              placeholder="e.g., INVESTIGATION-12345"
              value={recordId}
              onChange={(e) => setRecordId(e.target.value)}
              required
              pattern="^INVESTIGATION-\d+$"
              className="form-input"
            />
            <p className="mt-1.5 text-xs text-secondary-400 dark:text-secondary-500">
              Format: INVESTIGATION-#####
            </p>
          </div>
          <div>
            <label className="form-label">Title</label>
            <input
              type="text"
              placeholder="Investigation title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="form-input"
            />
          </div>
          <div>
            <label className="form-label">
              Description{" "}
              <span className="text-secondary-400 font-normal">(optional)</span>
            </label>
            <textarea
              placeholder="Brief description of the investigation..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="form-textarea"
              rows={3}
            />
          </div>
          {createMutation.isError && (
            <div
              className={clsx(
                "flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm",
                "bg-danger-50 text-danger-700 border border-danger-200",
                "dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
              )}
            >
              <AlertCircle className="h-4 w-4 shrink-0" />
              {(createMutation.error as { response?: { data?: { detail?: string } } })
                ?.response?.data?.detail ||
                "Failed to create investigation. Please try again."}
            </div>
          )}
        </form>
      </Modal>
    </div>
  );
}
