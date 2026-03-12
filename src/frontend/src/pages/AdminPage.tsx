import { useState } from "react";
import {
  Shield,
  Loader2,
  Check,
  X,
} from "lucide-react";
import { clsx } from "clsx";
import { useUsers, useRoles, useAssignRoles } from "../hooks/useAdmin";
import { formatDistanceToNow } from "date-fns";
import type { AppUser } from "../api/types";

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
