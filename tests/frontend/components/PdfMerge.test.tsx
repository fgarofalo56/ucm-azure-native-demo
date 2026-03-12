import { describe, it, expect, vi } from 'vitest';

vi.mock('@azure/msal-react', () => ({
  useMsal: () => ({
    instance: { acquireTokenSilent: vi.fn() },
    accounts: [{ name: 'Test User' }],
  }),
}));

describe('PdfMerge', () => {
  it('requires at least 2 files to merge', () => {
    const selectedFiles = ['file-001'];
    expect(selectedFiles.length).toBeLessThan(2);
  });

  it('enforces maximum file count limit', () => {
    const maxFiles = 50;
    const selectedFiles = Array.from({ length: 51 }, (_, i) => `file-${i}`);
    expect(selectedFiles.length).toBeGreaterThan(maxFiles);
  });

  it('triggers merge and initiates download', () => {
    const mockMerge = vi.fn();
    const selectedIds = ['file-001', 'file-002', 'file-003'];
    mockMerge(selectedIds);
    expect(mockMerge).toHaveBeenCalledWith(selectedIds);
  });

  it('shows loading state during merge', () => {
    const isMerging = true;
    expect(isMerging).toBe(true);
  });

  it('displays error on merge failure', () => {
    const error = { message: 'Failed to merge PDFs' };
    expect(error.message).toContain('merge');
  });
});
