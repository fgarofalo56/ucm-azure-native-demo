import { lazy, Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
} from "@azure/msal-react";
import { AppShell } from "./components/layout/AppShell";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { useAuth } from "./auth/useAuth";
import { Shield, Loader2 } from "lucide-react";
import { clsx } from "clsx";

// Lazy-loaded pages for code splitting
const DashboardPage = lazy(() =>
  import("./pages/DashboardPage").then((m) => ({ default: m.DashboardPage })),
);
const InvestigationsListPage = lazy(() =>
  import("./pages/InvestigationsListPage").then((m) => ({
    default: m.InvestigationsListPage,
  })),
);
const InvestigationPage = lazy(() =>
  import("./pages/InvestigationPage").then((m) => ({
    default: m.InvestigationPage,
  })),
);
const DocumentsPage = lazy(() =>
  import("./pages/DocumentsPage").then((m) => ({ default: m.DocumentsPage })),
);
const AuditLogPage = lazy(() =>
  import("./pages/AuditLogPage").then((m) => ({ default: m.AuditLogPage })),
);
const SettingsPage = lazy(() =>
  import("./pages/SettingsPage").then((m) => ({ default: m.SettingsPage })),
);
const SearchPage = lazy(() =>
  import("./pages/SearchPage").then((m) => ({ default: m.SearchPage })),
);
const FileExplorerPage = lazy(() =>
  import("./pages/FileExplorerPage").then((m) => ({
    default: m.FileExplorerPage,
  })),
);
const AdminPage = lazy(() =>
  import("./pages/AdminPage").then((m) => ({ default: m.AdminPage })),
);
const HelpPage = lazy(() =>
  import("./pages/HelpPage").then((m) => ({ default: m.HelpPage })),
);

function PageSpinner() {
  return (
    <div className="flex items-center justify-center py-24">
      <Loader2 className="h-8 w-8 text-primary-500 animate-spin" />
    </div>
  );
}

export function App() {
  const { login, loginError } = useAuth();

  return (
    <>
      <AuthenticatedTemplate>
        <AppShell>
          <ErrorBoundary>
            <Suspense fallback={<PageSpinner />}>
              <Routes>
                <Route path="/" element={<DashboardPage />} />
                <Route
                  path="/investigations"
                  element={<InvestigationsListPage />}
                />
                <Route
                  path="/investigations/:id"
                  element={<InvestigationPage />}
                />
                <Route path="/documents" element={<DocumentsPage />} />
                <Route path="/audit" element={<AuditLogPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/search" element={<SearchPage />} />
                <Route path="/explorer" element={<FileExplorerPage />} />
                <Route path="/admin" element={<AdminPage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </ErrorBoundary>
        </AppShell>
      </AuthenticatedTemplate>

      <UnauthenticatedTemplate>
        <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-secondary-50 via-primary-50/30 to-secondary-100 dark:from-secondary-950 dark:via-primary-950/20 dark:to-secondary-900">
          {/* Subtle grid pattern */}
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSAwIDEwIEwgNDAgMTAgTSAxMCAwIEwgMTAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzk0YTNiOCIgc3Ryb2tlLW9wYWNpdHk9IjAuMDUiIHN0cm9rZS13aWR0aD0iMSIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-60" />

          <div className="relative z-10 w-full max-w-md px-6">
            <div className="text-center mb-8">
              {/* Logo */}
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 shadow-lg shadow-primary-500/20">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h1 className="mt-6 text-3xl font-bold text-secondary-900 dark:text-secondary-50">
                AssuranceNet
              </h1>
              <p className="mt-2 text-secondary-500 dark:text-secondary-400">
                FSIS Document Management System
              </p>
            </div>

            {/* Sign in card */}
            <div
              className={clsx(
                "rounded-2xl p-8",
                "bg-white/80 backdrop-blur-sm shadow-xl",
                "dark:bg-secondary-900/80 dark:ring-1 dark:ring-secondary-700",
                "border border-secondary-200/50 dark:border-secondary-700/50",
              )}
            >
              <div className="text-center space-y-5">
                <div>
                  <h2 className="text-lg font-semibold text-secondary-900 dark:text-secondary-50">
                    Sign in to your account
                  </h2>
                  <p className="mt-1 text-sm text-secondary-500 dark:text-secondary-400">
                    Use your organizational credentials to access the system.
                  </p>
                </div>

                <button
                  onClick={login}
                  className={clsx(
                    "group relative flex w-full items-center justify-center gap-3 rounded-xl px-6 py-3.5",
                    "bg-primary-600 font-medium text-white shadow-lg shadow-primary-500/20",
                    "hover:bg-primary-700 hover:shadow-primary-500/30",
                    "dark:bg-primary-500 dark:hover:bg-primary-600",
                    "focus:outline-none focus:ring-2 focus:ring-primary-500/40 focus:ring-offset-2",
                    "dark:focus:ring-offset-secondary-900",
                    "transition-all duration-200",
                  )}
                >
                  {/* Microsoft logo */}
                  <svg
                    className="h-5 w-5"
                    viewBox="0 0 23 23"
                    fill="none"
                  >
                    <path d="M0 0h11v11H0z" fill="#f35325" />
                    <path d="M12 0h11v11H12z" fill="#81bc06" />
                    <path d="M0 12h11v11H0z" fill="#05a6f0" />
                    <path d="M12 12h11v11H12z" fill="#ffba08" />
                  </svg>
                  Sign in with Microsoft
                </button>

                {loginError && (
                  <div
                    className={clsx(
                      "flex items-start gap-2 rounded-lg px-4 py-3 text-left",
                      "bg-danger-50 text-danger-700 border border-danger-200",
                      "dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
                    )}
                  >
                    <span className="text-sm">{loginError}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Footer */}
            <p className="mt-6 text-center text-xs text-secondary-400 dark:text-secondary-600">
              United States Department of Agriculture &middot; Food Safety and
              Inspection Service
            </p>
          </div>
        </div>
      </UnauthenticatedTemplate>
    </>
  );
}
