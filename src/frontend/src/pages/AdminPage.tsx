import { useEffect, useState } from "react";
import {
  Shield,
  Loader2,
  Check,
  X,
  Settings,
  Save,
  Key,
  FileText,
  ShieldCheck,
} from "lucide-react";
import { clsx } from "clsx";
import { useUsers, useRoles, useAssignRoles } from "../hooks/useAdmin";
import { formatDistanceToNow } from "date-fns";
import type { AppUser } from "../api/types";
import {
  getSystemSettings,
  updateSystemSettings,
  type SystemSettings,
} from "../api/admin";

export function AdminPage() {
  const [page, setPage] = useState(1);
  const { data: usersData, isLoading } = useUsers(page);
  const [editingUser, setEditingUser] = useState<AppUser | null>(null);

  const users = usersData?.data ?? [];
  const total = usersData?.meta.total ?? 0;
  const totalPages = Math.ceil(total / 20);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="page-header mb-1">Administration</h2>
        <p className="page-subtitle">Manage users and role assignments</p>
      </div>

      {/* User table */}
      <div className="card overflow-hidden p-0">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
          </div>
        ) : (
          <>
            <table className="min-w-full">
              <thead>
                <tr className="border-b border-secondary-200 dark:border-secondary-700">
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                    Roles
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-secondary-400">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                    Last Login
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider text-secondary-400">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr
                    key={user.id}
                    className="border-b border-secondary-100 dark:border-secondary-800 last:border-0"
                  >
                    <td className="px-6 py-3">
                      <div className="flex items-center gap-3">
                        <div
                          className={clsx(
                            "flex h-9 w-9 items-center justify-center rounded-lg",
                            "bg-primary-100 text-primary-700 font-semibold text-sm",
                            "dark:bg-primary-500/20 dark:text-primary-300",
                          )}
                        >
                          {user.display_name
                            .split(" ")
                            .map((n) => n[0])
                            .join("")
                            .toUpperCase()
                            .slice(0, 2)}
                        </div>
                        <div>
                          <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                            {user.display_name}
                          </p>
                          <p className="text-xs text-secondary-500 dark:text-secondary-400">
                            {user.email ?? "No email"}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex flex-wrap gap-1.5">
                        {user.roles.map((role) => (
                          <span
                            key={role.id}
                            className={clsx(
                              "inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
                              role.name === "admin"
                                ? "bg-danger-100 text-danger-700 dark:bg-danger-500/20 dark:text-danger-300"
                                : "bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-primary-300",
                            )}
                          >
                            <Shield className="h-3 w-3" />
                            {role.display_name}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-6 py-3">
                      <span
                        className={clsx(
                          "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
                          user.is_active
                            ? "bg-success-100 text-success-700 dark:bg-success-500/20 dark:text-success-300"
                            : "bg-secondary-100 text-secondary-500 dark:bg-secondary-800 dark:text-secondary-400",
                        )}
                      >
                        <span
                          className={clsx(
                            "h-1.5 w-1.5 rounded-full",
                            user.is_active
                              ? "bg-success-500"
                              : "bg-secondary-400",
                          )}
                        />
                        {user.is_active ? "Active" : "Inactive"}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-right">
                      <span className="text-xs text-secondary-400 dark:text-secondary-500">
                        {user.last_login_at
                          ? formatDistanceToNow(new Date(user.last_login_at), {
                              addSuffix: true,
                            })
                          : "Never"}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-right">
                      <button
                        onClick={() => setEditingUser(user)}
                        className={clsx(
                          "rounded-lg px-3 py-1.5 text-xs font-medium transition-colors",
                          "text-primary-600 hover:bg-primary-50",
                          "dark:text-primary-400 dark:hover:bg-primary-500/10",
                        )}
                      >
                        Edit Roles
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between border-t border-secondary-200 dark:border-secondary-700 px-6 py-3">
                <p className="text-xs text-secondary-500">
                  {total} users total
                </p>
                <div className="flex gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map(
                    (p) => (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={clsx(
                          "h-8 w-8 rounded-lg text-xs font-medium transition-colors",
                          p === page
                            ? "bg-primary-600 text-white"
                            : "text-secondary-600 hover:bg-secondary-100 dark:text-secondary-400 dark:hover:bg-secondary-800",
                        )}
                      >
                        {p}
                      </button>
                    ),
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Role assignment modal */}
      {editingUser && (
        <RoleAssignmentModal
          user={editingUser}
          onClose={() => setEditingUser(null)}
        />
      )}

      {/* System Settings */}
      <SystemSettingsPanel />
    </div>
  );
}

function RoleAssignmentModal({
  user,
  onClose,
}: {
  user: AppUser;
  onClose: () => void;
}) {
  const { data: roles } = useRoles();
  const assignMutation = useAssignRoles();
  const [selectedRoles, setSelectedRoles] = useState<string[]>(
    user.roles.map((r) => r.name),
  );

  const toggleRole = (roleName: string) => {
    setSelectedRoles((prev) =>
      prev.includes(roleName)
        ? prev.filter((r) => r !== roleName)
        : [...prev, roleName],
    );
  };

  const handleSave = () => {
    assignMutation.mutate(
      { userId: user.id, roleNames: selectedRoles },
      { onSuccess: onClose },
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div
        className={clsx(
          "w-full max-w-md rounded-2xl p-6",
          "bg-white dark:bg-secondary-900",
          "border border-secondary-200 dark:border-secondary-700",
          "shadow-xl",
        )}
      >
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-lg font-semibold text-secondary-900 dark:text-secondary-50">
              Edit Roles
            </h3>
            <p className="text-sm text-secondary-500 dark:text-secondary-400">
              {user.display_name}
            </p>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg p-1.5 text-secondary-400 hover:bg-secondary-100 dark:hover:bg-secondary-800"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-2 mb-6">
          {(roles ?? []).map((role) => (
            <button
              key={role.id}
              onClick={() => toggleRole(role.name)}
              className={clsx(
                "flex w-full items-center justify-between rounded-xl border p-3.5 transition-all",
                selectedRoles.includes(role.name)
                  ? "border-primary-500 bg-primary-50/50 dark:bg-primary-500/10 dark:border-primary-500/50"
                  : "border-secondary-200 hover:border-secondary-300 dark:border-secondary-700 dark:hover:border-secondary-600",
              )}
            >
              <div className="text-left">
                <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                  {role.display_name}
                </p>
                <p className="text-xs text-secondary-500 dark:text-secondary-400">
                  {role.description}
                </p>
              </div>
              {selectedRoles.includes(role.name) && (
                <Check className="h-5 w-5 text-primary-600 dark:text-primary-400 shrink-0" />
              )}
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className={clsx(
              "flex-1 rounded-xl px-4 py-2.5 text-sm font-medium transition-colors",
              "border border-secondary-300 text-secondary-700 hover:bg-secondary-50",
              "dark:border-secondary-600 dark:text-secondary-300 dark:hover:bg-secondary-800",
            )}
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={
              assignMutation.isPending || selectedRoles.length === 0
            }
            className={clsx(
              "flex-1 rounded-xl px-4 py-2.5 text-sm font-medium transition-colors",
              "bg-primary-600 text-white hover:bg-primary-700",
              "dark:bg-primary-500 dark:hover:bg-primary-600",
              "disabled:opacity-50 disabled:cursor-not-allowed",
            )}
          >
            {assignMutation.isPending ? "Saving..." : "Save Roles"}
          </button>
        </div>
      </div>
    </div>
  );
}

function SystemSettingsPanel() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Local form state
  const [pdfEngine, setPdfEngine] = useState("opensource");
  const [malwareScanning, setMalwareScanning] = useState(true);
  const [gotenbergUrl, setGotenbergUrl] = useState("");
  const [asposeWordsLicense, setAsposeWordsLicense] = useState("");
  const [asposeCellsLicense, setAsposeCellsLicense] = useState("");
  const [asposeSlidesLicense, setAsposeSlidesLicense] = useState("");

  useEffect(() => {
    getSystemSettings()
      .then((data) => {
        setSettings(data);
        setPdfEngine(data.pdf_engine?.value ?? "opensource");
        setMalwareScanning(
          (data.malware_scanning_enabled?.value ?? "true").toLowerCase() === "true",
        );
        setGotenbergUrl(data.gotenberg_url?.value ?? "");
        // Don't prefill license keys (they're masked)
      })
      .catch((err) => {
        if (err?.response?.status === 403) {
          setError("Admin access required to view system settings.");
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    setSuccess(false);

    try {
      const updates: Record<string, string> = {
        pdf_engine: pdfEngine,
        malware_scanning_enabled: malwareScanning ? "true" : "false",
        gotenberg_url: gotenbergUrl,
      };
      // Only send license keys if the user typed something new (not masked)
      if (asposeWordsLicense && !asposeWordsLicense.startsWith("••")) {
        updates.aspose_words_license = asposeWordsLicense;
      }
      if (asposeCellsLicense && !asposeCellsLicense.startsWith("••")) {
        updates.aspose_cells_license = asposeCellsLicense;
      }
      if (asposeSlidesLicense && !asposeSlidesLicense.startsWith("••")) {
        updates.aspose_slides_license = asposeSlidesLicense;
      }

      const updated = await updateSystemSettings(updates);
      setSettings(updated);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 text-primary-500 animate-spin" />
        </div>
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="card">
        <p className="text-sm text-secondary-500 dark:text-secondary-400 text-center py-8">
          {error}
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-500/10">
            <Settings className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
              System Settings
            </h3>
            <p className="text-xs text-secondary-500 dark:text-secondary-400">
              PDF engine, malware scanning, and license configuration
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* PDF Engine Selection */}
        <div>
          <label className="flex items-center gap-2 text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-3">
            <FileText className="h-4 w-4" />
            PDF Conversion Engine
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => setPdfEngine("opensource")}
              className={clsx(
                "rounded-xl border p-4 text-left transition-all",
                pdfEngine === "opensource"
                  ? "border-primary-500 bg-primary-50/50 dark:bg-primary-500/10 dark:border-primary-500/50"
                  : "border-secondary-200 hover:border-secondary-300 dark:border-secondary-700",
              )}
            >
              <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Open Source
              </p>
              <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
                Pillow (images) + fpdf2 (text/CSV) + Gotenberg (Office, optional)
              </p>
              {pdfEngine === "opensource" && (
                <Check className="h-4 w-4 text-primary-600 dark:text-primary-400 mt-2" />
              )}
            </button>
            <button
              onClick={() => setPdfEngine("aspose")}
              className={clsx(
                "rounded-xl border p-4 text-left transition-all",
                pdfEngine === "aspose"
                  ? "border-primary-500 bg-primary-50/50 dark:bg-primary-500/10 dark:border-primary-500/50"
                  : "border-secondary-200 hover:border-secondary-300 dark:border-secondary-700",
              )}
            >
              <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Aspose (Licensed)
              </p>
              <p className="text-xs text-secondary-500 dark:text-secondary-400 mt-1">
                Aspose.Words + Cells + Slides for production-grade Office conversion
              </p>
              {pdfEngine === "aspose" && (
                <Check className="h-4 w-4 text-primary-600 dark:text-primary-400 mt-2" />
              )}
            </button>
          </div>
        </div>

        {/* Gotenberg URL (for opensource engine) */}
        {pdfEngine === "opensource" && (
          <div>
            <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
              Gotenberg URL (optional — for Office format conversion)
            </label>
            <input
              type="text"
              value={gotenbergUrl}
              onChange={(e) => setGotenbergUrl(e.target.value)}
              placeholder="e.g. http://gotenberg:3000"
              className="form-input w-full"
            />
            <p className="text-xs text-secondary-400 mt-1">
              Leave empty if you don&apos;t need Office document conversion
            </p>
          </div>
        )}

        {/* Aspose License Keys (for aspose engine) */}
        {pdfEngine === "aspose" && (
          <div className="space-y-3">
            <label className="flex items-center gap-2 text-sm font-medium text-secondary-700 dark:text-secondary-300">
              <Key className="h-4 w-4" />
              Aspose License Keys
            </label>
            <div>
              <label className="block text-xs text-secondary-500 mb-1">
                Aspose.Words License
              </label>
              <input
                type="password"
                value={asposeWordsLicense}
                onChange={(e) => setAsposeWordsLicense(e.target.value)}
                placeholder={
                  settings?.aspose_words_license?.value
                    ? settings.aspose_words_license.value
                    : "Paste license key"
                }
                className="form-input w-full font-mono text-xs"
              />
            </div>
            <div>
              <label className="block text-xs text-secondary-500 mb-1">
                Aspose.Cells License
              </label>
              <input
                type="password"
                value={asposeCellsLicense}
                onChange={(e) => setAsposeCellsLicense(e.target.value)}
                placeholder={
                  settings?.aspose_cells_license?.value
                    ? settings.aspose_cells_license.value
                    : "Paste license key"
                }
                className="form-input w-full font-mono text-xs"
              />
            </div>
            <div>
              <label className="block text-xs text-secondary-500 mb-1">
                Aspose.Slides License
              </label>
              <input
                type="password"
                value={asposeSlidesLicense}
                onChange={(e) => setAsposeSlidesLicense(e.target.value)}
                placeholder={
                  settings?.aspose_slides_license?.value
                    ? settings.aspose_slides_license.value
                    : "Paste license key"
                }
                className="form-input w-full font-mono text-xs"
              />
            </div>
            <p className="text-xs text-secondary-400">
              Without valid licenses, Aspose runs in evaluation mode (watermarked output).
              Images and text/CSV always use the free open-source converters.
            </p>
          </div>
        )}

        {/* Malware Scanning Toggle */}
        <div className="flex items-center justify-between rounded-xl border border-secondary-200 dark:border-secondary-700 p-4">
          <div className="flex items-center gap-3">
            <ShieldCheck className="h-5 w-5 text-success-600 dark:text-success-400" />
            <div>
              <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
                Malware Scanning
              </p>
              <p className="text-xs text-secondary-500 dark:text-secondary-400">
                Two-phase upload: files staged for scanning before promotion to production storage
              </p>
            </div>
          </div>
          <button
            onClick={() => setMalwareScanning(!malwareScanning)}
            className={clsx(
              "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full transition-colors",
              malwareScanning
                ? "bg-success-600 dark:bg-success-500"
                : "bg-secondary-300 dark:bg-secondary-600",
            )}
          >
            <span
              className={clsx(
                "inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform mt-0.5",
                malwareScanning ? "translate-x-5 ml-0.5" : "translate-x-0.5",
              )}
            />
          </button>
        </div>

        {/* Save button */}
        <div className="flex items-center gap-3">
          <button
            onClick={handleSave}
            disabled={saving}
            className={clsx(
              "inline-flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-medium transition-colors",
              "bg-primary-600 text-white hover:bg-primary-700",
              "dark:bg-primary-500 dark:hover:bg-primary-600",
              "disabled:opacity-50",
            )}
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Save className="h-4 w-4" />
            )}
            {saving ? "Saving..." : "Save Settings"}
          </button>
          {success && (
            <span className="flex items-center gap-1.5 text-sm text-success-600 dark:text-success-400">
              <Check className="h-4 w-4" />
              Settings saved
            </span>
          )}
          {error && (
            <span className="text-sm text-danger-600 dark:text-danger-400">
              {error}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
