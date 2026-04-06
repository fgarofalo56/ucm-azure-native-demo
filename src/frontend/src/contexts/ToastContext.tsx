import { createContext, useCallback, useContext, useState, type ReactNode } from "react";
import { CheckCircle2, AlertCircle, Info, X } from "lucide-react";
import { clsx } from "clsx";

type ToastType = "success" | "error" | "info";

interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

interface ToastContextType {
  addToast: (type: ToastType, message: string) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function useToast(): ToastContextType {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}

const icons: Record<ToastType, typeof CheckCircle2> = {
  success: CheckCircle2,
  error: AlertCircle,
  info: Info,
};

const styles: Record<ToastType, string> = {
  success: "bg-success-50 text-success-700 border-success-200 dark:bg-success-500/10 dark:text-success-400 dark:border-success-500/20",
  error: "bg-danger-50 text-danger-700 border-danger-200 dark:bg-danger-500/10 dark:text-danger-400 dark:border-danger-500/20",
  info: "bg-primary-50 text-primary-700 border-primary-200 dark:bg-primary-500/10 dark:text-primary-400 dark:border-primary-500/20",
};

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((type: ToastType, message: string) => {
    const id = crypto.randomUUID();
    setToasts((prev) => [...prev, { id, type, message }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 5000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ addToast, removeToast }}>
      {children}

      {/* Toast container */}
      {toasts.length > 0 && (
        <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 max-w-sm">
          {toasts.map((toast) => {
            const Icon = icons[toast.type];
            return (
              <div
                key={toast.id}
                className={clsx(
                  "flex items-center gap-3 rounded-lg border px-4 py-3 shadow-lg",
                  "animate-in slide-in-from-right",
                  styles[toast.type]
                )}
                role="alert"
              >
                <Icon className="h-5 w-5 shrink-0" />
                <p className="flex-1 text-sm">{toast.message}</p>
                <button
                  onClick={() => removeToast(toast.id)}
                  className="shrink-0 rounded p-0.5 hover:bg-black/5 dark:hover:bg-white/5"
                  aria-label="Dismiss"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </ToastContext.Provider>
  );
}
