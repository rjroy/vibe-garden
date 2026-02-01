# Plan: mind-reader Plugin Implementation

## Context

- **Spec**: `.lore/specs/mind-reader-plugin.md` (22 requirements)
- **Research**: `.lore/research/session-analysis-and-hooks-prior-art.md`, `.lore/research/typical-hours-algorithm.md`
- **Brainstorm**: `.lore/brainstorm/mind-reader-plugin-2026-01-31.md`

The plugin provides hook-based active feedback via two detection systems:
1. **Temporal**: Session duration, prompt count, unusual hours vs. historical baseline
2. **Sentiment**: VADER analysis on rolling window of prompts

## Approach

Transform the existing `mind-reader/` directory (currently standalone scripts) into a proper vibe-garden plugin following `notify-hook` patterns. The hook reads pre-computed baseline (from daily cron) and maintains per-session state.

**Key decisions:**
- VADER is the only non-stdlib dependency (~1MB)
- Lazy VADER import allows temporal-only fallback if not installed
- Session state files isolated by session ID (no cross-session issues)
- Atomic write-and-rename for session state; .lock file for baseline
- Hook always exits 0 (failures logged to stderr, output `{}`)

## Steps

### Phase 1: Core Infrastructure

1. **Create `scripts/lib/settings.py`**
   - Load/merge settings with defaults
   - Settings dataclass with typed fields

2. **Create `scripts/lib/state.py`**
   - Path utilities for `~/.claude/mind-reader/`
   - Atomic write-and-rename
   - Lock file utilities
   - Session state read/write
   - Baseline read

3. **Create `scripts/lib/__init__.py`**
   - Export public interfaces

### Phase 2: Detection Logic

4. **Create `scripts/lib/temporal.py`**
   - `check_duration_threshold()` - session duration vs p95
   - `check_prompt_threshold()` - prompt count vs p95
   - `check_unusual_hour()` - current hour vs typical_hours
   - Handle `insufficient_data` baseline gracefully

5. **Create `scripts/lib/sentiment.py`**
   - Lazy VADER import (graceful fallback if not installed)
   - `analyze_prompt()` - returns compound score
   - `check_rolling_sentiment()` - rolling average below threshold
   - Cooldown enforcement via `last_nudge_prompt`

### Phase 3: Hook Entry Point

6. **Create `scripts/hook.py`**
   - Read JSON from stdin (user_prompt, session_id)
   - Load settings, baseline, session state
   - Update session state (prompt_count, sentiment_scores)
   - Run temporal checks → run sentiment checks
   - Apply cooldown, emit nudge if triggered
   - Atomic write session state
   - Catch-all exception handler (log stderr, output `{}`, exit 0)
   - Target: <500ms

7. **Create `hooks/hooks.json`**
   - Register UserPromptSubmit hook

### Phase 4: Baseline Computation

8. **Create `scripts/baseline.py`**
   - Read `~/.claude/history.jsonl`
   - Group by sessionId, compute session metrics
   - Calculate percentiles (median, p75, p95)
   - Compute typical_hours (80th percentile)
   - Compute typical_days (at/above median)
   - Check minimum 10 sessions
   - Use .lock file for writes
   - Clean up session files >7 days old

### Phase 5: Plugin Metadata and Skill

9. **Create `.claude-plugin/plugin.json`**
   - Version 1.0.0, author Ronald Roy

10. **Create `skills/init/SKILL.md`**
    - Create directory structure
    - Generate `update-baseline.sh`
    - Run initial baseline computation
    - Output crontab entry for user

### Phase 6: Tests and Documentation

11. **Create tests/**
    - `test_settings.py` - merge logic, defaults
    - `test_state.py` - atomic writes, lock checking
    - `test_temporal.py` - threshold checks with mocked time
    - `test_sentiment.py` - VADER wrapper, rolling window
    - `test_hook.py` - integration with mocked stdin/stdout
    - `test_baseline.py` - baseline computation

12. **Update `pyproject.toml`**
    - Add vaderSentiment as optional dependency
    - Configure pytest

13. **Update `README.md`**
    - Installation, cron setup, configuration

14. **Delete existing scripts** (preprocess.py, topic_model.py, USAGE_REPORT.md)
    - These are replaced by the plugin architecture

## Phase Checkpoints

Each phase must pass its checkpoint before proceeding. No skipping.

### After Phase 1-2 (Core Infrastructure + Detection Logic)
```bash
cd mind-reader && python -c "from lib.settings import load_settings, Settings; from lib.state import read_baseline, read_session_state, write_session_state; from lib.temporal import check_duration_threshold, check_prompt_threshold, check_unusual_hour; from lib.sentiment import analyze_prompt, check_rolling_sentiment; print('All imports OK')"
```
Must print "All imports OK" without errors.

### After Phase 3 (Hook Entry Point)
```bash
cd mind-reader/scripts && echo '{"session_id": "test", "user_prompt": "hello"}' | python hook.py
```
Must output `{}` (empty JSON, no nudge) without crashing.

### After Phase 4 (Baseline Computation)
```bash
cd mind-reader/scripts && python baseline.py --dry-run
```
Must parse history.jsonl and print baseline stats without writing.

### After Phase 6 (Tests)
```bash
cd mind-reader && uv run pytest tests/ -v
```
All tests must pass. Not "tests exist" - tests PASS.

## Final Verification

1. **Unit tests pass**: `uv run pytest tests/ -v`
2. **Coverage**: `uv run pytest --cov=scripts --cov-report=term-missing` (target 90%+)
3. **Hook timing**: Run benchmark to verify <500ms p95
4. **Manual test**:
   - Install plugin via Claude Code
   - Run `/mind-reader:init`
   - Add crontab entry
   - Run baseline script manually
   - Start a session, send prompts
   - Verify nudges appear when thresholds crossed

## AI Validation

**Defaults applied:**
- Unit tests with mocked time/filesystem
- 90%+ coverage on new code
- Code review by fresh-context sub-agent

**Custom (from spec):**
- VADER import tested (graceful failure if not installed)
- Hook timeout test: <500ms with synthetic data
- Session isolation test: two concurrent sessions don't share state
- Settings merge test: partial settings correctly inherits defaults

## Critical Files

**Patterns to follow:**
- `notify-hook/scripts/lib.py` - settings/config loading, merge logic
- `notify-hook/scripts/notify.py` - hook entry point structure
- `notify-hook/hooks/hooks.json` - hook registration format
- `notify-hook/tests/test_lib.py` - unit test patterns

**Files to modify:**
- `mind-reader/` - entire directory restructured as plugin

## Risks

| Risk | Mitigation |
|------|------------|
| Hook exceeds 500ms | Lazy VADER import with caching; benchmark test catches regressions |
| VADER not installed | Graceful fallback to temporal-only; clear install instructions |
| Baseline missing | Temporal checks return None (no nudges); /init guides setup |
