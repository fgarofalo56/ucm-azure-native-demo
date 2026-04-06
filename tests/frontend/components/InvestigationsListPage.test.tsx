import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { InvestigationsListPage } from "../../../src/frontend/src/pages/InvestigationsListPage";
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

// Use vi.hoisted so the mock fn is available in the factory
const { mockListInvestigations } = vi.hoisted(() => ({
  mockListInvestigations: vi.fn(),
}));

const defaultInvestigationsResponse = {
  data: [
    {
      id: "inv-1",
      record_id: "INVESTIGATION-001",
      title: "Salmonella Outbreak Q1",
      description: "Test desc",
      status: "active",
      document_count: 5,
      created_by: "user-1",
      created_by_name: "John Doe",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-15T00:00:00Z",
    },
    {
      id: "inv-2",
      record_id: "INVESTIGATION-002",
      title: "E. Coli Contamination",
      description: null,
      status: "closed",
      document_count: 12,
      created_by: "user-2",
      created_by_name: "Jane Smith",
      created_at: "2026-02-01T00:00:00Z",
      updated_at: "2026-02-15T00:00:00Z",
    },
  ],
  meta: { page: 1, page_size: 20, total: 2, status_counts: { active: 1, closed: 1 } },
};

// Mock the API module — data must be inline in factory (vi.mock is hoisted)
vi.mock("../../../src/frontend/src/api/investigations", () => ({
  listInvestigations: (...args: unknown[]) => mockListInvestigations(...args),
  createInvestigation: vi.fn().mockResolvedValue({
    id: "inv-new",
    record_id: "INVESTIGATION-999",
    title: "New Investigation",
  }),
  getInvestigation: vi.fn(),
  updateInvestigation: vi.fn(),
}));

describe("InvestigationsListPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockListInvestigations.mockResolvedValue(defaultInvestigationsResponse);
  });

  it("renders page header", () => {
    renderWithProviders(<InvestigationsListPage />);
    expect(screen.getByText("Investigations")).toBeInTheDocument();
    expect(
      screen.getByText("Manage and track investigation cases and their documents"),
    ).toBeInTheDocument();
  });

  it("renders New Investigation button", () => {
    renderWithProviders(<InvestigationsListPage />);
    expect(
      screen.getByRole("button", { name: /new investigation/i }),
    ).toBeInTheDocument();
  });

  it("shows loading state initially", () => {
    renderWithProviders(<InvestigationsListPage />);
    expect(screen.getByText("Loading investigations...")).toBeInTheDocument();
  });

  it("renders investigation table after loading", async () => {
    renderWithProviders(<InvestigationsListPage />);

    await waitFor(() => {
      expect(screen.getByText("INVESTIGATION-001")).toBeInTheDocument();
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
      expect(screen.getByText("INVESTIGATION-002")).toBeInTheDocument();
    });
  });

  it("shows status tabs with counts", async () => {
    renderWithProviders(<InvestigationsListPage />);

    await waitFor(() => {
      expect(screen.getByText("All")).toBeInTheDocument();
      expect(screen.getByText("Active")).toBeInTheDocument();
      expect(screen.getByText("Closed")).toBeInTheDocument();
      expect(screen.getByText("Archived")).toBeInTheDocument();
    });
  });

  it("has a search input", () => {
    renderWithProviders(<InvestigationsListPage />);
    expect(
      screen.getByPlaceholderText("Search by title or record ID..."),
    ).toBeInTheDocument();
  });

  it("sends search query to the API (server-side search)", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvestigationsListPage />);

    await waitFor(() => {
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
    });

    await user.type(
      screen.getByPlaceholderText("Search by title or record ID..."),
      "Salmonella",
    );

    // After debounce, API should be called with the search param
    await waitFor(() => {
      expect(mockListInvestigations).toHaveBeenCalledWith(
        undefined,
        1,
        20,
        "Salmonella",
      );
    });
  });

  it("opens create modal when New Investigation is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvestigationsListPage />);

    await user.click(
      screen.getByRole("button", { name: /new investigation/i }),
    );

    expect(
      screen.getByPlaceholderText("e.g., INVESTIGATION-12345"),
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Investigation title"),
    ).toBeInTheDocument();
  });

  it("shows format hint for Record ID", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvestigationsListPage />);

    await user.click(
      screen.getByRole("button", { name: /new investigation/i }),
    );

    expect(screen.getByText("Format: INVESTIGATION-#####")).toBeInTheDocument();
  });

  it("disables submit when fields are empty", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvestigationsListPage />);

    await user.click(
      screen.getByRole("button", { name: /new investigation/i }),
    );

    const submitBtn = screen.getByRole("button", {
      name: /create investigation/i,
    });
    expect(submitBtn).toBeDisabled();
  });

  it("enables submit when required fields are filled", async () => {
    const user = userEvent.setup();
    renderWithProviders(<InvestigationsListPage />);

    await user.click(
      screen.getByRole("button", { name: /new investigation/i }),
    );

    await user.type(
      screen.getByPlaceholderText("e.g., INVESTIGATION-12345"),
      "INVESTIGATION-999",
    );
    await user.type(
      screen.getByPlaceholderText("Investigation title"),
      "Test Investigation",
    );

    const submitBtn = screen.getByRole("button", {
      name: /create investigation/i,
    });
    expect(submitBtn).not.toBeDisabled();
  });

  it("shows pagination when results exist", async () => {
    renderWithProviders(<InvestigationsListPage />);

    await waitFor(() => {
      expect(screen.getByText(/showing/i)).toBeInTheDocument();
    });
  });
});
