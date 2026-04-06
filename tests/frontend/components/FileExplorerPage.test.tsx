import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { FileExplorerPage } from "../../../src/frontend/src/pages/FileExplorerPage";
import { renderWithProviders } from "../utils/test-utils";

// Mock MSAL
vi.mock("../../../src/frontend/src/auth/msal-instance", () => ({
  msalInstance: {
    getActiveAccount: () => ({ name: "Test User" }),
    getAllAccounts: () => [{ name: "Test User" }],
    acquireTokenSilent: vi.fn().mockResolvedValue({ accessToken: "mock-token" }),
  },
}));

vi.mock("../../../src/frontend/src/auth/msal-config", () => ({
  apiScopes: ["api://test/access_as_user"],
}));

vi.mock("../../../src/frontend/src/api/explorer", () => ({
  browseExplorer: vi.fn().mockResolvedValue({
    prefix: "",
    items: [
      {
        name: "INVESTIGATION-001",
        type: "folder",
        path: "INVESTIGATION-001/",
        size: null,
        last_modified: null,
        content_type: null,
      },
      {
        name: "report.pdf",
        type: "file",
        path: "report.pdf",
        size: 102400,
        last_modified: "2026-03-01T10:00:00Z",
        content_type: "application/pdf",
      },
      {
        name: "data.csv",
        type: "file",
        path: "data.csv",
        size: 2048,
        last_modified: "2026-03-02T10:00:00Z",
        content_type: "text/csv",
      },
    ],
  }),
  downloadExplorerFile: vi.fn().mockResolvedValue(new Blob(["test"])),
  addFilesToInvestigation: vi.fn().mockResolvedValue({
    investigation_id: "inv-1",
    results: [{ blob_path: "report.pdf", success: true, file_id: "f-1" }],
    total: 1,
    succeeded: 1,
    failed: 0,
  }),
  deleteExplorerFiles: vi.fn(),
}));

// Also mock investigations for the picker
vi.mock("../../../src/frontend/src/api/investigations", () => ({
  listInvestigations: vi.fn().mockResolvedValue({
    data: [
      {
        id: "inv-1",
        record_id: "INVESTIGATION-001",
        title: "Test Investigation",
        status: "active",
        document_count: 3,
        created_by: "user-1",
        created_by_name: "Test User",
        created_at: "2026-01-01T00:00:00Z",
        updated_at: "2026-01-15T00:00:00Z",
      },
    ],
    meta: { page: 1, page_size: 20, total: 1 },
  }),
  createInvestigation: vi.fn(),
  getInvestigation: vi.fn(),
  updateInvestigation: vi.fn(),
}));

describe("FileExplorerPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page header", () => {
    renderWithProviders(<FileExplorerPage />);
    expect(screen.getByText("File Explorer")).toBeInTheDocument();
    expect(
      screen.getByText("Browse investigation folders and document files"),
    ).toBeInTheDocument();
  });

  it("renders breadcrumb with Root", () => {
    renderWithProviders(<FileExplorerPage />);
    expect(screen.getByText("Root")).toBeInTheDocument();
  });

  it("shows loading state initially", () => {
    renderWithProviders(<FileExplorerPage />);
    // The spinner is present via Loader2 icon
    expect(document.querySelector(".animate-spin")).toBeInTheDocument();
  });

  it("renders folder and file items after loading", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("INVESTIGATION-001")).toBeInTheDocument();
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
      expect(screen.getByText("data.csv")).toBeInTheDocument();
    });
  });

  it("shows file sizes for files", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("100 KB")).toBeInTheDocument(); // 102400 bytes
      expect(screen.getByText("2 KB")).toBeInTheDocument(); // 2048 bytes
    });
  });

  it("shows checkboxes for files but not folders", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole("checkbox");
    // select-all checkbox + 2 file checkboxes = 3
    expect(checkboxes.length).toBe(3);
  });

  it("shows Add to Investigation button when files are selected", async () => {
    const user = userEvent.setup();
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    // No button initially
    expect(
      screen.queryByRole("button", { name: /add.*investigation/i }),
    ).not.toBeInTheDocument();

    // Select a file
    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[1]); // First file checkbox

    // Button should appear
    expect(
      screen.getByRole("button", { name: /add 1 file.*investigation/i }),
    ).toBeInTheDocument();
  });

  it("select all checkbox toggles all files", async () => {
    const user = userEvent.setup();
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    const checkboxes = screen.getAllByRole("checkbox");
    const selectAll = checkboxes[0]; // Header checkbox

    await user.click(selectAll);

    // Should show "Add 2 files" button
    expect(
      screen.getByRole("button", { name: /add 2 files.*investigation/i }),
    ).toBeInTheDocument();

    // Toggle off
    await user.click(selectAll);
    expect(
      screen.queryByRole("button", { name: /add.*investigation/i }),
    ).not.toBeInTheDocument();
  });

  it("has download buttons for files", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    const downloadButtons = screen.getAllByTitle("Download");
    expect(downloadButtons.length).toBe(2); // 2 files
  });

  it("has delete buttons for files", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("report.pdf")).toBeInTheDocument();
    });

    const deleteButtons = screen.getAllByTitle("Delete");
    expect(deleteButtons.length).toBe(2);
  });

  it("renders table headers", async () => {
    renderWithProviders(<FileExplorerPage />);

    await waitFor(() => {
      expect(screen.getByText("Name")).toBeInTheDocument();
      expect(screen.getByText("Size")).toBeInTheDocument();
      expect(screen.getByText("Modified")).toBeInTheDocument();
      expect(screen.getByText("Actions")).toBeInTheDocument();
    });
  });
});
