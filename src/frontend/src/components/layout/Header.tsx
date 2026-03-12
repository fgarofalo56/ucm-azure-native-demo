import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  Menu,
  Sun,
  Moon,
  Bell,
  ChevronDown,
  LogOut,
  User,
  Shield,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
} from "lucide-react";
import { clsx } from "clsx";
import { useAuth } from "../../auth/useAuth";
import { useTheme } from "../../contexts/ThemeContext";
import { usePermissions } from "../../hooks/usePermissions";

interface HeaderProps {
  onMenuToggle: () => void;
  onSidebarCollapse?: () => void;
  sidebarCollapsed?: boolean;
}

export function Header({
  onMenuToggle,
  onSidebarCollapse,
  sidebarCollapsed,
}: HeaderProps) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { roles } = usePermissions();
  const navigate = useNavigate();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim().length >= 2) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery("");
    }
  };

  const initials = user?.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "U";

  const primaryRole = roles[0];

  return (
    <header
      className={clsx(
        "sticky top-0 z-40 h-16 border-b",
        "bg-white/80 backdrop-blur-md border-secondary-200/60",
        "dark:bg-secondary-900/80 dark:border-secondary-700/50",
      )}
    >
      <div className="flex h-full items-center justify-between px-4 md:px-6">
        {/* Left section */}
        <div className="flex items-center gap-3">
          {/* Mobile menu toggle */}
          <button
            onClick={onMenuToggle}
            className={clsx(
              "rounded-lg p-2 md:hidden",
              "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
              "dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-200",
            )}
            aria-label="Toggle menu"
          >
            <Menu className="h-5 w-5" />
          </button>

          {/* Desktop sidebar collapse toggle */}
          {onSidebarCollapse && (
            <button
              onClick={onSidebarCollapse}
              className={clsx(
                "hidden md:flex rounded-lg p-2",
                "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
                "dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-200",
              )}
              aria-label="Collapse sidebar"
            >
              {sidebarCollapsed ? (
                <PanelLeftOpen className="h-5 w-5" />
              ) : (
                <PanelLeftClose className="h-5 w-5" />
              )}
            </button>
          )}

          {/* Branding */}
          <div className="flex items-center gap-2.5">
            <div
              className={clsx(
                "flex h-9 w-9 items-center justify-center rounded-lg",
                "bg-gradient-to-br from-primary-500 to-primary-700",
                "shadow-sm shadow-primary-500/20",
              )}
            >
              <Shield className="h-5 w-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-base font-bold text-secondary-900 dark:text-secondary-50 leading-tight">
                AssuranceNet
              </h1>
              <p className="text-[11px] font-medium text-secondary-400 dark:text-secondary-500 leading-tight">
                FSIS Document Management
              </p>
            </div>
          </div>
        </div>

        {/* Center - Search bar */}
        <form
          onSubmit={handleSearchSubmit}
          className="hidden md:flex flex-1 max-w-md mx-8"
        >
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search investigations, documents..."
              className={clsx(
                "w-full rounded-lg border py-2 pl-9 pr-3 text-sm",
                "bg-secondary-50 border-secondary-200 placeholder-secondary-400",
                "focus:bg-white focus:border-primary-400 focus:ring-1 focus:ring-primary-400/30 focus:outline-none",
                "dark:bg-secondary-800 dark:border-secondary-700 dark:text-secondary-100",
                "dark:placeholder-secondary-500 dark:focus:bg-secondary-800 dark:focus:border-primary-500",
              )}
            />
          </div>
        </form>

        {/* Right section */}
        <div className="flex items-center gap-1.5">
          {/* Theme toggle */}
          <button
            onClick={toggleTheme}
            className={clsx(
              "rounded-lg p-2",
              "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
              "dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-200",
            )}
            aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
          >
            {theme === "light" ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </button>

          {/* Notifications */}
          <button
            className={clsx(
              "relative rounded-lg p-2",
              "text-secondary-500 hover:bg-secondary-100 hover:text-secondary-700",
              "dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-200",
            )}
            aria-label="Notifications"
          >
            <Bell className="h-5 w-5" />
            <span
              className={clsx(
                "absolute top-1.5 right-1.5 h-2 w-2 rounded-full",
                "bg-danger-500 ring-2 ring-white dark:ring-secondary-900",
              )}
            />
          </button>

          {/* Divider */}
          <div className="mx-2 h-6 w-px bg-secondary-200 dark:bg-secondary-700" />

          {/* User dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className={clsx(
                "flex items-center gap-2.5 rounded-lg py-1.5 pl-1.5 pr-2",
                "hover:bg-secondary-100",
                "dark:hover:bg-secondary-800",
              )}
            >
              <div
                className={clsx(
                  "flex h-8 w-8 items-center justify-center rounded-lg",
                  "bg-primary-100 text-primary-700 font-semibold text-sm",
                  "dark:bg-primary-500/20 dark:text-primary-300",
                )}
              >
                {initials}
              </div>
              <div className="hidden md:block text-left">
                <span className="block text-sm font-medium text-secondary-700 dark:text-secondary-200 leading-tight">
                  {user?.name ?? "User"}
                </span>
                {primaryRole && (
                  <span className="block text-[10px] font-medium text-primary-600 dark:text-primary-400 leading-tight capitalize">
                    {primaryRole}
                  </span>
                )}
              </div>
              <ChevronDown
                className={clsx(
                  "hidden h-4 w-4 text-secondary-400 transition-transform md:block",
                  dropdownOpen && "rotate-180",
                )}
              />
            </button>

            {dropdownOpen && (
              <div
                className={clsx(
                  "absolute right-0 top-full mt-1.5 w-64",
                  "rounded-xl border bg-white shadow-lg",
                  "dark:bg-secondary-900 dark:border-secondary-700",
                  "border-secondary-200",
                )}
              >
                {/* User info */}
                <div className="border-b border-secondary-100 dark:border-secondary-800 px-4 py-3">
                  <p className="text-sm font-medium text-secondary-900 dark:text-secondary-50">
                    {user?.name}
                  </p>
                  <p className="text-xs text-secondary-500 dark:text-secondary-400 truncate">
                    {user?.email}
                  </p>
                  {roles.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {roles.map((role) => (
                        <span
                          key={role}
                          className={clsx(
                            "inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium capitalize",
                            "bg-primary-100 text-primary-700",
                            "dark:bg-primary-500/20 dark:text-primary-300",
                          )}
                        >
                          {role}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="py-1.5">
                  <button
                    onClick={() => setDropdownOpen(false)}
                    className={clsx(
                      "flex w-full items-center gap-3 px-4 py-2.5 text-sm",
                      "text-secondary-700 hover:bg-secondary-50",
                      "dark:text-secondary-300 dark:hover:bg-secondary-800",
                    )}
                  >
                    <User className="h-4 w-4 text-secondary-400" />
                    Profile
                  </button>

                  <button
                    onClick={() => {
                      setDropdownOpen(false);
                      logout();
                    }}
                    className={clsx(
                      "flex w-full items-center gap-3 px-4 py-2.5 text-sm",
                      "text-danger-600 hover:bg-danger-50",
                      "dark:text-danger-400 dark:hover:bg-danger-500/10",
                    )}
                  >
                    <LogOut className="h-4 w-4" />
                    Sign out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
