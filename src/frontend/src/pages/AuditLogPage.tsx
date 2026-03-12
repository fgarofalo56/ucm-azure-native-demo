import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { AuditLogEntry, PaginatedResponse } from "../api/types";
import { AxiosError } from "axios";
import {
  Search,
  Download,
  Filter,
  ChevronLeft,
  ChevronRight,
  Loader2,
  AlertCircle,
  Lock,
  Inbox,
} from "lucide-react";
import { clsx } from "clsx";
import { format, formatDistanceToNow } from "date-fns";
import StatusBadge from "../components/ui/StatusBadge";
import Button from "../components/ui/Button";

function useAuditLogs(page: number) {
  return useQuery({
    queryKey: ["audit/logs", page],
    queryFn: async () => {
      const { data } = await apiClient.post<PaginatedResponse<AuditLogEntry>>(
        "/audit/logs",
        { page, page_size: 50 },
      );
      return data;
    },
  });
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  document_upload: "bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400",
  document_download: "bg-success-50 text-success-600 dark:bg-success-500/10 dark:text-success-400",
  document_delete: "bg-danger-50 text-danger-600 dark:bg-danger-500/10 dark:text-danger-400",
  investigation_create: "bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400",
  investigation_update: "bg-warning-50 text-warning-600 dark:bg-warning-500/10 dark:text-warning-400",
  auth_login: "bg-success-50 text-success-600 dark:bg-success-500/10 dark:text-success-400",
  auth_logout: "bg-secondary-100 text-secondary-600 dark:bg-secondary-800 dark:text-secondary-400",
};

function getEventTypeColor(eventType: string): string {
  return (
    EVENT_TYPE_COLORS[eventType] ??
    "bg-secondary-100 text-secondary-600 dark:bg-secondary-800 dark:text-secondary-400"
  );
}

