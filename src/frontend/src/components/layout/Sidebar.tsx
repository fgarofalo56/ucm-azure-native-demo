import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderSearch,
  FileText,
  Shield,
  Settings,
  Search,
  FolderOpen,
  Users,
  HelpCircle,
  type LucideIcon,
} from "lucide-react";
import { clsx } from "clsx";
import { usePermissions } from "../../hooks/usePermissions";

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  badge?: number;
  end?: boolean;
  permission?: string;
  role?: string;
}

const navItems: NavItem[] = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/investigations", label: "Investigations", icon: FolderSearch },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/explorer", label: "File Explorer", icon: FolderOpen, permission: "documents.read" },
  { to: "/search", label: "Search", icon: Search },
  { to: "/audit", label: "Audit Log", icon: Shield, permission: "audit.read" },
  { to: "/admin", label: "Administration", icon: Users, permission: "users.read" },
  { to: "/help", label: "Help", icon: HelpCircle },
  { to: "/settings", label: "Settings", icon: Settings },
];

interface SidebarProps {
  open: boolean;
  collapsed: boolean;
  onClose: () => void;
  investigationCount?: number;
}

export function Sidebar({
  open,
  collapsed,
  onClose,
  investigationCount,
}: SidebarProps) {
  const { hasPermission, hasRole } = usePermissions();

  const visibleItems = navItems
    .filter((item) => {
      if (item.permission && !hasPermission(item.permission)) return false;
      if (item.role && !hasRole(item.role)) return false;
      return true;
    })
    .map((item) => ({
      ...item,
      badge: item.to === "/investigations" ? investigationCount : undefined,
    }));

  return (
    <>
      {/* Mobile overlay */}
      {open && (
        <div
          className="fixed inset-0 z-20 bg-secondary-900/50 dark:bg-black/60 backdrop-blur-sm md:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-30 flex flex-col border-r",
          "bg-white dark:bg-secondary-900",
          "border-secondary-200/60 dark:border-secondary-700/50",
          "transition-all duration-200 ease-in-out",
          "md:static md:z-auto",
          // Width
          collapsed ? "md:w-[72px]" : "md:w-64",
          // Mobile: always full width when open
          "w-64",
          // Mobile transform
          open ? "translate-x-0" : "-translate-x-full md:translate-x-0",
          // Top padding for mobile (below header)
          "pt-16 md:pt-0",
        )}
      >
        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {visibleItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              onClick={onClose}
              className={({ isActive }) =>
                clsx(
                  "group relative flex items-center rounded-lg transition-all duration-150",
                  collapsed ? "justify-center px-2 py-2.5" : "gap-3 px-3 py-2.5",
                  isActive
                    ? clsx(
                        "bg-primary-50 text-primary-700 font-medium",
                        "dark:bg-primary-500/10 dark:text-primary-300",
                      )
                    : clsx(
                        "text-secondary-600 hover:bg-secondary-100 hover:text-secondary-900",
                        "dark:text-secondary-400 dark:hover:bg-secondary-800 dark:hover:text-secondary-200",
                      ),
                )
              }
            >
              {({ isActive }) => (
                <>
                  {/* Active indicator */}
                  {isActive && (
                    <div
                      className={clsx(
                        "absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 rounded-r-full",
                        "bg-primary-600 dark:bg-primary-400",
                        collapsed ? "-left-3" : "-left-3",
                      )}
                    />
                  )}

                  <item.icon
                    className={clsx(
                      "shrink-0 h-5 w-5",
                      isActive
                        ? "text-primary-600 dark:text-primary-400"
                        : "text-secondary-400 group-hover:text-secondary-600 dark:text-secondary-500 dark:group-hover:text-secondary-300",
                    )}
                  />

                  {!collapsed && (
                    <>
                      <span className="text-sm">{item.label}</span>
                      {item.badge !== undefined && item.badge > 0 && (
                        <span
                          className={clsx(
                            "ml-auto inline-flex items-center justify-center",
                            "min-w-[20px] h-5 px-1.5 rounded-full text-xs font-semibold",
                            "bg-primary-100 text-primary-700",
                            "dark:bg-primary-500/20 dark:text-primary-300",
                          )}
                        >
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}

                  {/* Tooltip for collapsed mode */}
                  {collapsed && (
                    <div
                      className={clsx(
                        "absolute left-full ml-2 px-2.5 py-1.5 rounded-lg",
                        "bg-secondary-900 text-white text-xs font-medium whitespace-nowrap",
                        "dark:bg-secondary-700",
                        "opacity-0 invisible group-hover:opacity-100 group-hover:visible",
                        "transition-all duration-150 z-50",
                        "pointer-events-none",
                      )}
                    >
                      {item.label}
                      {item.badge !== undefined && item.badge > 0 && (
                        <span className="ml-1.5 text-primary-300">
                          ({item.badge})
                        </span>
                      )}
                    </div>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div
          className={clsx(
            "border-t px-3 py-3",
            "border-secondary-200/60 dark:border-secondary-700/50",
          )}
        >
          {collapsed ? (
            <p className="text-center text-[10px] font-medium text-secondary-400 dark:text-secondary-600">
              v0.1
            </p>
          ) : (
            <div className="flex items-center justify-between">
              <p className="text-xs text-secondary-400 dark:text-secondary-600">
                AssuranceNet
              </p>
              <p className="text-xs font-medium text-secondary-400 dark:text-secondary-600">
                v0.1.0
              </p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
