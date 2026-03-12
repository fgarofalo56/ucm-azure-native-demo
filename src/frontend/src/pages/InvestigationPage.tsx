import { useCallback, useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  useInvestigation,
  useUpdateInvestigation,
} from "../hooks/useInvestigations";
import { useDocuments } from "../hooks/useDocuments";
import { DocumentUpload } from "../components/documents/DocumentUpload";
import { DocumentList } from "../components/documents/DocumentList";
import { DocumentViewer } from "../components/documents/DocumentViewer";
import { VersionHistory } from "../components/documents/VersionHistory";
import { PdfMerge } from "../components/documents/PdfMerge";
import StatusBadge from "../components/ui/StatusBadge";
import Button from "../components/ui/Button";
import type { Document } from "../api/types";
import {
  ChevronRight,
  LayoutDashboard,
  FolderSearch,
  FileText,
  Activity,
  Calendar,
  User,
  Edit3,
  Check,
  X,
  Loader2,
  AlertCircle,
  ChevronDown,
} from "lucide-react";
import { clsx } from "clsx";
import { format, formatDistanceToNow } from "date-fns";

type Tab = "documents" | "details" | "activity";

export function InvestigationPage() {
  const { id } = useParams<{ id: string }>();
  const {
    data: investigation,
    isLoading: invLoading,
    error: invError,
  } = useInvestigation(id ?? "");
  const {
    data: docsData,
    isLoading: docsLoading,
    refetch,
  } = useDocuments(id ?? "");
  const updateMutation = useUpdateInvestigation(id ?? "");

  const [selectedFileIds, setSelectedFileIds] = useState<Set<string>>(
    new Set(),
  );
  const [activeTab, setActiveTab] = useState<Tab>("documents");
  const [editingTitle, setEditingTitle] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editingDesc, setEditingDesc] = useState(false);
  const [editDesc, setEditDesc] = useState("");
  const [statusDropdownOpen, setStatusDropdownOpen] = useState(false);
  const [viewingDoc, setViewingDoc] = useState<Document | null>(null);
  const [viewingVersions, setViewingVersions] = useState<Document | null>(null);

  const handleSelectForMerge = useCallback(
    (fileId: string, selected: boolean) => {
      setSelectedFileIds((prev) => {
        const next = new Set(prev);
        if (selected) {
          next.add(fileId);
        } else {
          next.delete(fileId);
        }
        return next;
      });
    },
    [],
  );

  const handleSaveTitle = async () => {
    if (editTitle.trim() && editTitle !== investigation?.title) {
      await updateMutation.mutateAsync({ title: editTitle });
    }
    setEditingTitle(false);
  };

  const handleSaveDesc = async () => {
    await updateMutation.mutateAsync({ description: editDesc });
    setEditingDesc(false);
  };

  const handleStatusChange = async (status: string) => {
    await updateMutation.mutateAsync({ status });
    setStatusDropdownOpen(false);
  };

  // Loading state
  if (invLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
        <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
          Loading investigation...
        </p>
      </div>
    );
  }

  // Error state
  if (invError) {
    const status = (invError as { response?: { status?: number } })?.response
      ?.status;
    return (
      <div className="mx-auto max-w-md py-24 text-center">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-danger-50 dark:bg-danger-500/10">
          <AlertCircle className="h-8 w-8 text-danger-500" />
        </div>
        <h3 className="mt-4 text-lg font-semibold text-secondary-900 dark:text-secondary-50">
          {status === 404
            ? "Investigation Not Found"
            : status === 403
              ? "Access Denied"
              : "Error Loading Investigation"}
        </h3>
        <p className="mt-2 text-sm text-secondary-500 dark:text-secondary-400">
          {status === 404
            ? "The investigation you're looking for doesn't exist."
            : status === 403
              ? "You don't have permission to view this investigation."
              : invError.message}
        </p>
        <Link to="/investigations">
          <Button variant="secondary" className="mt-6">
            Back to Investigations
          </Button>
        </Link>
      </div>
    );
  }

  if (!investigation) {
    return (
      <div className="mx-auto max-w-md py-24 text-center">
        <AlertCircle className="mx-auto h-12 w-12 text-secondary-300" />
        <p className="mt-4 text-secondary-500">Investigation not found.</p>
      </div>
    );
  }

  const documents = docsData?.data ?? [];
  const tabs: { key: Tab; label: string; icon: typeof FileText; count?: number }[] = [
    {
      key: "documents",
      label: "Documents",
      icon: FileText,
      count: documents.length,
    },
    { key: "details", label: "Details", icon: Activity },
    { key: "activity", label: "Activity", icon: Activity },
  ];

  return (
    <div className="space-y-6">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-1.5 text-sm">
        <Link
          to="/"
          className="flex items-center gap-1 text-secondary-400 hover:text-secondary-600 dark:text-secondary-500 dark:hover:text-secondary-300 transition-colors"
        >
          <LayoutDashboard className="h-3.5 w-3.5" />
          Dashboard
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-secondary-300 dark:text-secondary-600" />
        <Link
          to="/investigations"
          className="flex items-center gap-1 text-secondary-400 hover:text-secondary-600 dark:text-secondary-500 dark:hover:text-secondary-300 transition-colors"
        >
          <FolderSearch className="h-3.5 w-3.5" />
          Investigations
        </Link>
        <ChevronRight className="h-3.5 w-3.5 text-secondary-300 dark:text-secondary-600" />
        <span className="font-medium text-secondary-700 dark:text-secondary-200">
          {investigation.record_id}
        </span>
      </nav>

      {/* Investigation header card */}
      <div className="card">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1 min-w-0">
            {/* Title */}
            {editingTitle ? (
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  value={editTitle}
                  onChange={(e) => setEditTitle(e.target.value)}
                  className="form-input text-lg font-bold"
                  autoFocus
                />
                <button
                  onClick={handleSaveTitle}
                  className="rounded-lg p-1.5 text-success-600 hover:bg-success-50 dark:text-success-400 dark:hover:bg-success-500/10"
                >
                  <Check className="h-5 w-5" />
                </button>
                <button
                  onClick={() => setEditingTitle(false)}
                  className="rounded-lg p-1.5 text-secondary-400 hover:bg-secondary-100 dark:hover:bg-secondary-800"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 group">
                <h2 className="text-xl font-bold text-secondary-900 dark:text-secondary-50">
                  {investigation.title}
                </h2>
                <button
                  onClick={() => {
                    setEditTitle(investigation.title);
                    setEditingTitle(true);
                  }}
                  className="rounded-lg p-1 text-secondary-400 opacity-0 group-hover:opacity-100 hover:bg-secondary-100 dark:hover:bg-secondary-800 transition-all"
                >
                  <Edit3 className="h-4 w-4" />
                </button>
              </div>
            )}

            <p className="mt-1 text-sm text-secondary-500 dark:text-secondary-400">
              {investigation.record_id}
            </p>

            {/* Description */}
            {editingDesc ? (
              <div className="mt-3">
                <textarea
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  className="form-textarea"
                  rows={2}
                  autoFocus
                />
                <div className="mt-2 flex gap-2">
                  <Button size="xs" onClick={handleSaveDesc}>
                    Save
                  </Button>
                  <Button
                    size="xs"
                    variant="ghost"
                    onClick={() => setEditingDesc(false)}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="mt-2 group/desc">
                {investigation.description ? (
                  <p className="text-sm text-secondary-600 dark:text-secondary-400">
                    {investigation.description}
                    <button
                      onClick={() => {
                        setEditDesc(investigation.description ?? "");
                        setEditingDesc(true);
                      }}
                      className="ml-2 text-secondary-400 opacity-0 group-hover/desc:opacity-100 hover:text-secondary-600 dark:hover:text-secondary-300 transition-all"
                    >
                      <Edit3 className="inline h-3.5 w-3.5" />
                    </button>
                  </p>
                ) : (
                  <button
                    onClick={() => {
                      setEditDesc("");
                      setEditingDesc(true);
                    }}
                    className="text-sm text-secondary-400 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                  >
                    + Add description
                  </button>
                )}
              </div>
            )}

            {/* Meta info */}
            <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-xs text-secondary-400 dark:text-secondary-500">
              <span className="flex items-center gap-1.5">
                <User className="h-3.5 w-3.5" />
                {investigation.created_by_name ?? investigation.created_by}
              </span>
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5" />
                {format(new Date(investigation.created_at), "PP")}
              </span>
              <span className="flex items-center gap-1.5">
                <FileText className="h-3.5 w-3.5" />
                {documents.length} document{documents.length !== 1 ? "s" : ""}
              </span>
              <span className="flex items-center gap-1.5">
                Updated{" "}
                {formatDistanceToNow(new Date(investigation.updated_at), {
                  addSuffix: true,
                })}
              </span>
            </div>
          </div>

          {/* Status control */}
          <div className="relative">
            <button
              onClick={() => setStatusDropdownOpen(!statusDropdownOpen)}
              className={clsx(
                "flex items-center gap-2 rounded-lg border px-3 py-2 transition-colors",
                "border-secondary-200 hover:border-secondary-300",
                "dark:border-secondary-700 dark:hover:border-secondary-600",
              )}
            >
              <StatusBadge
                variant={
                  investigation.status === "active"
                    ? "success"
                    : investigation.status === "closed"
                      ? "neutral"
                      : "warning"
                }
                label={investigation.status}
                dot
                size="md"
              />
              <ChevronDown className="h-4 w-4 text-secondary-400" />
            </button>
            {statusDropdownOpen && (
              <div
                className={clsx(
                  "absolute right-0 top-full mt-1 w-40 z-20",
                  "rounded-lg border bg-white shadow-lg py-1",
                  "dark:bg-secondary-900 dark:border-secondary-700",
                  "border-secondary-200",
                )}
              >
                {(["active", "closed", "archived"] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleStatusChange(s)}
                    className={clsx(
                      "flex w-full items-center gap-2 px-3 py-2 text-sm transition-colors",
                      s === investigation.status
                        ? "bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-300"
                        : "text-secondary-700 hover:bg-secondary-50 dark:text-secondary-300 dark:hover:bg-secondary-800",
                    )}
                  >
                    <StatusBadge
                      variant={
                        s === "active"
                          ? "success"
                          : s === "closed"
                            ? "neutral"
                            : "warning"
                      }
                      label={s}
                      dot
                    />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Document upload */}
      <DocumentUpload
        investigationId={investigation.id}
        onUploadComplete={() => refetch()}
      />

      {/* Tabs */}
      <div
        className={clsx(
          "flex gap-1 border-b",
          "border-secondary-200 dark:border-secondary-700",
        )}
      >
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={clsx(
              "flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors -mb-px",
              activeTab === tab.key
                ? "border-primary-600 text-primary-700 dark:border-primary-400 dark:text-primary-300"
                : "border-transparent text-secondary-500 hover:text-secondary-700 hover:border-secondary-300 dark:text-secondary-400 dark:hover:text-secondary-200",
            )}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
            {tab.count !== undefined && (
              <span
                className={clsx(
                  "inline-flex min-w-[20px] items-center justify-center rounded-full px-1.5 py-0.5 text-xs",
                  activeTab === tab.key
                    ? "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300"
                    : "bg-secondary-100 text-secondary-500 dark:bg-secondary-800 dark:text-secondary-400",
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === "documents" && (
        <div className="space-y-4">
          {/* Merge bar */}
          <PdfMerge
            recordId={investigation.record_id}
            selectedFileIds={Array.from(selectedFileIds)}
            onClear={() => setSelectedFileIds(new Set())}
          />

          {/* Document detail/version panels */}
          {viewingDoc && (
            <DocumentViewer
              document={viewingDoc}
              onClose={() => setViewingDoc(null)}
            />
          )}
          {viewingVersions && (
            <VersionHistory
              documentId={viewingVersions.id}
              onClose={() => setViewingVersions(null)}
            />
          )}

          {docsLoading ? (
            <div className="card">
              <div className="flex flex-col items-center justify-center py-12">
                <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
                <p className="mt-3 text-sm text-secondary-500 dark:text-secondary-400">
                  Loading documents...
                </p>
              </div>
            </div>
          ) : (
            <DocumentList
              documents={documents}
              onRefresh={() => refetch()}
              onSelectForMerge={handleSelectForMerge}
              selectedForMerge={selectedFileIds}
              onViewDetails={(doc) => setViewingDoc(doc)}
              onViewVersions={(doc) => setViewingVersions(doc)}
            />
          )}
        </div>
      )}

      {activeTab === "details" && (
        <div className="card">
          <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100 mb-4">
            Investigation Details
          </h3>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <DetailItem
              label="Investigation ID"
              value={investigation.id}
            />
            <DetailItem
              label="Record ID"
              value={investigation.record_id}
            />
            <DetailItem
              label="Status"
              value={
                <StatusBadge
                  variant={
                    investigation.status === "active"
                      ? "success"
                      : investigation.status === "closed"
                        ? "neutral"
                        : "warning"
                  }
                  label={investigation.status}
                  dot
                />
              }
            />
            <DetailItem
              label="Created By"
              value={investigation.created_by_name ?? investigation.created_by}
            />
            <DetailItem
              label="Created At"
              value={format(new Date(investigation.created_at), "PPpp")}
            />
            <DetailItem
              label="Last Updated"
              value={format(new Date(investigation.updated_at), "PPpp")}
            />
            <div className="sm:col-span-2">
              <DetailItem
                label="Description"
                value={investigation.description ?? "No description provided"}
              />
            </div>
          </dl>
        </div>
      )}

      {activeTab === "activity" && (
        <div className="card">
          <div className="flex flex-col items-center justify-center py-12">
            <div className="rounded-xl bg-secondary-100 dark:bg-secondary-800 p-4">
              <Activity className="h-8 w-8 text-secondary-400 dark:text-secondary-500" />
            </div>
            <p className="mt-4 text-sm font-medium text-secondary-500 dark:text-secondary-400">
              Activity timeline coming soon
            </p>
            <p className="mt-1 text-xs text-secondary-400 dark:text-secondary-500">
              Check the Audit Log for investigation-level activity
            </p>
            <Link to="/audit">
              <Button variant="secondary" size="sm" className="mt-4">
                View Audit Log
              </Button>
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

function DetailItem({
  label,
  value,
}: {
  label: string;
  value: React.ReactNode;
}) {
  return (
    <div>
      <dt className="text-xs font-medium text-secondary-500 dark:text-secondary-400">
        {label}
      </dt>
      <dd className="mt-1 text-sm text-secondary-900 dark:text-secondary-100">
        {value}
      </dd>
    </div>
  );
}
