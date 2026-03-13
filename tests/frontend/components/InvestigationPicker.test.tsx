import { describe, it, expect, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import InvestigationPicker from "../../../src/frontend/src/components/ui/InvestigationPicker";
import { renderWithProviders } from "../utils/test-utils";

// Use vi.hoisted so the mock fn is available in the factory
const { mockListInvestigations } = vi.hoisted(() => ({
  mockListInvestigations: vi.fn(),
}));

const defaultPickerResponse = {
  data: [
    {
      id: "inv-1",
      record_id: "INVESTIGATION-001",
      title: "Salmonella Outbreak Q1",
      status: "active",
      document_count: 5,
      created_by: "user-1",
      created_by_name: "Test User",
      created_at: "2026-01-01T00:00:00Z",
      updated_at: "2026-01-15T00:00:00Z",
    },
    {
      id: "inv-2",
      record_id: "INVESTIGATION-002",
      title: "E. Coli Contamination",
      status: "active",
      document_count: 12,
      created_by: "user-1",
      created_by_name: "Test User",
      created_at: "2026-02-01T00:00:00Z",
      updated_at: "2026-02-15T00:00:00Z",
    },
  ],
  meta: { page: 1, page_size: 20, total: 2 },
};

// Mock the investigations API
vi.mock("../../../src/frontend/src/api/investigations", () => ({
  listInvestigations: (...args: unknown[]) => mockListInvestigations(...args),
  createInvestigation: vi.fn(),
  getInvestigation: vi.fn(),
  updateInvestigation: vi.fn(),
}));

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

describe("InvestigationPicker", () => {
  const mockOnClose = vi.fn();
  const mockOnSelect = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockListInvestigations.mockResolvedValue(defaultPickerResponse);
  });

  it("renders nothing when closed", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={false}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );
    expect(screen.queryByText("Add to Investigation")).not.toBeInTheDocument();
  });

  it("renders modal with title when open", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );
    expect(screen.getByText("Add to Investigation")).toBeInTheDocument();
  });

  it("renders search input", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );
    expect(
      screen.getByPlaceholderText("Search investigations..."),
    ).toBeInTheDocument();
  });

  it("renders cancel and add files buttons", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Add Files" }),
    ).toBeInTheDocument();
  });

  it("add files button is disabled when nothing is selected", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );
    expect(screen.getByRole("button", { name: "Add Files" })).toBeDisabled();
  });

  it("calls onClose when cancel is clicked", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it("shows investigations list after loading", async () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
      expect(screen.getByText("E. Coli Contamination")).toBeInTheDocument();
    });
  });

  it("allows selecting an investigation and submitting", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
    });

    // Click to select
    await user.click(screen.getByText("Salmonella Outbreak Q1"));

    // Add Files should now be enabled
    const addBtn = screen.getByRole("button", { name: "Add Files" });
    expect(addBtn).not.toBeDisabled();

    await user.click(addBtn);
    expect(mockOnSelect).toHaveBeenCalledWith("inv-1");
  });

  it("sends search term to the API (server-side search)", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
      />,
    );

    await waitFor(() => {
      expect(screen.getByText("Salmonella Outbreak Q1")).toBeInTheDocument();
    });

    await user.type(
      screen.getByPlaceholderText("Search investigations..."),
      "Coli",
    );

    // The API should be called with the search term
    await waitFor(() => {
      expect(mockListInvestigations).toHaveBeenCalledWith(
        undefined,
        1,
        20,
        "Coli",
      );
    });
  });

  it("accepts custom title prop", () => {
    renderWithProviders(
      <InvestigationPicker
        isOpen={true}
        onClose={mockOnClose}
        onSelect={mockOnSelect}
        title="Copy Documents"
      />,
    );
    expect(screen.getByText("Copy Documents")).toBeInTheDocument();
  });
});
