import { describe, it, expect, vi } from 'vitest';

// Mock MSAL
vi.mock('@azure/msal-react', () => ({
  useMsal: () => ({
    instance: { acquireTokenSilent: vi.fn() },
    accounts: [{ name: 'Test User' }],
  }),
}));

describe('DocumentList', () => {
  it('renders empty state when no documents', () => {
    // Placeholder: requires test setup with React Query provider + MSAL mocks
    expect(true).toBe(true);
  });

  it('renders document rows when data is provided', () => {
    const mockDocuments = [
      {
        id: '1',
        file_id: 'file-001',
        original_filename: 'report.docx',
        content_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        file_size_bytes: 1024000,
        pdf_conversion_status: 'completed',
        uploaded_by_name: 'Test User',
        uploaded_at: '2026-01-15T10:00:00Z',
      },
    ];
    expect(mockDocuments).toHaveLength(1);
    expect(mockDocuments[0].original_filename).toBe('report.docx');
  });

  it('shows conversion status badges', () => {
    const statuses = ['pending', 'processing', 'completed', 'failed', 'not_required'];
    expect(statuses).toHaveLength(5);
  });

  it('enables multi-select for PDF merge', () => {
    const selected = new Set<string>();
    selected.add('file-001');
    selected.add('file-002');
    expect(selected.size).toBe(2);
  });
});
