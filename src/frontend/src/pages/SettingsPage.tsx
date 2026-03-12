import { useAuth } from "../auth/useAuth";
import { useTheme } from "../contexts/ThemeContext";
import { usePermissions } from "../hooks/usePermissions";
import {
  Sun,
  Moon,
  Monitor,
  User,
  Mail,
  Shield,
  Info,
  Globe,
  Bell,
  Palette,
} from "lucide-react";
import { clsx } from "clsx";

export function SettingsPage() {
  const { user } = useAuth();
  const { theme, setTheme } = useTheme();
  const { roles } = usePermissions();

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";
  const environment = import.meta.env.MODE ?? "development";

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h2 className="page-header mb-1">Settings</h2>
        <p className="page-subtitle">
          Manage your preferences and application settings
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Theme section */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-500/10">
              <Palette className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                Appearance
              </h3>
              <p className="text-xs text-secondary-500 dark:text-secondary-400">
                Customize the look and feel
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-3">
            <ThemeOption
              label="Light"
              icon={<Sun className="h-5 w-5" />}
              active={theme === "light"}
              onClick={() => setTheme("light")}
              preview="bg-white border-secondary-200"
            />
            <ThemeOption
              label="Dark"
              icon={<Moon className="h-5 w-5" />}
              active={theme === "dark"}
              onClick={() => setTheme("dark")}
              preview="bg-secondary-800 border-secondary-700"
            />
            <ThemeOption
              label="System"
              icon={<Monitor className="h-5 w-5" />}
              active={false}
              onClick={() => {
                localStorage.removeItem("assurancenet-theme");
                const prefersDark = window.matchMedia(
                  "(prefers-color-scheme: dark)",
                ).matches;
                setTheme(prefersDark ? "dark" : "light");
              }}
              preview="bg-gradient-to-r from-white to-secondary-800 border-secondary-300"
            />
          </div>
        </div>

        {/* User profile section */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-500/10">
              <User className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                User Profile
              </h3>
              <p className="text-xs text-secondary-500 dark:text-secondary-400">
                Your account information (read-only)
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <ProfileItem
              icon={<User className="h-4 w-4" />}
              label="Full Name"
              value={user?.name ?? "Not available"}
            />
            <ProfileItem
              icon={<Mail className="h-4 w-4" />}
              label="Email"
              value={user?.email ?? "Not available"}
            />
            <ProfileItem
              icon={<Shield className="h-4 w-4" />}
              label="Account ID"
              value={user?.id ?? "Not available"}
              mono
            />
            {roles.length > 0 && (
              <div className="flex items-start gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800">
                  <span className="text-secondary-500">
                    <Shield className="h-4 w-4" />
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-xs font-medium text-secondary-500 dark:text-secondary-400">
                    Roles
                  </p>
                  <div className="mt-1 flex flex-wrap gap-1.5">
                    {roles.map((role) => (
                      <span
                        key={role}
                        className={clsx(
                          "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize",
                          "bg-primary-100 text-primary-700",
                          "dark:bg-primary-500/20 dark:text-primary-300",
                        )}
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Notification preferences */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-500/10">
              <Bell className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                Notifications
              </h3>
              <p className="text-xs text-secondary-500 dark:text-secondary-400">
                Manage how you receive updates
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <ToggleItem
              label="Document upload complete"
              description="Get notified when document processing finishes"
              defaultOn
            />
            <ToggleItem
              label="Investigation updates"
              description="Notifications for status changes"
              defaultOn
            />
            <ToggleItem
              label="PDF conversion failures"
              description="Alert when a conversion fails"
              defaultOn
            />
            <ToggleItem
              label="Weekly summary"
              description="Receive a weekly activity digest"
              defaultOn={false}
            />
          </div>
        </div>

        {/* Application info */}
        <div className="card">
          <div className="flex items-center gap-3 mb-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 dark:bg-primary-500/10">
              <Info className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-secondary-900 dark:text-secondary-100">
                Application Info
              </h3>
              <p className="text-xs text-secondary-500 dark:text-secondary-400">
                System information and configuration
              </p>
            </div>
          </div>

          <div className="space-y-4">
            <ProfileItem
              icon={<Shield className="h-4 w-4" />}
              label="Application"
              value="AssuranceNet Document Management"
            />
            <ProfileItem
              icon={<Info className="h-4 w-4" />}
              label="Version"
              value="v0.1.0"
            />
            <ProfileItem
              icon={<Globe className="h-4 w-4" />}
              label="Environment"
              value={environment}
            />
            <ProfileItem
              icon={<Globe className="h-4 w-4" />}
              label="API URL"
              value={apiBaseUrl}
              mono
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ThemeOption({
  label,
  icon,
  active,
  onClick,
  preview,
}: {
  label: string;
  icon: React.ReactNode;
  active: boolean;
  onClick: () => void;
  preview: string;
}) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        "flex flex-col items-center gap-2 rounded-xl border-2 p-4 transition-all",
        active
          ? "border-primary-500 bg-primary-50/50 dark:bg-primary-500/5"
          : clsx(
              "border-secondary-200 hover:border-secondary-300",
              "dark:border-secondary-700 dark:hover:border-secondary-600",
            ),
      )}
    >
      <div
        className={clsx(
          "h-12 w-full rounded-lg border",
          preview,
        )}
      />
      <div className="flex items-center gap-1.5">
        <span
          className={clsx(
            active
              ? "text-primary-600 dark:text-primary-400"
              : "text-secondary-400 dark:text-secondary-500",
          )}
        >
          {icon}
        </span>
        <span
          className={clsx(
            "text-sm font-medium",
            active
              ? "text-primary-700 dark:text-primary-300"
              : "text-secondary-600 dark:text-secondary-400",
          )}
        >
          {label}
        </span>
      </div>
    </button>
  );
}

function ProfileItem({
  icon,
  label,
  value,
  mono = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary-100 dark:bg-secondary-800">
        <span className="text-secondary-500">{icon}</span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xs font-medium text-secondary-500 dark:text-secondary-400">
          {label}
        </p>
        <p
          className={clsx(
            "mt-0.5 text-sm text-secondary-900 dark:text-secondary-100 truncate",
            mono && "font-mono text-xs",
          )}
        >
          {value}
        </p>
      </div>
    </div>
  );
}

function ToggleItem({
  label,
  description,
  defaultOn = true,
}: {
  label: string;
  description: string;
  defaultOn?: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="text-sm font-medium text-secondary-900 dark:text-secondary-100">
          {label}
        </p>
        <p className="text-xs text-secondary-500 dark:text-secondary-400">
          {description}
        </p>
      </div>
      <button
        className={clsx(
          "relative inline-flex h-6 w-11 shrink-0 rounded-full transition-colors duration-200 ease-in-out",
          "focus:outline-none focus:ring-2 focus:ring-primary-500/30 focus:ring-offset-2 dark:focus:ring-offset-secondary-900",
          defaultOn
            ? "bg-primary-600 dark:bg-primary-500"
            : "bg-secondary-300 dark:bg-secondary-600",
        )}
      >
        <span
          className={clsx(
            "pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow-sm transform transition-transform duration-200 ease-in-out",
            defaultOn ? "translate-x-5" : "translate-x-0.5",
            "mt-0.5",
          )}
        />
      </button>
    </div>
  );
}
