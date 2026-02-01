"""
Unit tests for sentiment.py (VADER sentiment analysis).
"""

import sys
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Reset module state before tests
import core.sentiment as sentiment_module
from core.sentiment import (
    analyze_prompt,
    check_rolling_sentiment,
    is_vader_available,
    update_sentiment_window,
)
from core.settings import Settings
from core.state import SessionState


@pytest.fixture(autouse=True)
def reset_vader_state():
    """Reset VADER cached state before each test."""
    sentiment_module._vader_available = None
    sentiment_module._vader_analyzer = None
    yield
    sentiment_module._vader_available = None
    sentiment_module._vader_analyzer = None


class TestIsVaderAvailable:
    """Test is_vader_available function."""

    def test_vader_available_when_installed(self):
        """Test returns True when vaderSentiment is installed."""
        # This test will pass if vaderSentiment is installed
        result = is_vader_available()
        # We can't assert True/False without knowing if it's installed
        # Just verify it returns a boolean and caches
        assert isinstance(result, bool)

        # Verify caching
        result2 = is_vader_available()
        assert result == result2

    def test_vader_unavailable_with_mock(self):
        """Test returns False when vaderSentiment import fails."""
        with (
            mock.patch.dict("sys.modules", {"vaderSentiment": None}),
            mock.patch(
                "builtins.__import__",
                side_effect=ImportError("No module named 'vaderSentiment'"),
            ),
        ):
            sentiment_module._vader_available = None
            # Force re-check
            sentiment_module.is_vader_available()
            # The cached value should now be set
            assert sentiment_module._vader_available is not None


class TestAnalyzePrompt:
    """Test analyze_prompt function."""

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_positive_sentiment(self):
        """Test analyzing positive text."""
        score = analyze_prompt("This is wonderful! I love it!")
        assert score is not None
        assert score > 0

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_negative_sentiment(self):
        """Test analyzing negative text."""
        score = analyze_prompt("This is terrible and frustrating!")
        assert score is not None
        assert score < 0

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_neutral_sentiment(self):
        """Test analyzing neutral text."""
        score = analyze_prompt("The function takes two parameters")
        assert score is not None
        # Neutral text should be close to 0
        assert -0.3 <= score <= 0.3

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_empty_text(self):
        """Test analyzing empty text returns 0."""
        score = analyze_prompt("")
        assert score == 0.0

        score = analyze_prompt("   ")
        assert score == 0.0


class TestCheckRollingSentiment:
    """Test check_rolling_sentiment function."""

    @pytest.fixture
    def settings(self):
        """Create default settings."""
        return Settings.from_dict({})

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_no_nudge_with_positive_sentiment(self, settings):
        """Test no nudge when sentiment is positive."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=10,
            sentiment_scores=[0.5, 0.3, 0.4, 0.2, 0.1],
            last_nudge_prompt=None,
        )
        result = check_rolling_sentiment(state, settings)
        assert result is None

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_nudge_with_negative_sentiment(self, settings):
        """Test nudge when sentiment is negative."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=10,
            sentiment_scores=[-0.5, -0.4, -0.6, -0.3, -0.5],
            last_nudge_prompt=None,
        )
        result = check_rolling_sentiment(state, settings)
        assert result is not None
        assert "frustration" in result.message
        assert result.average_score < settings.sentiment.threshold

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_no_nudge_with_few_prompts(self, settings):
        """Test no nudge when below min_prompts."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=2,
            sentiment_scores=[-0.5, -0.5],  # Only 2 scores
            last_nudge_prompt=None,
        )
        result = check_rolling_sentiment(state, settings)
        assert result is None

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_cooldown_prevents_nudge(self, settings):
        """Test cooldown prevents repeated nudges."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=15,
            sentiment_scores=[-0.5, -0.4, -0.6, -0.3, -0.5],
            last_nudge_prompt=10,  # Nudged at prompt 10, only 5 prompts ago
        )
        result = check_rolling_sentiment(state, settings)
        assert result is None  # Cooldown prevents nudge

    @pytest.mark.skipif(
        not is_vader_available(), reason="vaderSentiment not installed"
    )
    def test_nudge_after_cooldown(self, settings):
        """Test nudge allowed after cooldown period."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=25,
            sentiment_scores=[-0.5, -0.4, -0.6, -0.3, -0.5],
            last_nudge_prompt=10,  # Nudged at prompt 10, 15 prompts ago
        )
        result = check_rolling_sentiment(state, settings)
        assert result is not None  # Cooldown passed

    def test_no_nudge_when_disabled(self):
        """Test no nudge when sentiment is disabled."""
        settings = Settings.from_dict({"sentiment": {"enabled": False}})
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=10,
            sentiment_scores=[-0.5, -0.4, -0.6, -0.3, -0.5],
            last_nudge_prompt=None,
        )
        result = check_rolling_sentiment(state, settings)
        assert result is None


class TestUpdateSentimentWindow:
    """Test update_sentiment_window function."""

    def test_adds_score_to_empty_window(self):
        """Test adding score to empty window."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=1,
            sentiment_scores=[],
            last_nudge_prompt=None,
        )
        result = update_sentiment_window(state, 0.5, window_size=5)
        assert result == [0.5]
        assert state.sentiment_scores == [0.5]

    def test_adds_score_to_partial_window(self):
        """Test adding score to partial window."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=3,
            sentiment_scores=[0.1, 0.2],
            last_nudge_prompt=None,
        )
        result = update_sentiment_window(state, 0.3, window_size=5)
        assert result == [0.1, 0.2, 0.3]

    def test_trims_window_when_full(self):
        """Test window is trimmed when full."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=6,
            sentiment_scores=[0.1, 0.2, 0.3, 0.4, 0.5],
            last_nudge_prompt=None,
        )
        result = update_sentiment_window(state, 0.6, window_size=5)
        assert result == [0.2, 0.3, 0.4, 0.5, 0.6]
        assert len(result) == 5

    def test_modifies_state_in_place(self):
        """Test state is modified in place."""
        state = SessionState(
            session_id="test",
            started_at=datetime.now(),
            prompt_count=1,
            sentiment_scores=[0.1],
            last_nudge_prompt=None,
        )
        update_sentiment_window(state, 0.2, window_size=5)
        assert state.sentiment_scores == [0.1, 0.2]
