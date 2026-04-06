import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ErrorBoundary } from "@/components/ErrorBoundary";

// A component that conditionally throws
function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) {
    throw new Error("Test error message");
  }
  return <div>Content rendered successfully</div>;
}

describe("ErrorBoundary", () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    // Suppress console.error for error boundary tests —
    // React logs caught errors to console.error which clutters output.
    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it("renders children when no error occurs", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Content rendered successfully")).toBeInTheDocument();
  });

  it("renders fallback UI when a child throws", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("shows the error message in an expandable details section", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    // The <summary> text
    expect(screen.getByText("Error details")).toBeInTheDocument();
    // The error message inside <pre>
    expect(screen.getByText("Test error message")).toBeInTheDocument();
  });

  it("renders a custom fallback when the fallback prop is provided", () => {
    render(
      <ErrorBoundary fallback={<div>Custom error page</div>}>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Custom error page")).toBeInTheDocument();
    // The default UI should not appear
    expect(screen.queryByText("Something went wrong")).not.toBeInTheDocument();
  });

  it("displays a 'Try again' button in the default fallback", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(screen.getByText("Try again")).toBeInTheDocument();
  });

  it("resets the error state when 'Try again' is clicked", () => {
    // We need a component whose throw behaviour can change between renders.
    // After reset the ErrorBoundary re-renders children, so if the child
    // no longer throws, we should see the normal content.
    let shouldThrow = true;

    function ToggleThrow() {
      if (shouldThrow) {
        throw new Error("Boom");
      }
      return <div>Recovered successfully</div>;
    }

    render(
      <ErrorBoundary>
        <ToggleThrow />
      </ErrorBoundary>,
    );

    // Should be in error state
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();

    // Stop throwing before clicking retry
    shouldThrow = false;

    fireEvent.click(screen.getByText("Try again"));

    // After reset, the child renders normally
    expect(screen.getByText("Recovered successfully")).toBeInTheDocument();
    expect(screen.queryByText("Something went wrong")).not.toBeInTheDocument();
  });

  it("shows a description paragraph in the default fallback", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    expect(
      screen.getByText(/unexpected error occurred/i),
    ).toBeInTheDocument();
  });

  it("calls console.error when catching an error", () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>,
    );
    // React + our componentDidCatch both call console.error
    expect(consoleErrorSpy).toHaveBeenCalled();
  });
});
