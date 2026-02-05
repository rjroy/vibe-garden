---
title: mind-reader plugin
date: 2026-01-31
status: implemented
tags: [plugin, hooks, sentiment-analysis, temporal-patterns, behavioral-feedback]
modules: [mind-reader]
related:
  - .lore/brainstorm/mind-reader/mind-reader-plugin.md
  - .lore/research/session-analysis-and-hooks-prior-art.md
  - .lore/research/typical-hours-algorithm.md
---

# Spec: mind-reader Plugin

## Overview

A Claude Code plugin that provides active feedback during sessions via hooks. Two detection systems: temporal anomalies (session deviates from historical baseline) and sentiment analysis (frustration detection via VADER). Hooks run synchronously; baseline computation happens via daily cron.

## Entry Points

- **Plugin installation**: User installs plugin, runs `/mind-reader:init` to set up cron and initialize baseline
- **Automatic hooks**: Fire on `UserPromptSubmit`, check temporal and sentiment signals
- **Manual suppression**: `/mind-reader:quiet` to disable nudges temporarily [STUB: quiet-mode]

## Requirements

### Plugin Structure

- REQ-1: Plugin lives at `mind-reader/` in vibe-garden repo, replacing existing analysis scripts
- REQ-2: Follows vibe-garden plugin conventions (`.claude-plugin/plugin.json`, `hooks/hooks.json`, `scripts/`, `pyproject.toml`)
- REQ-3: Python scripts with VADER as only non-stdlib dependency (~1MB)

### Data Storage

- REQ-4: All runtime data stored in `~/.claude/mind-reader/`:
  ```
  ~/.claude/mind-reader/
  ├── baseline.json              # Computed by cron, read by hooks
  ├── settings.json              # User-configurable thresholds
  └── sessions/
      └── <session-id>.json      # Per-session rolling state
  ```
- REQ-5: Session ID sourced from `history.jsonl` entry's `sessionId` field
- REQ-6: Session state files cleaned up after 7 days of inactivity (by cron)

### Init Skill

- REQ-7: `/mind-reader:init` skill that:
  1. Creates `~/.claude/mind-reader/` directory structure
  2. Generates `~/.claude/mind-reader/update-baseline.sh` script
  3. Validates `~/.claude/history.jsonl` exists and is parseable
  4. Runs initial baseline computation (warns if <10 sessions)
  5. Outputs crontab entry for user to add (does not auto-modify crontab)
  6. Creates default `settings.json` if not present
- REQ-7a: If history.jsonl missing or corrupt, exits with clear error message

### Temporal Detection

- REQ-8: Hook reads `baseline.json` containing:
  ```json
  {
    "computed_at": "2026-01-31T03:00:00Z",
    "session_duration_minutes": {
      "median": 41,
      "p75": 90,
      "p95": 180
    },
    "prompts_per_session": {
      "median": 5,
      "p75": 12,
      "p95": 30
    },
    "typical_hours": [8, 9, 10, 17, 18, 19, 20],
    "typical_days": ["Saturday", "Sunday", "Monday"]
  }
  ```
  Note: Example values are illustrative; actual values depend on user's history.
- REQ-8a: Baseline is considered stale if `computed_at` is older than 14 days
- REQ-8b: `typical_hours` algorithm: hours in top 20% of activity (80th percentile by prompt count)
- REQ-8c: `typical_days` algorithm: days with prompt count at or above median
- REQ-9: Temporal nudges trigger when:
  - Session duration exceeds `p95` threshold
  - Prompt count exceeds `p95` threshold
  - Current hour outside `typical_hours`
- REQ-10: Nudge messages are baseline-relative: "45 prompts (your p95 is 30)"

### Sentiment Detection

- REQ-11: Hook runs VADER sentiment analysis on each prompt
- REQ-12: Session state tracks rolling window of last N scores (default: 5)
  ```json
  {
    "session_id": "abc123",
    "started_at": "2026-01-31T19:00:00Z",
    "prompt_count": 12,
    "sentiment_scores": [-0.1, 0.2, -0.3, -0.4, -0.2],
    "last_nudge_prompt": null
  }
  ```
- REQ-13: Sentiment nudge triggers when rolling average falls below threshold (default: -0.2) for at least 3 prompts
- REQ-13a: Sentiment nudge message: "Recent prompts suggest frustration (avg: -0.3). Everything okay?"
- REQ-14: Nudge cooldown: no repeated sentiment nudges within 10 prompts (configurable)
- REQ-14a: Session state tracks `last_nudge_prompt` (integer) for cooldown enforcement

### Settings

