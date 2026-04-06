"""Unit tests for rate limiting middleware."""

from unittest.mock import MagicMock

from app.middleware.rate_limit import get_client_ip


class TestRateLimit:
    def test_get_client_ip_direct(self):
        """Should return remote address when no forwarded header."""
        request = MagicMock()
        request.headers.get.return_value = None
        request.client.host = "192.168.1.1"

        # Mock get_remote_address behavior
        with MagicMock() as mock_get_remote:
            mock_get_remote.return_value = "192.168.1.1"
            # Import and patch at module level
            import app.middleware.rate_limit as rl_module
            original_get_remote = rl_module.get_remote_address
            rl_module.get_remote_address = mock_get_remote

            ip = get_client_ip(request)

            # Restore original function
            rl_module.get_remote_address = original_get_remote

            assert ip == "192.168.1.1"
            mock_get_remote.assert_called_once_with(request)

    def test_get_client_ip_forwarded_multiple(self):
        """Should extract first IP from X-Forwarded-For header."""
        request = MagicMock()
        request.headers.get.return_value = "10.0.0.1, 10.0.0.2, 10.0.0.3"

        ip = get_client_ip(request)

        assert ip == "10.0.0.1"

    def test_get_client_ip_forwarded_single(self):
        """Should handle single IP in X-Forwarded-For."""
        request = MagicMock()
        request.headers.get.return_value = "10.0.0.1"

        ip = get_client_ip(request)

        assert ip == "10.0.0.1"

    def test_get_client_ip_forwarded_with_spaces(self):
        """Should strip whitespace from forwarded IPs."""
        request = MagicMock()
        request.headers.get.return_value = "  10.0.0.1  ,  10.0.0.2  "

        ip = get_client_ip(request)

        assert ip == "10.0.0.1"

    def test_get_client_ip_forwarded_empty(self):
        """Should fall back to remote address when forwarded header is empty."""
        request = MagicMock()
        request.headers.get.return_value = ""

        # Mock get_remote_address behavior
        with MagicMock() as mock_get_remote:
            mock_get_remote.return_value = "127.0.0.1"
            import app.middleware.rate_limit as rl_module
            original_get_remote = rl_module.get_remote_address
            rl_module.get_remote_address = mock_get_remote

            ip = get_client_ip(request)

            # Restore original function
            rl_module.get_remote_address = original_get_remote

            assert ip == "127.0.0.1"

    def test_get_client_ip_forwarded_whitespace_only(self):
        """Should handle forwarded header with only whitespace."""
        request = MagicMock()
        request.headers.get.return_value = "   "

        ip = get_client_ip(request)

        # Whitespace-only header results in empty string after strip
        assert ip == ""

    def test_get_client_ip_header_case_insensitive(self):
        """Should handle case variations in header name."""
        request = MagicMock()
        # Test with different case
        request.headers.get.side_effect = lambda h: {
            "X-Forwarded-For": "10.0.0.1",
            "x-forwarded-for": "10.0.0.1",
            "X-FORWARDED-FOR": "10.0.0.1",
        }.get(h)

        ip = get_client_ip(request)

        assert ip == "10.0.0.1"

    def test_header_parsing_edge_cases(self):
        """Should handle edge cases in header parsing."""
        test_cases = [
            ("10.0.0.1,", "10.0.0.1"),  # Trailing comma
            (",10.0.0.1", ""),  # Leading comma (empty first element after strip)
            ("10.0.0.1,,10.0.0.2", "10.0.0.1"),  # Empty middle element
            ("192.168.1.100", "192.168.1.100"),  # No comma
        ]

        for header_value, expected_ip in test_cases:
            request = MagicMock()
            request.headers.get.return_value = header_value

            ip = get_client_ip(request)
            assert ip == expected_ip, f"For header '{header_value}', expected '{expected_ip}' but got '{ip}'"