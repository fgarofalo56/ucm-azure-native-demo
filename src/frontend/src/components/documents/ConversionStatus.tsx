import {
  CheckCircle2,
  Clock,
  Loader2,
  AlertCircle,
  FileText,
} from "lucide-react";
import { clsx } from "clsx";
import type { ReactNode } from "react";

interface ConversionStatusProps {
  status: string;
}

const statusConfig: Record<
  string,
  { label: string; icon: ReactNode; className: string; dotClass: string }
> = {
  pending: {
    label: "Pending",
    icon: <Clock className="h-3.5 w-3.5" />,
    className: clsx(
      "bg-warning-50 text-warning-700 ring-warning-600/20",
      "dark:bg-warning-500/10 dark:text-warning-400 dark:ring-warning-400/20",
    ),
    dotClass: "bg-warning-500",
  },
  processing: {
    label: "Converting",
    icon: <Loader2 className="h-3.5 w-3.5 animate-spin" />,
    className: clsx(
      "bg-primary-50 text-primary-700 ring-primary-600/20",
      "dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-400/20",
    ),
    dotClass: "bg-primary-500 animate-pulse",
  },
  completed: {
    label: "Ready",
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
    className: clsx(
      "bg-success-50 text-success-700 ring-success-600/20",
      "dark:bg-success-500/10 dark:text-success-400 dark:ring-success-400/20",
    ),
    dotClass: "bg-success-500",
  },
  failed: {
    label: "Failed",
    icon: <AlertCircle className="h-3.5 w-3.5" />,
    className: clsx(
      "bg-danger-50 text-danger-700 ring-danger-600/20",
      "dark:bg-danger-500/10 dark:text-danger-400 dark:ring-danger-400/20",
    ),
    dotClass: "bg-danger-500",
  },
  not_required: {
    label: "PDF",
    icon: <FileText className="h-3.5 w-3.5" />,
    className: clsx(
      "bg-secondary-100 text-secondary-600 ring-secondary-500/20",
      "dark:bg-secondary-500/10 dark:text-secondary-400 dark:ring-secondary-400/20",
    ),
    dotClass: "bg-secondary-400",
  },
};

export function ConversionStatus({ status }: ConversionStatusProps) {
  const config = statusConfig[status] ?? {
    label: status,
    icon: null,
    className: "bg-secondary-100 text-secondary-600 dark:bg-secondary-800 dark:text-secondary-400",
    dotClass: "bg-secondary-400",
  };

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset",
        config.className,
      )}
    >
      {config.icon}
      {config.label}
    </span>
  );
}
