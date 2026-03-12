import { clsx } from "clsx";
import type { ReactNode } from "react";

type BadgeVariant =
  | "success"
  | "warning"
  | "error"
  | "info"
  | "neutral"
  | "primary"
  | "processing";

interface StatusBadgeProps {
  variant: BadgeVariant;
  label: string;
  icon?: ReactNode;
  dot?: boolean;
  size?: "sm" | "md";
}

const variantStyles: Record<BadgeVariant, string> = {
  success: clsx(
    "bg-success-50 text-success-700 ring-success-600/20",
    "dark:bg-success-500/10 dark:text-success-400 dark:ring-success-400/20",
  ),
  warning: clsx(
    "bg-warning-50 text-warning-700 ring-warning-600/20",
    "dark:bg-warning-500/10 dark:text-warning-400 dark:ring-warning-400/20",
  ),
  error: clsx(
    "bg-danger-50 text-danger-700 ring-danger-600/20",
    "dark:bg-danger-500/10 dark:text-danger-400 dark:ring-danger-400/20",
  ),
  info: clsx(
    "bg-primary-50 text-primary-700 ring-primary-600/20",
    "dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-400/20",
  ),
  neutral: clsx(
    "bg-secondary-100 text-secondary-600 ring-secondary-500/20",
    "dark:bg-secondary-500/10 dark:text-secondary-400 dark:ring-secondary-400/20",
  ),
  primary: clsx(
    "bg-primary-50 text-primary-700 ring-primary-600/20",
    "dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-400/20",
  ),
  processing: clsx(
    "bg-primary-50 text-primary-700 ring-primary-600/20",
    "dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-400/20",
  ),
};

const dotColors: Record<BadgeVariant, string> = {
  success: "bg-success-500",
  warning: "bg-warning-500",
  error: "bg-danger-500",
  info: "bg-primary-500",
  neutral: "bg-secondary-400",
  primary: "bg-primary-500",
  processing: "bg-primary-500 animate-pulse",
};

export default function StatusBadge({
  variant,
  label,
  icon,
  dot = false,
  size = "sm",
}: StatusBadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full font-medium ring-1 ring-inset",
        variantStyles[variant],
        size === "sm" ? "px-2 py-0.5 text-xs gap-1" : "px-2.5 py-1 text-xs gap-1.5",
      )}
    >
      {dot && (
        <span
          className={clsx("h-1.5 w-1.5 rounded-full", dotColors[variant])}
        />
      )}
      {icon && <span className="shrink-0 -ml-0.5">{icon}</span>}
      {label}
    </span>
  );
}