- REQ-15: `settings.json` schema:
  ```json
  {
    "enabled": true,
    "temporal": {
      "enabled": true,
      "duration_threshold": "p95",
      "prompt_threshold": "p95",
      "check_hours": true
    },
    "sentiment": {
      "enabled": true,
      "window_size": 5,
      "threshold": -0.2,
      "min_prompts": 3,
      "cooldown_prompts": 10
    },
    "quiet_until": null
  }
  ```
  Note: `quiet_until` is ISO 8601 timestamp or null.
- REQ-16: Missing settings file uses defaults; partial settings merged with defaults

### Hooks

- REQ-17: Single `UserPromptSubmit` hook that:
  1. Checks if `enabled` is false or `quiet_until` is in future → skip
  2. Loads baseline.json (skip temporal checks if missing/stale)
  3. Loads or creates session state
  4. Runs temporal checks → emit nudge if triggered
  5. Runs VADER on prompt → update rolling window → emit nudge if triggered
  6. Saves session state
- REQ-17a: Hook output format is JSON to stdout:
  ```json
  {"systemMessage": "45 prompts (your p95 is 30). Long session?"}
  ```
  Empty `{}` if no nudge triggered.
- REQ-18: Hook must complete in <500ms to avoid blocking user interaction
- REQ-19: Hook failures are silent (log to stderr, output `{}` to stdout, exit 0)

### Cron Script

- REQ-20: `update-baseline.sh` reads `~/.claude/history.jsonl` and:
  1. Computes temporal statistics (duration, prompt count distributions)
  2. Identifies typical hours and days (see REQ-8b, REQ-8c for algorithms)
  3. Writes `baseline.json` (using `.lock` file, skip if locked)
  4. Cleans up session files older than 7 days
- REQ-20a: If computation fails, preserve existing baseline.json and log error
- REQ-20b: If <10 sessions in history, write baseline with `insufficient_data: true` flag
- REQ-21: Script is idempotent and handles missing/empty history gracefully
- REQ-22: Recommended cron schedule: daily at 3 AM (`0 3 * * *`)

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Temporal nudge | Session exceeds baseline thresholds | Hook stdout message |
| Sentiment nudge | Rolling sentiment below threshold | Hook stdout message |
| Quiet mode | User runs `/mind-reader:quiet` | [STUB: quiet-mode] |
| Settings edit | User manually edits settings.json | No action needed |

## Success Criteria

- [ ] Plugin installs and `/mind-reader:init` creates directory structure
- [ ] Cron script computes baseline from real history.jsonl
- [ ] Hook fires on UserPromptSubmit without blocking
- [ ] Temporal nudge appears when session exceeds thresholds
- [ ] Sentiment nudge appears when rolling average drops
- [ ] Settings changes take effect without restart
- [ ] Hook completes in <500ms with VADER analysis
- [ ] Parallel sessions use separate state files (no cross-talk)

## AI Validation

**Defaults** (apply unless overridden):
- Unit tests with mocked time/network/filesystem
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom**:
- VADER import tested (graceful failure message if not installed)
- Hook timeout test: verify completion under 500ms with synthetic data
- Session isolation test: two concurrent sessions don't share state
- Settings merge test: partial settings.json correctly inherits defaults

## Constraints

- No network calls from hooks (all data local)
- VADER is the only ML dependency (~1MB); no torch/transformers
- Hook must not crash if baseline.json missing (skip temporal checks)
- Baseline writes use `.lock` file mechanism; if lock held, skip update (not critical)
- Session state uses atomic write-and-rename to prevent corruption
- Plugin must work on Linux and macOS (no Windows-specific paths)
- Minimum 10 sessions required for valid baseline; cron warns if fewer

## Context

This spec draws from:
- [Brainstorm: Promoting mind-reader to a plugin](.lore/brainstorm/mind-reader/mind-reader-plugin.md) - architectural decisions and scope reduction
- [Research: Session analysis and hooks prior art](.lore/research/session-analysis-and-hooks-prior-art.md) - RescueTime's baseline-relative nudges, VADER for sentiment

Key insight from research: "A good feedback loop tells you where you are right now, and allows you to make small changes." Nudges should be baseline-relative, not absolute thresholds.

## Stubs

### [STUB: quiet-mode]

Mechanism to temporarily disable nudges. Options explored in brainstorm:
- `/mind-reader:quiet` skill that sets `quiet_until` in settings
- Duration-based (quiet for 1 hour) or session-based (quiet until session ends)
- Quick toggle vs. explicit duration argument

To be specified separately once core hooks are validated.
