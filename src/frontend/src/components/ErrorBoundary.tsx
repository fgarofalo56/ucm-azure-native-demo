import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { clsx } from "clsx";

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({ hasError: false, error: null });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex min-h-[400px] items-center justify-center p-8">
          <div className="max-w-md text-center space-y-4">
            <div className={clsx(
              "mx-auto flex h-16 w-16 items-center justify-center rounded-2xl",
              "bg-danger-100 dark:bg-danger-500/10"
            )}>
              <AlertTriangle className="h-8 w-8 text-danger-500" />
            </div>
            <h2 className="text-xl font-semibold text-secondary-900 dark:text-secondary-50">
              Something went wrong
            </h2>
            <p className="text-sm text-secondary-500 dark:text-secondary-400">
              An unexpected error occurred. Please try again or contact support if the problem persists.
            </p>
            {this.state.error && (
              <details className="text-left">
                <summary className="cursor-pointer text-xs text-secondary-400 hover:text-secondary-600">
                  Error details
                </summary>
                <pre className={clsx(
                  "mt-2 overflow-auto rounded-lg p-3 text-xs",
                  "bg-secondary-100 text-secondary-700",
                  "dark:bg-secondary-800 dark:text-secondary-300"
                )}>
                  {this.state.error.message}
                </pre>
              </details>
            )}
            <button
              onClick={this.handleReset}
              className={clsx(
                "inline-flex items-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium",
                "bg-primary-600 text-white hover:bg-primary-700",
                "dark:bg-primary-500 dark:hover:bg-primary-600",
                "transition-colors"
              )}
            >
              <RefreshCw className="h-4 w-4" />
              Try again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
