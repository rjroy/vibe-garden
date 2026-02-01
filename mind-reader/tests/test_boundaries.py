"""
Unit tests for boundaries.py (boundary discovery logic).
"""

import sys
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from core.boundaries import (
    DEFAULT_BOUNDARIES,
    discover_boundaries,
    get_all_bucket_names,
    get_bucket_name,
    is_scipy_available,
)


class TestIsSciPyAvailable:
    """Test is_scipy_available function."""

    def test_returns_bool(self):
        """Test returns boolean."""
        result = is_scipy_available()
        assert isinstance(result, bool)

    def test_caches_result(self):
        """Test result is cached (calling twice returns same value)."""
        result1 = is_scipy_available()
        result2 = is_scipy_available()
        assert result1 == result2


class TestDiscoverBoundaries:
    """Test discover_boundaries function."""

    def test_empty_counts_returns_defaults(self):
        """Test empty counts returns default boundaries."""
        assert discover_boundaries([]) == DEFAULT_BOUNDARIES

    def test_wrong_length_returns_defaults(self):
        """Test non-24 length returns default boundaries."""
        assert discover_boundaries([1, 2, 3]) == DEFAULT_BOUNDARIES

    def test_uniform_counts_returns_defaults(self):
        """Test uniform counts returns defaults (no valleys)."""
        counts = [10] * 24
        assert discover_boundaries(counts) == DEFAULT_BOUNDARIES

    def test_all_zeros_returns_defaults(self):
        """Test all zeros returns defaults."""
        counts = [0] * 24
        assert discover_boundaries(counts) == DEFAULT_BOUNDARIES

    @pytest.mark.skipif(
        not is_scipy_available(), reason="scipy not installed"
    )
    def test_clear_valleys_discovers_boundaries(self):
        """Test finds boundaries at clear valleys."""
        # Create data with clear valleys at 6, 12, 18, 22
        counts = [0] * 24
        # Morning activity (7-11)
        for h in range(7, 12):
            counts[h] = 50
        # Afternoon activity (13-17)
        for h in range(13, 18):
            counts[h] = 40
        # Evening activity (19-21)
        for h in range(19, 22):
            counts[h] = 30
        # Late night minimal
        counts[23] = 5
        counts[0] = 2

        result = discover_boundaries(counts)

        # Should find boundaries near the valleys
        assert isinstance(result, list)
        assert len(result) == 4
        # Results should be sorted
        assert result == sorted(result)

    def test_scipy_unavailable_returns_defaults(self):
        """Test returns defaults when scipy not available."""
        with mock.patch(
            "core.boundaries.is_scipy_available", return_value=False
        ):
            counts = [10, 20, 30] * 8  # 24 values
            result = discover_boundaries(counts)
            assert result == DEFAULT_BOUNDARIES


class TestGetBucketName:
    """Test get_bucket_name function."""

    def test_with_default_boundaries(self):
        """Test bucket mapping with default boundaries [6, 12, 18, 22]."""
        boundaries = [6, 12, 18, 22]

        # late_night: 0-5, 22-23
        assert get_bucket_name(0, boundaries) == "late_night"
        assert get_bucket_name(3, boundaries) == "late_night"
        assert get_bucket_name(5, boundaries) == "late_night"

        # early_morning: 6-11
        assert get_bucket_name(6, boundaries) == "early_morning"
        assert get_bucket_name(9, boundaries) == "early_morning"
        assert get_bucket_name(11, boundaries) == "early_morning"

        # morning: 12-17
        assert get_bucket_name(12, boundaries) == "morning"
        assert get_bucket_name(14, boundaries) == "morning"
        assert get_bucket_name(17, boundaries) == "morning"

        # afternoon: 18-21
        assert get_bucket_name(18, boundaries) == "afternoon"
        assert get_bucket_name(20, boundaries) == "afternoon"
        assert get_bucket_name(21, boundaries) == "afternoon"

        # evening: 22-23
        assert get_bucket_name(22, boundaries) == "evening"
        assert get_bucket_name(23, boundaries) == "evening"

    def test_with_custom_boundaries(self):
        """Test bucket mapping with custom boundaries."""
        boundaries = [5, 10, 16, 20]

        assert get_bucket_name(3, boundaries) == "late_night"
        assert get_bucket_name(7, boundaries) == "early_morning"
        assert get_bucket_name(13, boundaries) == "morning"
        assert get_bucket_name(18, boundaries) == "afternoon"
        assert get_bucket_name(22, boundaries) == "evening"

    def test_empty_boundaries_uses_defaults(self):
        """Test empty boundaries uses defaults."""
        assert get_bucket_name(10, []) == get_bucket_name(10, DEFAULT_BOUNDARIES)

    def test_wrong_length_boundaries_uses_defaults(self):
        """Test wrong length boundaries uses defaults."""
        assert get_bucket_name(10, [6, 12]) == get_bucket_name(10, DEFAULT_BOUNDARIES)

    def test_unsorted_boundaries_get_sorted(self):
        """Test unsorted boundaries are handled correctly."""
        # Pass unsorted, should still work
        result = get_bucket_name(14, [18, 6, 22, 12])
        expected = get_bucket_name(14, [6, 12, 18, 22])
        assert result == expected


class TestGetAllBucketNames:
    """Test get_all_bucket_names function."""

    def test_returns_all_names(self):
        """Test returns all bucket names."""
        names = get_all_bucket_names()

        assert "late_night" in names
        assert "early_morning" in names
        assert "morning" in names
        assert "afternoon" in names
        assert "evening" in names
        assert len(names) == 5

    def test_returns_list(self):
        """Test returns a list."""
        names = get_all_bucket_names()
        assert isinstance(names, list)
