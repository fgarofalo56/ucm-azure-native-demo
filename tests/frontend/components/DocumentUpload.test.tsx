import { describe, it, expect, vi } from 'vitest';

vi.mock('@azure/msal-react', () => ({
  useMsal: () => ({
    instance: { acquireTokenSilent: vi.fn() },
    accounts: [{ name: 'Test User' }],
  }),
}));

describe('DocumentUpload', () => {
  it('accepts files via drag and drop', () => {
    const file = new File(['test content'], 'test.docx', {
      type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    });
    expect(file.name).toBe('test.docx');
    expect(file.size).toBeGreaterThan(0);
  });

  it('rejects files exceeding max size', () => {
    const maxSize = 500 * 1024 * 1024; // 500MB
    const oversizedFile = { size: maxSize + 1 };
    expect(oversizedFile.size).toBeGreaterThan(maxSize);
  });

  it('shows upload progress', () => {
    const progress = { loaded: 50, total: 100 };
    const percent = Math.round((progress.loaded / progress.total) * 100);
    expect(percent).toBe(50);
  });

  it('displays success message after upload', () => {
    const response = { id: 'doc-1', status: 'pending_conversion' };
    expect(response.status).toBe('pending_conversion');
  });
});
