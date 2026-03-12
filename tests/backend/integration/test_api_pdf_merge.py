"""Integration tests for PDF merge endpoint."""

import pytest


class TestPdfMergeEndpoint:
    def test_merge_requires_at_least_two_files(self, test_client):
        """Merge should reject requests with fewer than 2 file IDs."""
        response = test_client.post(
            "/api/v1/investigations/INVESTIGATION-123/merge-pdf",
            json={"file_ids": ["one"]},
        )
        assert response.status_code == 422  # Validation error

    def test_merge_rejects_empty_list(self, test_client):
        response = test_client.post(
            "/api/v1/investigations/INVESTIGATION-123/merge-pdf",
            json={"file_ids": []},
        )
        assert response.status_code == 422
