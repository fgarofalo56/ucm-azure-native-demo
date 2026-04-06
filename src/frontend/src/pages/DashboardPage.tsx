import { Link } from "react-router-dom";
import { useInvestigations } from "../hooks/useInvestigations";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../api/client";
import type { AuditLogEntry, PaginatedResponse } from "../api/types";
import {
  FolderSearch,
  Activity,
  FileText,
  Clock,
  ArrowRight,
  TrendingUp,
  Loader2,
  AlertCircle,
  FileUp,
  Trash2,
  Edit,
  Eye,
  Shield,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { clsx } from "clsx";
import { formatDistanceToNow } from "date-fns";
import StatusBadge from "../components/ui/StatusBadge";

function useRecentAuditLogs() {
  return useQuery({
    queryKey: ["audit/logs", "recent"],
    queryFn: async () => {
      const { data } = await apiClient.post<PaginatedResponse<AuditLogEntry>>(
        "/audit/logs",
        { page: 1, page_size: 10 },
      );
      return data;
    },
    retry: false,
  });
}

const CHART_COLORS = [
  "#6366f1", // primary
  "#10b981", // success
  "#f59e0b", // warning
  "#f43f5e", // danger
  "#64748b", // secondary
  "#8b5cf6", // violet
  "#06b6d4", // cyan
  "#ec4899", // pink
];

const PIE_COLORS: Record<string, string> = {
  completed: "#10b981",
  pending: "#f59e0b",
  processing: "#6366f1",
  failed: "#f43f5e",
  not_required: "#64748b",
};

function getEventIcon(eventType: string) {
  if (eventType.includes("upload") || eventType.includes("create"))
    return FileUp;
  if (eventType.includes("delete")) return Trash2;
  if (eventType.includes("update") || eventType.includes("edit")) return Edit;
  if (eventType.includes("view") || eventType.includes("download")) return Eye;
  if (eventType.includes("auth") || eventType.includes("login")) return Shield;
  return Activity;
}

export function DashboardPage() {
  const { data, isLoading } = useInvestigations();
  const { data: auditData } = useRecentAuditLogs();

  const investigations = data?.data ?? [];
  const totalCount = data?.meta.total ?? 0;
  const activeCount = investigations.filter(
    (i) => i.status === "active",
  ).length;
  const docCount = investigations.reduce(
    (sum, i) => sum + i.document_count,
    0,
  );

  // Documents by investigation for bar chart (top 10 by doc count)
  const barChartData = [...investigations]
    .sort((a, b) => b.document_count - a.document_count)
    .slice(0, 10)
    .map((inv) => ({
      name:
        inv.record_id.length > 16
          ? inv.record_id.slice(0, 16) + "..."
          : inv.record_id,
      documents: inv.document_count,
      fullName: inv.title,
    }));

  // Simulated document status distribution based on what we know
  // In a real app this would come from a dedicated API endpoint
  const pendingCount = Math.max(0, Math.floor(docCount * 0.1));
  const processingCount = Math.max(0, Math.floor(docCount * 0.05));
  const failedCount = Math.max(0, Math.floor(docCount * 0.02));
  const completedCount = Math.max(
    0,
    docCount - pendingCount - processingCount - failedCount,
  );

  const pieChartData = [
    { name: "Completed", value: completedCount, key: "completed" },
    { name: "Pending", value: pendingCount, key: "pending" },
    { name: "Processing", value: processingCount, key: "processing" },
    { name: "Failed", value: failedCount, key: "failed" },
  ].filter((d) => d.value > 0);

  const recentAuditEntries = auditData?.data ?? [];

  return (
    <div className="space-y-6">
      {/* USDA Welcome Banner */}
      <div
        className={clsx(
          "rounded-2xl p-6 md:p-8",
          "bg-gradient-to-r from-[#004B87] to-[#4B7F52]",
          "text-white shadow-lg",
        )}
      >
        <div className="flex items-start gap-4">
          <div className="hidden md:flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-white/15 backdrop-blur-sm">
            <Shield className="h-7 w-7 text-white" />
          </div>
          <div>
            <h2 className="text-xl md:text-2xl font-bold">
              Welcome to AssuranceNet
            </h2>
            <p className="mt-2 text-sm md:text-base text-white/85 leading-relaxed max-w-2xl">
              AssuranceNet is a document management system for the USDA Food
              Safety and Inspection Service (FSIS). Manage investigations, upload
              and convert documents, merge PDFs, and maintain a complete audit
              trail &mdash; all within an Azure-native architecture.
            </p>
            <p className="mt-3 text-xs text-white/60">
              Demo purposes only. Data sourced from{" "}
              <a
                href="https://www.fsis.usda.gov/science-data"
                target="_blank"
                rel="noopener noreferrer"
                className="underline underline-offset-2 hover:text-white/80"
              >
                fsis.usda.gov/science-data
              </a>
            </p>
          </div>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<FolderSearch className="h-6 w-6" />}
          iconBg="bg-primary-50 dark:bg-primary-500/10"
          iconColor="text-primary-600 dark:text-primary-400"
          label="Total Investigations"
          value={isLoading ? "..." : totalCount}
          trend="+12% this month"
        />
        <StatCard
          icon={<Activity className="h-6 w-6" />}
          iconBg="bg-success-50 dark:bg-success-500/10"
          iconColor="text-success-600 dark:text-success-400"
          label="Active Investigations"
          value={isLoading ? "..." : activeCount}
          trend="Currently open"
        />
        <StatCard
          icon={<FileText className="h-6 w-6" />}
          iconBg="bg-purple-50 dark:bg-purple-500/10"
          iconColor="text-purple-600 dark:text-purple-400"
          label="Total Documents"
          value={isLoading ? "..." : docCount}
          trend="+8 this week"
        />
        <StatCard
          icon={<Clock className="h-6 w-6" />}
          iconBg="bg-warning-50 dark:bg-warning-500/10"
          iconColor="text-warning-600 dark:text-warning-400"
          label="Pending Conversion"
          value={isLoading ? "..." : pendingCount}
          trend="In queue"
        />
      </div>

      {/* Charts section */}
      {docCount > 0 && (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          {/* Bar chart */}
          <div className="card">
            <h3 className="mb-4 text-sm font-semibold text-secondary-900 dark:text-secondary-100">
              Documents by Investigation
            </h3>
            {barChartData.length > 0 ? (
              <div className="h-72 min-h-[288px]">
                <ResponsiveContainer width="100%" height="100%" debounce={50} minWidth={0} minHeight={0}>
                  <BarChart
                    data={barChartData}
                    margin={{ top: 5, right: 20, left: 0, bottom: 60 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      className="stroke-secondary-200 dark:stroke-secondary-700"
                    />
                    <XAxis
                      dataKey="name"
                      angle={-45}
                      textAnchor="end"
                      tick={{ fontSize: 11, fill: "currentColor" }}
                      className="text-secondary-500"
                      height={70}
                    />
                    <YAxis
                      tick={{ fontSize: 11, fill: "currentColor" }}
                      className="text-secondary-500"
                    />
                    <Tooltip
                      contentStyle={{
                        borderRadius: "8px",
                        border: "1px solid var(--tw-border-opacity, #e2e8f0)",
                        boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)",
                      }}
                      labelFormatter={(_, payload) =>
                        payload[0]?.payload?.fullName ?? ""
                      }
                    />
                    <Bar
                      dataKey="documents"
                      fill="#6366f1"
                      radius={[4, 4, 0, 0]}
                      maxBarSize={40}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyChartState />
            )}
          </div>

          {/* Pie chart */}
          <div className="card">
            <h3 className="mb-4 text-sm font-semibold text-secondary-900 dark:text-secondary-100">
              Document Status Distribution
            </h3>
            {pieChartData.length > 0 ? (
              <div className="h-72 min-h-[288px]">
                <ResponsiveContainer width="100%" height="100%" debounce={50} minWidth={0} minHeight={0}>
                  <PieChart>
                    <Pie
                      data={pieChartData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={4}
                      dataKey="value"
                      stroke="none"
                    >
                      {pieChartData.map((entry) => (
                        <Cell
                          key={entry.key}
                          fill={PIE_COLORS[entry.key] ?? CHART_COLORS[0]}
                        />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        borderRadius: "8px",
                        border: "1px solid #e2e8f0",
                        boxShadow: "0 4px 6px -1px rgba(0,0,0,0.05)",
                      }}
                    />
                    <Legend
                      verticalAlign="bottom"
                      iconType="circle"
                      formatter={(value) => (
                        <span className="text-sm text-secondary-600 dark:text-secondary-400">
                          {value}
                        </span>
                      )}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <EmptyChartState />
            )}
          </div>
        </div>
      )}

      {/* Two-column layout: Recent Activity & Recent Investigations */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Activity */}
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
              Recent Activity
            </h3>
            <Link
              to="/audit"
              className={clsx(
                "flex items-center gap-1 text-xs font-medium",
                "text-primary-600 hover:text-primary-700",
                "dark:text-primary-400 dark:hover:text-primary-300",
              )}
            >
              View All <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          {recentAuditEntries.length > 0 ? (
            <div className="space-y-1">
              {recentAuditEntries.slice(0, 8).map((entry) => {
                const EventIcon = getEventIcon(entry.event_type);
                return (
                  <div
                    key={entry.id}
                    className={clsx(
                      "flex items-start gap-3 rounded-lg px-3 py-2.5",
                      "hover:bg-secondary-50 dark:hover:bg-secondary-800/50",
                      "transition-colors",
                    )}
                  >
                    <div
                      className={clsx(
                        "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg mt-0.5",
                        entry.result === "success"
                          ? "bg-success-50 text-success-500 dark:bg-success-500/10"
                          : entry.result === "failure"
                            ? "bg-danger-50 text-danger-500 dark:bg-danger-500/10"
                            : "bg-secondary-100 text-secondary-400 dark:bg-secondary-800",
                      )}
                    >
                      <EventIcon className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm text-secondary-700 dark:text-secondary-300">
                        <span className="font-medium">
                          {entry.user_principal_name ?? "System"}
                        </span>{" "}
                        {entry.action}
                      </p>
                      <p className="text-xs text-secondary-400 dark:text-secondary-500">
                        {formatDistanceToNow(
                          new Date(entry.event_timestamp),
                          { addSuffix: true },
                        )}
                      </p>
                    </div>
                    <StatusBadge
                      variant={
                        entry.result === "success"
                          ? "success"
                          : entry.result === "failure"
                            ? "error"
                            : "warning"
                      }
                      label={entry.result}
                      size="sm"
                    />
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8">
              <Activity className="h-8 w-8 text-secondary-300 dark:text-secondary-600" />
              <p className="mt-2 text-sm text-secondary-400 dark:text-secondary-500">
                No recent activity
              </p>
            </div>
          )}
        </div>

        {/* Recent Investigations */}
        <div className="card">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
              Recent Investigations
            </h3>
            <Link
              to="/investigations"
              className={clsx(
                "flex items-center gap-1 text-xs font-medium",
                "text-primary-600 hover:text-primary-700",
                "dark:text-primary-400 dark:hover:text-primary-300",
              )}
            >
              View All <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
            </div>
          ) : investigations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8">
              <FolderSearch className="h-8 w-8 text-secondary-300 dark:text-secondary-600" />
              <p className="mt-2 text-sm text-secondary-400 dark:text-secondary-500">
                No investigations yet
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto -mx-6">
              <table className="min-w-full">
                <thead>
                  <tr className="border-b border-secondary-100 dark:border-secondary-800">
                    <th className="px-6 py-2.5 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                      Record ID
                    </th>
                    <th className="px-6 py-2.5 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                      Status
                    </th>
                    <th className="px-6 py-2.5 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                      Docs
                    </th>
                    <th className="px-6 py-2.5 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                      Updated
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {investigations.slice(0, 8).map((inv) => (
                    <tr
                      key={inv.id}
                      className="border-b border-secondary-50 dark:border-secondary-800/50 last:border-0"
                    >
                      <td className="px-6 py-3">
                        <Link
                          to={`/investigations/${inv.id}`}
                          className="group"
                        >
                          <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                            {inv.title}
                          </p>
                          <p className="text-xs text-secondary-400">
                            {inv.record_id}
                          </p>
                        </Link>
                      </td>
                      <td className="px-6 py-3">
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
                      <td className="px-6 py-3 text-right">
                        <span className="text-sm text-secondary-500 dark:text-secondary-400">
                          {inv.document_count}
                        </span>
                      </td>
                      <td className="px-6 py-3 text-right">
                        <span className="text-xs text-secondary-400 dark:text-secondary-500">
                          {formatDistanceToNow(new Date(inv.updated_at), {
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
        </div>
      </div>
    </div>
  );
}

function StatCard({
  icon,
  iconBg,
  iconColor,
  label,
  value,
  trend,
}: {
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  label: string;
  value: number | string;
  trend?: string;
}) {
  return (
    <div className="card-hover">
      <div className="flex items-start gap-4">
        <div
          className={clsx(
            "flex h-12 w-12 shrink-0 items-center justify-center rounded-xl",
            iconBg,
          )}
        >
          <span className={iconColor}>{icon}</span>
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-secondary-500 dark:text-secondary-400">
            {label}
          </p>
          <p className="mt-1 text-2xl font-bold text-secondary-900 dark:text-secondary-50">
            {value}
          </p>
          {trend && (
            <p className="mt-1 flex items-center gap-1 text-xs text-secondary-400 dark:text-secondary-500">
              <TrendingUp className="h-3 w-3" />
              {trend}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyChartState() {
  return (
    <div className="flex h-72 items-center justify-center">
      <div className="text-center">
        <AlertCircle className="mx-auto h-8 w-8 text-secondary-300 dark:text-secondary-600" />
        <p className="mt-2 text-sm text-secondary-400 dark:text-secondary-500">
          No data to display
        </p>
      </div>
    </div>
  );
}
