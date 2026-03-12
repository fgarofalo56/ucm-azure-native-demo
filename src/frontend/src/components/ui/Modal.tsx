import { type ReactNode, useEffect, useRef } from "react";
import { X } from "lucide-react";
import { clsx } from "clsx";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  size?: "sm" | "md" | "lg" | "xl";
  footer?: ReactNode;
}

const sizeStyles = {
  sm: "max-w-md",
  md: "max-w-lg",
  lg: "max-w-2xl",
  xl: "max-w-4xl",
};

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = "md",
  footer,
}: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={overlayRef}
      className={clsx(
        "fixed inset-0 z-50 flex items-center justify-center p-4",
        "bg-secondary-900/60 dark:bg-black/70",
        "backdrop-blur-sm",
        "animate-in fade-in",
      )}
      onClick={(e) => {
        if (e.target === overlayRef.current) onClose();
      }}
    >
      <div
        className={clsx(
          "bg-white rounded-xl shadow-xl w-full",
          "dark:bg-secondary-900 dark:ring-1 dark:ring-secondary-700",
          sizeStyles[size],
          "animate-in zoom-in-95",
        )}
      >
        {/* Header */}
        <div
          className={clsx(
            "flex items-center justify-between px-6 py-4",
            "border-b border-secondary-200 dark:border-secondary-700",
          )}
        >
          <h2 className="text-lg font-semibold text-secondary-900 dark:text-secondary-50">
            {title}
          </h2>
          <button
            onClick={onClose}
            className={clsx(
              "rounded-lg p-1.5 transition-colors",
              "text-secondary-400 hover:text-secondary-600 hover:bg-secondary-100",
              "dark:text-secondary-500 dark:hover:text-secondary-300 dark:hover:bg-secondary-800",
            )}
            aria-label="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5">{children}</div>

        {/* Footer */}
        {footer && (
          <div
            className={clsx(
              "flex items-center justify-end gap-3 px-6 py-4",
              "border-t border-secondary-200 dark:border-secondary-700",
              "bg-secondary-50/50 dark:bg-secondary-800/30 rounded-b-xl",
            )}
          >
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
