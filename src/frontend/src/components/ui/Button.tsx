import { type ButtonHTMLAttributes, type ReactNode, forwardRef } from "react";
import { clsx } from "clsx";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost" | "success";
type ButtonSize = "xs" | "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  icon?: ReactNode;
  iconPosition?: "left" | "right";
}

const variantStyles: Record<ButtonVariant, string> = {
  primary: clsx(
    "bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500/40",
    "dark:bg-primary-500 dark:hover:bg-primary-600 dark:focus:ring-primary-400/40",
    "shadow-sm",
  ),
  secondary: clsx(
    "bg-white text-secondary-700 border border-secondary-300 hover:bg-secondary-50 focus:ring-secondary-500/30",
    "dark:bg-secondary-800 dark:text-secondary-200 dark:border-secondary-600 dark:hover:bg-secondary-700",
    "shadow-sm",
  ),
  danger: clsx(
    "bg-danger-600 text-white hover:bg-danger-700 focus:ring-danger-500/40",
    "dark:bg-danger-500 dark:hover:bg-danger-600",
    "shadow-sm",
  ),
  ghost: clsx(
    "bg-transparent text-secondary-600 hover:bg-secondary-100 focus:ring-secondary-500/30",
    "dark:text-secondary-300 dark:hover:bg-secondary-800",
  ),
  success: clsx(
    "bg-success-600 text-white hover:bg-success-700 focus:ring-success-500/40",
    "dark:bg-success-500 dark:hover:bg-success-600",
    "shadow-sm",
  ),
};

const sizeStyles: Record<ButtonSize, string> = {
  xs: "px-2.5 py-1.5 text-xs gap-1.5",
  sm: "px-3 py-1.5 text-sm gap-1.5",
  md: "px-4 py-2 text-sm gap-2",
  lg: "px-6 py-3 text-base gap-2",
};

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      loading = false,
      icon,
      iconPosition = "left",
      disabled,
      className = "",
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={clsx(
          "inline-flex items-center justify-center rounded-lg font-medium",
          "transition-all duration-150 ease-in-out",
          "focus:outline-none focus:ring-2 focus:ring-offset-2",
          "dark:focus:ring-offset-secondary-900",
          "disabled:opacity-50 disabled:pointer-events-none",
          variantStyles[variant],
          sizeStyles[size],
          className,
        )}
        {...props}
      >
        {loading && (
          <svg
            className="animate-spin h-4 w-4 shrink-0"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {!loading && icon && iconPosition === "left" && (
          <span className="shrink-0">{icon}</span>
        )}
        {children}
        {!loading && icon && iconPosition === "right" && (
          <span className="shrink-0">{icon}</span>
        )}
      </button>
    );
  },
);

Button.displayName = "Button";
export default Button;
