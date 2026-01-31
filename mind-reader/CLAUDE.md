# mind-reader

Active feedback plugin for Claude Code that provides gentle nudges based on session patterns and sentiment analysis.

## Features

- **Temporal detection**: Alerts when sessions exceed your typical duration or prompt count
- **Unusual hours**: Notices when you're working outside your normal hours
- **Sentiment analysis**: Detects frustration patterns using VADER (optional)

## Installation

1. Install the plugin via Claude Code
2. Run `/mind-reader:init` to set up directories and compute initial baseline
3. Add the crontab entry to update baseline daily

## Structure

```
mind-reader/
├── .claude-plugin/
│   └── plugin.json          # Plugin metadata
├── hooks/
│   └── hooks.json            # UserPromptSubmit hook registration
├── scripts/
│   ├── hook.py               # Main hook entry point
│   ├── baseline.py           # Baseline computation script
│   └── lib/
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

Without VADER, only temporal detection works.
