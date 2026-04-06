import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { ToastProvider, useToast } from "@/contexts/ToastContext";

// Mock crypto.randomUUID — jsdom may not provide it
beforeEach(() => {
  let counter = 0;
  if (!globalThis.crypto?.randomUUID) {
    Object.defineProperty(globalThis, "crypto", {
      value: {
        ...globalThis.crypto,
        randomUUID: () => `test-uuid-${++counter}`,
      },
      writable: true,
      configurable: true,
    });
  } else {
    vi.spyOn(crypto, "randomUUID").mockImplementation(
      () => `test-uuid-${++counter}` as ReturnType<typeof crypto.randomUUID>,
    );
  }
});

// Component that exposes toast actions for testing
function ToastTrigger() {
  const { addToast } = useToast();
  return (
    <div>
      <button onClick={() => addToast("success", "Success message")}>
        Show Success
      </button>
      <button onClick={() => addToast("error", "Error message")}>
        Show Error
      </button>
      <button onClick={() => addToast("info", "Info message")}>
        Show Info
      </button>
    </div>
  );
}

describe("ToastContext", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("renders children without any toasts initially", () => {
    render(
      <ToastProvider>
        <div>Child content</div>
      </ToastProvider>,
    );
    expect(screen.getByText("Child content")).toBeInTheDocument();
  });

  it("shows a success toast when triggered", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByText("Success message")).toBeInTheDocument();
  });

  it("shows an error toast when triggered", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Error"));
    expect(screen.getByText("Error message")).toBeInTheDocument();
  });

  it("shows an info toast when triggered", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Info"));
    expect(screen.getByText("Info message")).toBeInTheDocument();
  });

  it("renders each toast with role='alert' for accessibility", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });

  it("renders a dismiss button with aria-label='Dismiss'", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByLabelText("Dismiss")).toBeInTheDocument();
  });

  it("removes the toast when the dismiss button is clicked", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByText("Success message")).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText("Dismiss"));
    expect(screen.queryByText("Success message")).not.toBeInTheDocument();
  });

  it("auto-removes toast after 5 seconds", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    expect(screen.getByText("Success message")).toBeInTheDocument();

    // Advance past the 5-second auto-dismiss
    act(() => {
      vi.advanceTimersByTime(5000);
    });

    expect(screen.queryByText("Success message")).not.toBeInTheDocument();
  });

  it("can show multiple toasts simultaneously", () => {
    render(
      <ToastProvider>
        <ToastTrigger />
      </ToastProvider>,
    );
    fireEvent.click(screen.getByText("Show Success"));
    fireEvent.click(screen.getByText("Show Error"));

    expect(screen.getByText("Success message")).toBeInTheDocument();
    expect(screen.getByText("Error message")).toBeInTheDocument();
    expect(screen.getAllByRole("alert")).toHaveLength(2);
  });

  it("throws when useToast is used outside a ToastProvider", () => {
    // Suppress React error output for this expected failure
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});

    function BrokenComponent() {
      useToast();
      return null;
    }

    expect(() => render(<BrokenComponent />)).toThrow(
      "useToast must be used within a ToastProvider",
    );

    spy.mockRestore();
  });
});
