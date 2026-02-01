"""
State management for mind-reader plugin.
Handles session state, baseline, paths, and atomic file operations.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


def get_data_dir() -> Path:
    """Get path to mind-reader data directory."""
    return Path.home() / ".claude" / "mind-reader"


def get_baseline_path() -> Path:
    """Get path to baseline file."""
    return get_data_dir() / "baseline.json"


def get_session_path(session_id: str) -> Path:
    """Get path to session state file."""
    return get_data_dir() / "sessions" / f"{session_id}.json"


def get_lock_path() -> Path:
    """Get path to baseline lock file."""
    return get_data_dir() / "baseline.lock"


@dataclass
class SessionState:
    """Per-session state tracking."""

    session_id: str
    started_at: datetime = field(default_factory=datetime.now)
    prompt_count: int = 0
    sentiment_scores: list[float] = field(default_factory=list)
    last_nudge_prompt: int | None = None

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "prompt_count": self.prompt_count,
            "sentiment_scores": self.sentiment_scores,
            "last_nudge_prompt": self.last_nudge_prompt,
        }

    @classmethod
    def from_dict(cls, data: dict) -> SessionState:
        """Deserialize from dictionary."""
        started_at = datetime.now()
        if "started_at" in data:
            try:
                started_at = datetime.fromisoformat(data["started_at"])
            except (ValueError, TypeError):
                pass

        return cls(
            session_id=data.get("session_id", ""),
            started_at=started_at,
            prompt_count=data.get("prompt_count", 0),
            sentiment_scores=data.get("sentiment_scores", []),
            last_nudge_prompt=data.get("last_nudge_prompt"),
        )


@dataclass
class BucketStats:
    """Statistics for a single time bucket."""

    session_count: int
    session_rate: float  # session_count / window_days
    duration: dict[str, float]  # p50, p75, p90

    @classmethod
    def from_dict(cls, data: dict) -> BucketStats:
        """Deserialize from dictionary."""
        return cls(
            session_count=data.get("session_count", 0),
            session_rate=data.get("session_rate", 0.0),
            duration=data.get("duration", {"p50": 0, "p75": 0, "p90": 0}),
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "session_count": self.session_count,
            "session_rate": self.session_rate,
            "duration": self.duration,
        }


@dataclass
class DayBaseline:
    """Baseline statistics for a single day of the week."""

    boundaries: list[int]  # Hour boundaries, e.g., [6, 12, 18, 22]
    buckets: dict[str, BucketStats]  # bucket_name -> stats

    @classmethod
    def from_dict(cls, data: dict) -> DayBaseline:
        """Deserialize from dictionary."""
        boundaries = data.get("boundaries", [6, 12, 18, 22])
        buckets_data = data.get("buckets", {})
        buckets = {
            name: BucketStats.from_dict(stats) for name, stats in buckets_data.items()
        }
        return cls(boundaries=boundaries, buckets=buckets)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "boundaries": self.boundaries,
            "buckets": {name: stats.to_dict() for name, stats in self.buckets.items()},
        }


@dataclass
class Baseline:
    """Historical baseline statistics."""

    computed_at: datetime
    session_duration_minutes: dict = field(default_factory=dict)
    prompts_per_session: dict = field(default_factory=dict)
    typical_hours: list[int] = field(default_factory=list)
    typical_days: list[str] = field(default_factory=list)
    insufficient_data: bool = False

    # V2 fields for time-bucket baselines
    boundaries_computed_at: datetime | None = None
    window_days: int = 42
    days: dict[str, DayBaseline] | None = None
    global_stats: dict | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Baseline:
        """Deserialize from dictionary."""
        computed_at = datetime.now()
        if "computed_at" in data:
            try:
                computed_at = datetime.fromisoformat(data["computed_at"])
            except (ValueError, TypeError):
                pass

        # Parse boundaries_computed_at if present
        boundaries_computed_at = None
        if "boundaries_computed_at" in data:
            try:
                boundaries_computed_at = datetime.fromisoformat(
                    data["boundaries_computed_at"]
                )
            except (ValueError, TypeError):
                pass

        # Parse days if present
        days = None
        if "days" in data and data["days"]:
            days = {
                day_name: DayBaseline.from_dict(day_data)
                for day_name, day_data in data["days"].items()
            }

        return cls(
            computed_at=computed_at,
            session_duration_minutes=data.get("session_duration_minutes", {}),
            prompts_per_session=data.get("prompts_per_session", {}),
            typical_hours=data.get("typical_hours", []),
            typical_days=data.get("typical_days", []),
            insufficient_data=data.get("insufficient_data", False),
            boundaries_computed_at=boundaries_computed_at,
            window_days=data.get("window_days", 42),
            days=days,
            global_stats=data.get("global_stats"),
        )

    def is_stale(self, max_age_days: int = 14) -> bool:
        """Check if baseline is too old."""
        age = datetime.now() - self.computed_at
        return age > timedelta(days=max_age_days)

    def has_v2_data(self) -> bool:
        """Check if baseline has v2 time-bucket data."""
        return self.days is not None and len(self.days) > 0


def is_baseline_locked() -> bool:
    """Check if baseline lock is held."""
    return get_lock_path().exists()


def acquire_baseline_lock() -> bool:
    """
    Acquire baseline lock.

    Returns:
        True if lock acquired, False if already locked.
    """
    lock_path = get_lock_path()
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    if lock_path.exists():
        return False

    try:
        lock_path.write_text(str(os.getpid()))
        return True
    except OSError:
        return False


def release_baseline_lock() -> None:
    """Release baseline lock."""
    lock_path = get_lock_path()
    try:
        lock_path.unlink(missing_ok=True)
    except OSError:
        pass


def read_baseline() -> Baseline | None:
    """
    Read baseline from file.

    Returns:
        Baseline instance or None if not found.
    """
    path = get_baseline_path()
    if not path.exists():
        return None

    try:
        with open(path) as f:
            data = json.load(f)
        return Baseline.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return None


def write_baseline(data: dict) -> bool:
    """
    Write baseline using atomic write-and-rename.

    Args:
        data: Baseline data dictionary

    Returns:
        True if successful.
    """
    path = get_baseline_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            suffix=".tmp",
            delete=False,
        ) as f:
            json.dump(data, f, indent=2)
            temp_path = Path(f.name)

        temp_path.rename(path)
        return True
    except OSError:
        return False


def read_session_state(session_id: str) -> SessionState | None:
    """
    Read session state from file.

    Args:
        session_id: Session identifier

    Returns:
        SessionState instance or None if not found.
    """
    path = get_session_path(session_id)
    if not path.exists():
        return None

    try:
        with open(path) as f:
            data = json.load(f)
        return SessionState.from_dict(data)
    except (json.JSONDecodeError, OSError):
        return None


def write_session_state(state: SessionState) -> bool:
    """
    Write session state using atomic write-and-rename.

    Args:
        state: Session state to write

    Returns:
        True if successful.
    """
    path = get_session_path(state.session_id)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            suffix=".tmp",
            delete=False,
        ) as f:
            json.dump(state.to_dict(), f, indent=2)
            temp_path = Path(f.name)

        temp_path.rename(path)
        return True
    except OSError:
        return False


def cleanup_old_sessions(max_age_days: int = 7) -> int:
    """
    Remove session files older than max_age_days.

    Args:
        max_age_days: Maximum age in days

    Returns:
        Number of files removed.
    """
    sessions_dir = get_data_dir() / "sessions"
    if not sessions_dir.exists():
        return 0

    removed = 0
    cutoff = datetime.now() - timedelta(days=max_age_days)

    for path in sessions_dir.glob("*.json"):
        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < cutoff:
                path.unlink()
                removed += 1
        except OSError:
            pass

    return removed
