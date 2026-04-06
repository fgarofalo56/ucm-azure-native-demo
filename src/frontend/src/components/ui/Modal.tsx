import { type ReactNode, useEffect, useRef, useCallback } from "react";
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
  const panelRef = useRef<HTMLDivElement>(null);
  const hasAutoFocused = useRef(false);

  // Focus trap: keep Tab cycling within the modal
  const handleFocusTrap = useCallback((e: KeyboardEvent) => {
    if (e.key !== "Tab") return;
    const panel = panelRef.current;
    if (!panel) return;

    const focusableElements = panel.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    if (focusableElements.length === 0) return;

    const firstEl = focusableElements[0];
    const lastEl = focusableElements[focusableElements.length - 1];

    if (e.shiftKey) {
      if (document.activeElement === firstEl) {
        e.preventDefault();
        lastEl.focus();
      }
    } else {
      if (document.activeElement === lastEl) {
        e.preventDefault();
        firstEl.focus();
      }
    }
  }, []);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) {
      document.addEventListener("keydown", handleEscape);
      document.addEventListener("keydown", handleFocusTrap);
      document.body.style.overflow = "hidden";

      // Focus the first focusable element only on initial open
      if (!hasAutoFocused.current) {
        hasAutoFocused.current = true;
        requestAnimationFrame(() => {
          const panel = panelRef.current;
          if (!panel) return;
          const firstFocusable = panel.querySelector<HTMLElement>(
            'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
          );
          firstFocusable?.focus();
        });
      }
    } else {
      hasAutoFocused.current = false;
    }
    return () => {
      document.removeEventListener("keydown", handleEscape);
      document.removeEventListener("keydown", handleFocusTrap);
      document.body.style.overflow = "";
    };
  }, [isOpen, onClose, handleFocusTrap]);

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
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
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
          <h2 id="modal-title" className="text-lg font-semibold text-secondary-900 dark:text-secondary-50">
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
