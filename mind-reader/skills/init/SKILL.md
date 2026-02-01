---
description: Initialize mind-reader plugin - creates directories, generates baseline script, runs initial computation
user-invocable: true
---

# Initialize mind-reader

Set up the mind-reader plugin for first use.

## Steps

0. **Check and install sentiment analysis (optional)**

Check if vaderSentiment is available:

```bash
python3 -c "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer; print('VADER available')" 2>/dev/null || echo "VADER not installed"
```

If not installed, ask the user if they want sentiment analysis:
- **Yes**: Install vaderSentiment into the plugin's venv:
  ```bash
  cd ${CLAUDE_PLUGIN_ROOT}
  uv sync --group sentiment
  ```
  Then update the hook shebang to use the plugin's Python:
  ```bash
  sed -i "1s|.*|#!${CLAUDE_PLUGIN_ROOT}/.venv/bin/python3|" ${CLAUDE_PLUGIN_ROOT}/scripts/hook.py
  sed -i "1s|.*|#!${CLAUDE_PLUGIN_ROOT}/.venv/bin/python3|" ${CLAUDE_PLUGIN_ROOT}/scripts/baseline.py
  ```
- **No**: Skip. Temporal detection (session duration, prompt count, unusual hours) works without it.

1. **Create directory structure**

Create the mind-reader data directory:

```bash
mkdir -p ~/.claude/mind-reader/sessions
```

2. **Generate update-baseline.sh script**

Create the baseline update script at `~/.claude/mind-reader/update-baseline.sh`:

```bash
#!/bin/bash
# Update mind-reader baseline from Claude Code history
# Run via cron: 0 3 * * * ~/.claude/mind-reader/update-baseline.sh

PLUGIN_CACHE="$HOME/.claude/plugins/cache/vibe-garden/mind-reader"

# Find latest version (sort -V handles semantic versioning)
if [ -d "$PLUGIN_CACHE" ]; then
    LATEST_VERSION=$(ls "$PLUGIN_CACHE" | sort -V | tail -1)
    PLUGIN_ROOT="$PLUGIN_CACHE/$LATEST_VERSION"
else
    echo "Error: Plugin cache not found at $PLUGIN_CACHE" >&2
    exit 1
fi

# Use plugin's venv Python if available, otherwise system python3
if [ -x "$PLUGIN_ROOT/.venv/bin/python3" ]; then
    PYTHON="$PLUGIN_ROOT/.venv/bin/python3"
else
    PYTHON="python3"
fi

"$PYTHON" "$PLUGIN_ROOT/scripts/baseline.py"
```

Make it executable:

```bash
chmod +x ~/.claude/mind-reader/update-baseline.sh
```

3. **Validate history.jsonl**

Check that `~/.claude/history.jsonl` exists and is valid:

```bash
if [ ! -f ~/.claude/history.jsonl ]; then
    echo "Error: ~/.claude/history.jsonl not found."
    echo "Claude Code creates this file automatically when used."
    exit 1
fi

# Check it's valid JSON lines (sample first 10 lines)
head -10 ~/.claude/history.jsonl | while read line; do
    echo "$line" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null || {
        echo "Warning: history.jsonl may contain invalid JSON"
        break
    }
done
```

4. **Run initial baseline computation**

Run the baseline computation script (using the same Python as the hook):

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/baseline.py
```

If fewer than 10 sessions exist, warn the user:
> Your history has fewer than 10 sessions. Baseline statistics may be unreliable. Continue using Claude Code normally and re-run `/mind-reader:init` later for better baseline data.

5. **Create default settings.json**

If `~/.claude/mind-reader/settings.json` doesn't exist, create it with defaults:

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

6. **Output crontab entry**

Display the crontab entry for the user to add manually:

```
Add this line to your crontab (run `crontab -e`):

0 3 * * * ~/.claude/mind-reader/update-baseline.sh >> ~/.claude/mind-reader/cron.log 2>&1

This runs the baseline update daily at 3 AM.
```

## Success Criteria

- `~/.claude/mind-reader/` directory exists with `sessions/` subdirectory
- `update-baseline.sh` is executable
- `baseline.json` exists (even if with `insufficient_data: true`)
- `settings.json` exists with default values
- Crontab entry is displayed for user to add

## Notes

- The plugin does NOT auto-modify crontab (user must add manually)
- Sentiment analysis (VADER) is optional; temporal detection works without it
- If user declines sentiment setup, set `sentiment.enabled: false` in settings.json
- Settings can be customized by editing `~/.claude/mind-reader/settings.json`
