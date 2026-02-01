"""
Sentiment detection logic for mind-reader plugin.
Uses VADER for sentiment analysis with lazy loading.
"""

from __future__ import annotations

from dataclasses import dataclass

from .settings import Settings
from .state import SessionState

# Lazy-loaded VADER state
_vader_available: bool | None = None
_vader_analyzer: object | None = None


@dataclass
class SentimentNudge:
    """Result of a sentiment check."""

    message: str
    average_score: float


def is_vader_available() -> bool:
    """
    Check if VADER is installed.

    Returns:
        True if vaderSentiment is available.
    """
    global _vader_available

    if _vader_available is not None:
        return _vader_available

    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        _vader_available = True
    except ImportError:
        _vader_available = False

    return _vader_available


def _get_analyzer():
    """Get or create VADER analyzer instance."""
    global _vader_analyzer

    if _vader_analyzer is not None:
        return _vader_analyzer

    if not is_vader_available():
        return None

    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

    _vader_analyzer = SentimentIntensityAnalyzer()
    return _vader_analyzer


def analyze_prompt(text: str) -> float | None:
    """
    Analyze sentiment of a prompt.

    Args:
        text: Text to analyze

    Returns:
        Compound sentiment score (-1 to 1), or None if VADER unavailable.
    """
    if not is_vader_available():
        return None

    if not text or not text.strip():
        return 0.0

    analyzer = _get_analyzer()
    if analyzer is None:
        return None

    scores = analyzer.polarity_scores(text)
    return scores["compound"]


def update_sentiment_window(
    state: SessionState,
    score: float,
    window_size: int,
) -> list[float]:
    """
    Add a score to the rolling sentiment window.

    Args:
        state: Session state (modified in place)
        score: New sentiment score
        window_size: Maximum window size

    Returns:
        Updated sentiment scores list.
    """
    state.sentiment_scores.append(score)

    if len(state.sentiment_scores) > window_size:
        state.sentiment_scores = state.sentiment_scores[-window_size:]

    return state.sentiment_scores


def check_rolling_sentiment(
    state: SessionState,
    settings: Settings,
) -> SentimentNudge | None:
    """
    Check if rolling sentiment indicates frustration.

    Args:
        state: Current session state
        settings: Plugin settings

    Returns:
        SentimentNudge if frustration detected, None otherwise.
    """
    if not settings.sentiment.enabled:
        return None

    if not is_vader_available():
        return None

    if len(state.sentiment_scores) < settings.sentiment.min_prompts:
        return None

    # Check cooldown
    if state.last_nudge_prompt is not None:
        prompts_since_nudge = state.prompt_count - state.last_nudge_prompt
        if prompts_since_nudge < settings.sentiment.cooldown_prompts:
            return None

    # Calculate rolling average
    avg_score = sum(state.sentiment_scores) / len(state.sentiment_scores)

    if avg_score >= settings.sentiment.threshold:
        return None

    return SentimentNudge(
        message=f"Recent prompts suggest frustration (avg: {avg_score:.2f}). Everything okay?",
        average_score=avg_score,
    )
