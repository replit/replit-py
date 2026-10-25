"""Tests for database retry backoff."""

from unittest import TestCase
from unittest.mock import patch

from replit.database.database import _JitteredExponentialRetry, _JitteredRetry


class TestJitteredExponentialRetry(TestCase):
    """Tests for async database retry backoff."""

    def test_adds_jitter_to_exponential_timeout(self) -> None:
        """Async retry delays include jitter while respecting their cap."""
        retry = _JitteredExponentialRetry(
            attempts=3, start_timeout=1, factor=2, max_timeout=3
        )

        with patch("replit.database.database._SYSTEM_RANDOM.uniform", return_value=1.5):
            self.assertEqual(retry.get_timeout(attempt=1), 3)


class TestJitteredRetry(TestCase):
    """Tests for synchronous database retry backoff."""

    def test_adds_jitter_to_first_retry(self) -> None:
        """The first synchronous retry is delayed by random jitter."""
        retry = _JitteredRetry(total=3, backoff_factor=0.1)
        retry = retry.increment(method="GET", url="/")

        with patch(
            "replit.database.database._SYSTEM_RANDOM.uniform", return_value=0.05
        ):
            self.assertEqual(retry.get_backoff_time(), 0.05)