export function AuditLogPage() {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("");
  const [resultFilter, setResultFilter] = useState("");
  const { data, isLoading, error } = useAuditLogs(page);

  const entries = data?.data ?? [];
  const total = data?.meta.total ?? 0;
  const pageSize = data?.meta.page_size ?? 50;
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  const isForbidden =
    error instanceof AxiosError && error.response?.status === 403;

  // Client-side filtering
  const filteredEntries = entries.filter((entry) => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matches =
        (entry.resource_id?.toLowerCase().includes(q) ?? false) ||
        (entry.user_principal_name?.toLowerCase().includes(q) ?? false) ||
        entry.event_type.toLowerCase().includes(q) ||
        entry.action.toLowerCase().includes(q);
      if (!matches) return false;
    }
    if (eventTypeFilter && entry.event_type !== eventTypeFilter) return false;
    if (resultFilter && entry.result !== resultFilter) return false;
    return true;
  });

  // Get unique event types from data
  const eventTypes = [...new Set(entries.map((e) => e.event_type))].sort();

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="page-header mb-1">Audit Log</h2>
          <p className="page-subtitle">
            Track all system events and user activities
          </p>
        </div>
        <Button
          variant="secondary"
          icon={<Download className="h-4 w-4" />}
          disabled
        >
          Export
        </Button>
      </div>

      {/* Filters */}
      <div className="card !p-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2 text-sm font-medium text-secondary-500 dark:text-secondary-400">
            <Filter className="h-4 w-4" />
            Filters
          </div>

          <div className="flex flex-1 flex-wrap gap-3">
            {/* Search */}
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-secondary-400" />
              <input
                type="text"
                placeholder="Search by user, resource, or action..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input pl-9"
              />
            </div>

            {/* Event type filter */}
            <select
              value={eventTypeFilter}
              onChange={(e) => setEventTypeFilter(e.target.value)}
              className="form-select min-w-[160px]"
            >
              <option value="">All Events</option>
              {eventTypes.map((type) => (
                <option key={type} value={type}>
                  {type.replace(/_/g, " ")}
                </option>
              ))}
            </select>

            {/* Result filter */}
            <select
              value={resultFilter}
              onChange={(e) => setResultFilter(e.target.value)}
              className="form-select min-w-[130px]"
            >
              <option value="">All Results</option>
              <option value="success">Success</option>
              <option value="failure">Failure</option>
              <option value="denied">Denied</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
            <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
              Loading audit logs...
            </p>
          </div>
        </div>
      ) : error ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            {isForbidden ? (
              <>
                <div className="rounded-full bg-warning-50 dark:bg-warning-500/10 p-4">
                  <Lock className="h-8 w-8 text-warning-500" />
                </div>
                <p className="mt-4 text-sm font-medium text-secondary-700 dark:text-secondary-300">
                  Access Denied
                </p>
                <p className="mt-1 text-sm text-secondary-500 dark:text-secondary-400">
                  You need Admin role to view audit logs.
                </p>
              </>
            ) : (
              <>
                <div className="rounded-full bg-danger-50 dark:bg-danger-500/10 p-4">
                  <AlertCircle className="h-8 w-8 text-danger-500" />
                </div>
                <p className="mt-4 text-sm font-medium text-secondary-700 dark:text-secondary-300">
                  Failed to load audit logs
                </p>
                <p className="mt-1 text-sm text-secondary-500 dark:text-secondary-400">
                  {error instanceof Error ? error.message : "Unknown error"}
                </p>
              </>
            )}
          </div>
        </div>
      ) : filteredEntries.length === 0 ? (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-16">
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
              <Inbox className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
            </div>
            <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
              {searchQuery || eventTypeFilter || resultFilter
                ? "No audit entries match your filters"
                : "No audit entries found"}
            </p>
          </div>
        </div>
      ) : (
        <>
          <div className="table-wrapper">
            <table className="min-w-full divide-y divide-secondary-200 dark:divide-secondary-700">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Timestamp</th>
                  <th className="table-header-cell">Event</th>
                  <th className="table-header-cell">User</th>
                  <th className="table-header-cell">Action</th>
                  <th className="table-header-cell">Result</th>
                  <th className="table-header-cell">Resource</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {filteredEntries.map((entry) => (
                  <tr key={entry.id} className="table-row">
                    <td className="table-cell whitespace-nowrap">
                      <div>
                        <p className="text-sm text-secondary-700 dark:text-secondary-300">
                          {format(
                            new Date(entry.event_timestamp),
                            "MMM d, HH:mm",
                          )}
                        </p>
                        <p className="text-xs text-secondary-400 dark:text-secondary-500">
                          {formatDistanceToNow(
                            new Date(entry.event_timestamp),
                            { addSuffix: true },
                          )}
                        </p>
                      </div>
                    </td>
                    <td className="table-cell">
                      <span
                        className={clsx(
                          "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium",
                          getEventTypeColor(entry.event_type),
                        )}
                      >
                        {entry.event_type.replace(/_/g, " ")}
                      </span>
                    </td>
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <div
                          className={clsx(
                            "flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-xs font-semibold",
                            "bg-secondary-100 text-secondary-500",
                            "dark:bg-secondary-800 dark:text-secondary-400",
                          )}
                        >
                          {(entry.user_principal_name ?? entry.user_id)
                            .charAt(0)
                            .toUpperCase()}
                        </div>
                        <span className="text-sm text-secondary-700 dark:text-secondary-300 truncate max-w-[160px]">
                          {entry.user_principal_name ?? entry.user_id}
                        </span>
                      </div>
                    </td>
                    <td className="table-cell">
                      <span className="text-sm text-secondary-600 dark:text-secondary-400">
                        {entry.action}
                      </span>
                    </td>
                    <td className="table-cell">
                      <StatusBadge
                        variant={
                          entry.result === "success"
                            ? "success"
                            : entry.result === "failure"
                              ? "error"
                              : "warning"
                        }
                        label={entry.result}
                        dot
                      />
                    </td>
                    <td className="table-cell">
                      {entry.resource_id ? (
                        <span className="inline-flex max-w-[180px] truncate rounded-md bg-secondary-100 dark:bg-secondary-800 px-2 py-0.5 text-xs font-mono text-secondary-500 dark:text-secondary-400">
                          {entry.resource_id}
                        </span>
                      ) : (
                        <span className="text-xs text-secondary-300 dark:text-secondary-600">
                          --
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <p className="text-sm text-secondary-500 dark:text-secondary-400">
              Showing{" "}
              <span className="font-medium text-secondary-700 dark:text-secondary-300">
                {filteredEntries.length}
              </span>{" "}
              of{" "}
              <span className="font-medium text-secondary-700 dark:text-secondary-300">
                {total}
              </span>{" "}
              entries
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
        </>
      )}
    </div>
  );
}
