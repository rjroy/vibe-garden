# Mind Reader

<img src="logo.webp" align="right" width="128" height="128" alt="Mind Reader Logo">

A Claude Code plugin for active feedback based on session patterns and sentiment analysis.

## Overview

Mind Reader provides gentle nudges when sessions run long, you're working unusual hours, or frustration patterns emerge. It learns your typical usage patterns and alerts when something seems off.

## Features

- **Temporal detection**: Alerts when sessions exceed your typical duration or prompt count
- **Unusual hours**: Notices when you're working outside your normal hours
- **Sentiment analysis**: Detects frustration patterns using VADER (optional)
- **Configurable thresholds**: Tune sensitivity to match your preferences

## Installation

```bash
/plugin install mind-reader@vibe-garden
```

After installation, run the init skill to set up directories and compute your initial baseline:

```bash
/mind-reader:init
```

## Structure

```
mind-reader/
├── .claude-plugin/
│   └── plugin.json           # Plugin metadata
├── hooks/
│   └── hooks.json            # UserPromptSubmit hook registration
├── scripts/
│   ├── hook.py               # Main hook entry point
│   ├── baseline.py           # Baseline computation script
│   └── core/
│       ├── settings.py       # Settings management
│       ├── state.py          # Session state and baseline I/O
│       ├── temporal.py       # Temporal detection logic
│       └── sentiment.py      # VADER sentiment analysis
├── skills/
│   └── init/
│       └── SKILL.md          # Initialization skill
└── tests/
    └── test_*.py             # Unit tests
```

## Data Storage

All data stored in `~/.claude/mind-reader/`:

```
~/.claude/mind-reader/
├── baseline.json         # Computed by cron, read by hooks
├── settings.json         # User-configurable thresholds
└── sessions/
    └── <session-id>.json # Per-session rolling state
```

## Configuration

Edit `~/.claude/mind-reader/settings.json`:

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

### Settings Reference

**Temporal settings:**
- `duration_threshold`: Percentile for session duration alerts (default: p95)
- `prompt_threshold`: Percentile for prompt count alerts (default: p95)
- `check_hours`: Whether to alert for unusual working hours

**Sentiment settings:**
- `window_size`: Number of recent prompts to analyze
- `threshold`: VADER compound score threshold (negative = frustrated)
- `min_prompts`: Minimum prompts before sentiment analysis kicks in
- `cooldown_prompts`: Prompts to wait after an alert before alerting again

## Baseline Updates

The baseline is computed from your Claude Code history. For accurate detection, update it periodically:

```bash
# Manual update
python ~/.claude/plugins/mind-reader/scripts/baseline.py

# Or add to crontab for daily updates
0 3 * * * python ~/.claude/plugins/mind-reader/scripts/baseline.py
```

## Testing

```bash
# Install dev dependencies
uv sync --group dev

# Install sentiment analysis (optional)
uv sync --group sentiment

# Run tests
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=scripts --cov-report=term-missing
```

## Dependencies

- **Core**: Python 3.12+, stdlib only
- **Sentiment** (optional): vaderSentiment (~1MB)

Without VADER installed, only temporal detection works. Sentiment analysis is disabled gracefully.
