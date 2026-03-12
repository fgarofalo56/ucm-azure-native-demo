import { ReactNode, useState } from "react";
import { clsx } from "clsx";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { useInvestigations } from "../../hooks/useInvestigations";

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { data: investigationsData } = useInvestigations();

  const investigationCount = investigationsData?.meta.total ?? 0;

  return (
    <div className="flex min-h-screen flex-col bg-secondary-50 dark:bg-secondary-950">
      <Header
        onMenuToggle={() => setSidebarOpen((o) => !o)}
        onSidebarCollapse={() => setSidebarCollapsed((c) => !c)}
        sidebarCollapsed={sidebarCollapsed}
      />
      <div className="flex flex-1">
        <Sidebar
          open={sidebarOpen}
          collapsed={sidebarCollapsed}
          onClose={() => setSidebarOpen(false)}
          investigationCount={investigationCount}
        />
        <main
          className={clsx(
            "flex-1 overflow-auto",
            "p-4 md:p-6 lg:p-8",
          )}
        >
          <div className="mx-auto max-w-7xl">{children}</div>
        </main>
      </div>
    </div>
  );
}
