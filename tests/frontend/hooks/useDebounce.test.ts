import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { renderHook, act } from "@testing-library/react";
import { useDebounce } from "@/hooks/useDebounce";

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("returns the initial value immediately", () => {
    const { result } = renderHook(() => useDebounce("initial", 500));
    expect(result.current).toBe("initial");
  });

  it("does not update the value before the delay has elapsed", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } },
    );

    rerender({ value: "updated", delay: 500 });

    // Only 200ms in — should still be the old value
    act(() => {
      vi.advanceTimersByTime(200);
    });
    expect(result.current).toBe("initial");
  });

  it("updates the value after the delay", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } },
    );

    rerender({ value: "updated", delay: 500 });

    act(() => {
      vi.advanceTimersByTime(500);
    });

    expect(result.current).toBe("updated");
  });

  it("resets the timer on rapid successive changes", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "a", delay: 500 } },
    );

    rerender({ value: "ab", delay: 500 });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    rerender({ value: "abc", delay: 500 });
    act(() => {
      vi.advanceTimersByTime(200);
    });

    // 400ms since the last change — still the original value
    expect(result.current).toBe("a");

    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Now 500ms since "abc" was set — should update
    expect(result.current).toBe("abc");
  });

  it("works with number values", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 0, delay: 300 } },
    );

    rerender({ value: 42, delay: 300 });
    act(() => {
      vi.advanceTimersByTime(300);
    });
    expect(result.current).toBe(42);
  });

  it("works with object values (reference changes)", () => {
    const obj1 = { name: "Alice" };
    const obj2 = { name: "Bob" };

    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: obj1, delay: 300 } },
    );

    rerender({ value: obj2, delay: 300 });

    // Before delay — still the first object
    expect(result.current).toBe(obj1);

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current).toBe(obj2);
  });

  it("cleans up the timeout on unmount", () => {
    const clearTimeoutSpy = vi.spyOn(globalThis, "clearTimeout");

    const { unmount } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "test", delay: 500 } },
    );

    unmount();

    // The cleanup function in useEffect should have called clearTimeout
    expect(clearTimeoutSpy).toHaveBeenCalled();
    clearTimeoutSpy.mockRestore();
  });

  it("handles delay changes", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "test", delay: 500 } },
    );

    // Change delay to 100ms (both value and delay change triggers new timer)
    rerender({ value: "changed", delay: 100 });

    act(() => {
      vi.advanceTimersByTime(100);
    });

    expect(result.current).toBe("changed");
  });
});
