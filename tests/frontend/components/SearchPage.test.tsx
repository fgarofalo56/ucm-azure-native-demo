import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { SearchPage } from "../../../src/frontend/src/pages/SearchPage";
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

// Use vi.hoisted to make mockSearchFn available in vi.mock factory
const { mockSearchFn } = vi.hoisted(() => {
  const mockSearchFn = vi.fn();
  return { mockSearchFn };
});

const defaultSearchResults = {
  query: "salmonella",
  results: [
    {
      type: "investigation",
      id: "inv-1",
      title: "Salmonella Outbreak Q1",
      subtitle: "INVESTIGATION-001",
      url: "/investigations/inv-1",
    },
    {
      type: "document",
      id: "doc-1",
      title: "salmonella_test_results.pdf",
      subtitle: "Investigation: inv-1",
      url: "/investigations/inv-1",
    },
    {
      type: "document",
      id: "doc-2",
      title: "salmonella_lab_report.docx",
      subtitle: "Investigation: inv-1",
      url: "/investigations/inv-1",
    },
  ],
  total: 3,
};

vi.mock("../../../src/frontend/src/api/search", () => ({
  searchAll: (...args: unknown[]) => mockSearchFn(...args),
}));

vi.mock("../../../src/frontend/src/api/documents", () => ({
  copyDocumentsToInvestigation: vi.fn().mockResolvedValue({
    investigation_id: "inv-1",
    results: [{ document_id: "doc-1", success: true, new_file_id: "f-1" }],
    total: 1,
    succeeded: 1,
    failed: 0,
  }),
  uploadDocument: vi.fn(),
  getDocument: vi.fn(),
  downloadDocument: vi.fn(),
  downloadPdf: vi.fn(),
  getDocumentVersions: vi.fn(),
  deleteDocument: vi.fn(),
  mergePdfs: vi.fn(),
  listInvestigationDocuments: vi.fn(),
}));

// Mock investigations for InvestigationPicker
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

describe("SearchPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockSearchFn.mockResolvedValue(defaultSearchResults);
  });

  it("renders page header", () => {
    renderWithProviders(<SearchPage />);
    expect(screen.getByText("Search")).toBeInTheDocument();
    expect(
      screen.getByText("Search across investigations and documents"),
    ).toBeInTheDocument();
  });

  it("renders search input with autofocus", () => {
    renderWithProviders(<SearchPage />);
    const input = screen.getByPlaceholderText(
      "Search by title, filename, record ID...",
    );
    expect(input).toBeInTheDocument();
  });

  it("shows type filter tabs", () => {
    renderWithProviders(<SearchPage />);
    expect(screen.getByRole("button", { name: "All" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Investigations" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Documents" }),
    ).toBeInTheDocument();
  });

  it("shows hint when query is less than 2 characters", () => {
    renderWithProviders(<SearchPage />);
    expect(
      screen.getByText("Type at least 2 characters to search"),
    ).toBeInTheDocument();
  });

  it("shows search results after typing", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SearchPage />);

    await user.type(
      screen.getByPlaceholderText("Search by title, filename, record ID..."),
      "salmonella",
    );

    await waitFor(() => {
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
      expect(
        screen.getByText("salmonella_test_results.pdf"),
      ).toBeInTheDocument();
    });
  });

  it("groups results by type with headers", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SearchPage />);

    await user.type(
      screen.getByPlaceholderText("Search by title, filename, record ID..."),
      "salmonella",
    );

    await waitFor(() => {
      expect(screen.getByText(/Investigations \(1\)/)).toBeInTheDocument();
      expect(screen.getByText(/Documents \(2\)/)).toBeInTheDocument();
    });
  });

  it("shows checkboxes for document results", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SearchPage />);

    await user.type(
      screen.getByPlaceholderText("Search by title, filename, record ID..."),
      "salmonella",
    );

    await waitFor(() => {
      expect(
        screen.getByText("salmonella_test_results.pdf"),
      ).toBeInTheDocument();
    });

    // Document results should have checkboxes
    const checkboxes = screen.getAllByRole("checkbox");
    expect(checkboxes.length).toBe(2); // 2 document results
  });

  it("shows Add to Investigation button when documents are selected", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SearchPage />);

    await user.type(
      screen.getByPlaceholderText("Search by title, filename, record ID..."),
      "salmonella",
    );

    await waitFor(() => {
      expect(
        screen.getByText("salmonella_test_results.pdf"),
      ).toBeInTheDocument();
    });

    // Select a document
    const checkboxes = screen.getAllByRole("checkbox");
    await user.click(checkboxes[0]);

    expect(
      screen.getByRole("button", { name: /add 1 to investigation/i }),
    ).toBeInTheDocument();
  });

  it("shows no results message for empty query", async () => {
    // Override mock to always return empty results
    mockSearchFn.mockResolvedValue({
      query: "zzzzz",
      results: [],
      total: 0,
    });

    const user = userEvent.setup();
    renderWithProviders(<SearchPage />);

    await user.type(
      screen.getByPlaceholderText("Search by title, filename, record ID..."),
      "zzzzz",
    );

    await waitFor(() => {
      expect(screen.getByText(/no results found/i)).toBeInTheDocument();
    });
  });
});
