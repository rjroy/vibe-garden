# Notify Hook Plugin - Technical Plan

**Specification**: [notify-hook.md](../.sdd/specs/notify-hook.md)
**Status**: Draft
**Created**: 2025-10-25
**Last Updated**: 2025-10-25

## Overview

The Notify Hook plugin provides desktop/mobile notifications when Claude Code needs user attention. The system hooks into Claude Code's `Notification` event and dispatches sanitized messages to configurable notification backends (ntfy.sh, Discord, Slack) with privacy-first design, rate limiting, and zero-config operation.

**Core architectural principles**:
- **Fire-and-forget async delivery** - Never block Claude Code execution
- **Privacy by default** - Strip sensitive data before transmission
- **Sensible defaults** - Work out-of-box with ntfy.sh, no authentication
- **Configuration hierarchy** - Env vars > repo config > user config > defaults
- **Keep it simple** - Lightweight script (~600 lines), stdlib only, no bloat

## Architecture

### System Context

The plugin integrates with Claude Code's hook system as a `Notification` event handler. When Claude triggers a notification (permission requests, idle timeouts), the hook script processes and forwards the message to external notification services.

```
┌─────────────────┐
│  Claude Code    │
│                 │
│  Notification   │──→ Hook Event (JSON via stdin)
│     Event       │
└─────────────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│  Notify Hook Plugin                     │
│  ┌─────────────────────────────────────┐│
│  │ notify.py (Python script)           ││
│  │  ├─ Config Loader                   ││
│  │  ├─ Message Sanitizer               ││
│  │  ├─ Rate Limiter                    ││
│  │  ├─ Git Repo Detector               ││
│  │  └─ Backend Dispatcher              ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
         │
         ├──→ ntfy.sh (HTTP POST)
         ├──→ Discord (Webhook)
         └──→ Slack (Webhook)
```

### Components

**Simple 4-file architecture** (~600 lines total):

1. **Hook Registration** (`hooks/hooks.json`)
   - Registers for `Notification` events
   - Invokes `scripts/notify.py` with hook input JSON

2. **Main Script** (`scripts/notify.py`, ~200 lines)
   - Entry point invoked by hook
   - Orchestrates: config load → filter → sanitize → rate limit → dispatch
   - Handles all errors gracefully (log and exit 0)

3. **Core Library** (`scripts/lib.py`, ~250 lines)
   - **Config loading**: Hierarchical (env > repo > user > defaults), validation
   - **Message sanitization**: Remove paths, code, error traces; truncate to 100 chars
   - **Message filtering**: Regex include/exclude patterns
   - **Rate limiting**: In-memory timestamp tracking per backend

4. **Backend Dispatchers** (`scripts/backends.py`, ~100 lines)
   - **ntfy.sh**: POST to ntfy.sh with topic, headers, timeout
   - **Discord**: POST to webhook with JSON payload
   - **Slack**: POST to webhook with JSON payload
   - **Orchestration**: Sequential dispatch with error isolation

5. **Git Repository Detector** (`scripts/git.py`, ~50 lines)
   - Extracts git remote URL (HTTPS or SSH format)
   - Parses owner/repo from GitHub URLs
   - Provides fallback topic if not in git repo

## Technical Decisions

### Simplicity Over Abstraction

**Choice**: Keep implementation simple—4 files, ~600 lines, stdlib only

**Rationale**:
- **This is "just a script"**: Not a framework, service, or complex system
- **Fast execution**: Lightweight code executes quickly, meets <2s requirement
- **Easy to maintain**: Single contributor can understand entire codebase
- **No dependency hell**: Stdlib only means no version conflicts, pip install issues
- **Avoid premature optimization**: Don't add complexity for hypothetical future needs

**Explicit anti-patterns to avoid**:
- ❌ Factory patterns, dependency injection, plugin architectures
- ❌ External dependencies (requests, pydantic, etc.)
- ❌ Dataclasses for simple config (plain dicts are fine)
- ❌ Splitting logic across 10+ modules (cohesion > granularity)
- ❌ Persistent state, databases, caching layers

**Target metrics**:
- Total Python code: ≤700 lines (excluding tests)
- External dependencies: 0 (stdlib only)
- Module count: 4 files (notify.py, lib.py, backends.py, git.py)

### Python Over Shell Script

**Choice**: Implement in Python 3.x rather than Bash/shell script

**Rationale**:
- **Structured data handling**: JSON parsing, config management, regex filtering are cleaner in Python
- **Testing**: Unit tests for sanitization, rate limiting, config loading (harder in shell)
- **Error handling**: Robust try/except blocks vs fragile shell error handling
- **Type safety**: Type hints for maintainability
- **Existing pattern**: Courier MCP plugin already uses Python, establishes precedent
- **Async HTTP**: Python `subprocess` with timeout for non-blocking curl calls (or `requests` library if available)

**Trade-off**: Requires Python 3.x in environment (acceptable for Claude Code users)

**Why not use `requests` library**: Stdlib `urllib` or `subprocess + curl` is sufficient for simple HTTP POST. Adding `requests` would violate the "no external dependencies" constraint and add ~50KB of dependencies for functionality we can achieve in ~20 lines of stdlib code.

### Configuration System Design

**Choice**: Hierarchical config (env vars > repo > user > defaults) with JSON format

**Rationale**:
- **Precedence matches user expectations**: Environment variables override files (common in 12-factor apps)
- **Repo-level config**: `.claude/notify-config.json` enables team-wide defaults (e.g., Slack webhook for team channel)
- **User-level config**: `~/.claude/notify-config.json` for personal preferences (e.g., Discord webhook)
- **JSON over YAML**: Simpler parsing (stdlib `json` module), matches hook input format
- **Follows Courier MCP pattern**: Similar 3-tier config (env > file > defaults), proven approach

**Implementation**: Python functions in `lib.py` (~100 lines for config):
- `load_config()` function merging defaults → user file → repo file → env vars
- Returns dict-based config structure (no complex classes)
- Validation inline with config loading
- Keep it simple: avoid over-abstraction (no factory patterns, DI, etc.)

### Message Sanitization Strategy

**Choice**: Regex-based stripping with configurable rules

**Rationale**:
- **Privacy-first**: Default rules remove file paths, code blocks, error traces
- **Configurable**: Users can adjust `strip_paths`, `strip_code` flags
- **Simple implementation**: Regex patterns in Python (no ML/NLP complexity)
- **Max length enforcement**: Hard cap at 100 chars prevents leakage via verbose messages

**Sanitization rules**:
1. Remove absolute paths: `/home/user/...`, `C:\Users\...`
2. Remove relative paths: `src/components/...`, `./file.py`
3. Remove code blocks: ` ```...``` `, inline code
4. Remove error traces: `Traceback`, `at line X`
5. Truncate to 100 chars (configurable via `privacy.max_message_length`)

**Example transformations**:
- Input: `Error in /home/user/project/src/app.py line 42`
- Output: `Error in [path] line 42` (or truncated further)

### Rate Limiting Implementation

**Choice**: In-memory timestamp tracking, no persistence

**Rationale**:
- **Simple**: Dict `{backend_name: last_timestamp}` in memory
- **Sufficient for use case**: Rate limiting per-session (not cross-session)
- **No state file overhead**: Avoids file I/O, locking issues
- **Max 1/min default**: Conservative to prevent spam, configurable

**Trade-off**: Rate limit resets if hook script crashes/restarts (acceptable - rare edge case)

**Implementation**:
```python
# Global state (module-level)
_last_notification_time = {}  # {backend: timestamp}

def should_send_notification(backend: str, rate_limit_seconds: int) -> bool:
    now = time.time()
    last = _last_notification_time.get(backend, 0)
    if now - last < rate_limit_seconds:
        return False
    _last_notification_time[backend] = now
    return True
```

### Git Repository Detection

**Choice**: Shell out to `git remote get-url origin`, parse with regex

**Rationale**:
- **Reliable**: Git CLI is standard in dev environments
- **Handles both HTTPS and SSH**: Regex patterns for `https://github.com/owner/repo.git` and `git@github.com:owner/repo.git`
- **Fallback gracefully**: If git command fails or not in repo, use generic topic `claude-unknown-unknown`
- **Follows existing pattern**: notify.py:20-36 already implements this approach

**Alternative considered**: Parse `.git/config` directly (rejected - fragile, git internals may change)

### Backend Dispatcher Architecture

**Choice**: Sequential dispatch with per-backend timeout, fail-fast logging

**Rationale**:
- **Non-blocking**: Each backend dispatch has 5s timeout (configurable)
- **Parallel not needed**: 2-3 backends max, sequential is fast enough (<1s total)
- **Error isolation**: One backend failure doesn't block others (try/except per backend)
- **Logging over retry**: Log failures but don't retry (keeps hook fast, user can check logs)

**Implementation**:
```python
def dispatch_to_backends(message, config):
    for backend in config.enabled_backends():
        try:
            if backend == 'ntfy':
                send_ntfy(message, config, timeout=5)
            elif backend == 'discord':
                send_discord(message, config, timeout=5)
            elif backend == 'slack':
                send_slack(message, config, timeout=5)
        except Exception as e:
            log_error(f"Backend {backend} failed: {e}")
            # Continue to next backend
```

### Default Backend: ntfy.sh

**Choice**: ntfy.sh as default backend with auto-generated topic

**Rationale**:
- **No authentication**: Public ntfy.sh service requires no API keys
- **Zero config**: Auto-generate topic from git repo (`claude-{owner}-{repo}`)
- **Cross-platform**: Works on desktop (web UI, apps) and mobile (iOS/Android apps)
- **Privacy-preserving**: Topic name is predictable but not guessable (includes repo name)
- **User can subscribe**: User installs ntfy.sh app, subscribes to `claude-{owner}-{repo}` topic

**Topic generation**: `claude-rjroy-vibe-garden` (from `https://github.com/rjroy/vibe-garden.git`)

**Alternative considered**: Desktop notifications (notify-send, osascript) - rejected due to cross-platform complexity

## Data Model

### Configuration Schema

**File**: `.claude/notify-config.json` (repo) or `~/.claude/notify-config.json` (user)

```python
{
  "backends": {
    "ntfy": {
      "enabled": bool,          # Default: true
      "topic": str,             # Default: "claude-{owner}-{repo}"
      "priority": str,          # Default: "default" (ntfy priority levels)
      "tags": list[str]         # Default: ["computer", "claude"]
    },
    "discord": {
      "enabled": bool,          # Default: false
      "webhook_url": str | null # Required if enabled
    },
    "slack": {
      "enabled": bool,          # Default: false
      "webhook_url": str | null # Required if enabled
    }
  },
  "filtering": {
    "exclude_patterns": list[str],  # Default: ["^Debug:", "^Trace:"]
    "include_patterns": list[str]   # Default: [] (empty = allow all)
  },
  "privacy": {
    "max_message_length": int,      # Default: 100
    "strip_paths": bool,            # Default: true
    "strip_code": bool              # Default: true
  },
  "rate_limiting": {
    "enabled": bool,                # Default: true
    "max_per_minute": int           # Default: 1
  }
}
```

### Hook Input Schema

**Source**: Claude Code `Notification` event (see claude-code-hooks.md:333-344)

```python
{
  "session_id": str,
  "transcript_path": str,
  "cwd": str,
  "permission_mode": str,
  "hook_event_name": "Notification",
  "message": str                    # Core data we process
}
```

### Internal Data Structures

**Config structure** (simple dict, no dataclasses for simplicity):
```python
config = {
    "backends": {
        "ntfy": {"enabled": True, "topic": "...", "priority": "default", "tags": [...]},
        "discord": {"enabled": False, "webhook_url": None},
        "slack": {"enabled": False, "webhook_url": None}
    },
    "filtering": {"exclude_patterns": [...], "include_patterns": [...]},
    "privacy": {"max_message_length": 100, "strip_paths": True, "strip_code": True},
    "rate_limiting": {"enabled": True, "max_per_minute": 1}
}
```

**Message flow**:
```python
HookInput (JSON) → lib.load_config() → lib.filter_message() → lib.sanitize_message()
→ lib.check_rate_limit() → backends.dispatch() → HTTP POST
```

## Integration Points

### Claude Code Hook System

- **Event**: `Notification` (no matcher required for this event type)
- **Hook definition**: `hooks/hooks.json` registers `scripts/notify.py` as command
- **Input**: JSON via stdin (session_id, message, cwd, etc.)
- **Output**: Exit code 0 (success), stderr for errors (non-blocking)
- **Environment**: `$CLAUDE_PLUGIN_ROOT` available for referencing plugin scripts

### External Services

1. **ntfy.sh** (default)
   - Endpoint: `https://ntfy.sh/{topic}`
   - Method: POST with body as message text
   - Headers: `Title`, `Priority`, `Tags`
   - No authentication required

2. **Discord** (optional)
   - Endpoint: User-provided webhook URL
   - Method: POST with JSON body `{"content": "message"}`
   - Authentication: Webhook URL contains token

3. **Slack** (optional)
   - Endpoint: User-provided webhook URL
   - Method: POST with JSON body `{"text": "message"}`
   - Authentication: Webhook URL contains token

### File System

- **Config files**: Read from `~/.claude/notify-config.json` and `.claude/notify-config.json`
- **Git repo**: Execute `git remote get-url origin` via subprocess
- **Logging**: Write errors to stderr (captured by Claude Code debug logs)

## Error Handling Strategy

**Principle**: Never block Claude Code execution, log and continue gracefully

### Error Categories

1. **Config errors** (invalid JSON, missing required fields)
   - Load defaults, log warning to stderr
   - Continue with default config

2. **Network errors** (ntfy.sh/Discord/Slack unreachable)
   - Log error to stderr
   - Skip failed backend, continue to next

3. **Git errors** (not in repo, no remote)
   - Use fallback topic `claude-unknown-unknown`
   - Log warning to stderr

4. **JSON parsing errors** (malformed hook input)
   - Log error to stderr
   - Exit 0 (don't block Claude)

### Implementation Pattern

```python
def main():
    try:
        hook_input = json.loads(sys.stdin.read())
        message = hook_input.get("message", "")
    except json.JSONDecodeError as e:
        log_error(f"Invalid hook input: {e}")
        sys.exit(0)  # Exit gracefully, don't block Claude

    try:
        config = load_config()
    except ConfigError as e:
        log_error(f"Config error: {e}, using defaults")
        config = get_default_config()

    try:
        # Filter, sanitize, rate limit, dispatch
        if not should_send(message, config):
            return

        sanitized = sanitize_message(message, config)
        dispatch_to_backends(sanitized, config)
    except Exception as e:
        log_error(f"Unexpected error: {e}")
        # Don't re-raise, exit gracefully

    sys.exit(0)
```

### Exit Codes

- **Exit 0**: Always (success or graceful failure)
- **No exit 2**: Don't block Claude Code (hook output not fed back to Claude)

## Performance Considerations

### Targets

- **Hook execution time**: < 2 seconds total (spec requirement)
- **Network timeout**: 5 seconds per backend (configurable)
- **Async dispatch**: Non-blocking (fire-and-forget)

### Optimization Strategies

1. **Sequential backend dispatch** (not parallel)
   - 2-3 backends max, sequential is fast enough
   - Avoids subprocess complexity, thread safety issues

2. **Timeout enforcement**
   - `subprocess.run(..., timeout=5)` for curl commands
   - Prevents hanging on network issues

3. **No retry logic**
   - Failed notifications are logged but not retried
   - Keeps hook fast, user can monitor logs

4. **Minimal config parsing**
   - Config cached in memory (if module reload supported)
   - Fallback to defaults if config missing

### Async Dispatch Implementation

**Choice**: Use `subprocess.run()` with timeout for curl commands

**Rationale**:
- **No external dependencies**: Works with stdlib only
- **Timeout support**: Built-in timeout parameter
- **Fire-and-forget**: Exit immediately after dispatching all backends
- **Alternative considered**: `requests` library (rejected - requires pip install, overkill for simple HTTP POST)

## Security Considerations

### Privacy Boundaries

**Sensitive data stripping** (see Message Sanitization Strategy):
- File paths removed by default (`privacy.strip_paths: true`)
- Code snippets removed by default (`privacy.strip_code: true`)
- Message truncated to 100 chars (`privacy.max_message_length`)

**Example**:
- Input: `Claude needs permission to write /home/user/project/src/app.py`
- Output: `Claude needs permission to write [path]` (17 chars)

### Webhook URL Security

**Risk**: Webhook URLs in config files may be committed to git, exposing tokens

**Mitigation**:
1. **Documentation warning**: README.md and spec note to use environment variables for webhooks
2. **Recommended pattern**: Store webhooks in env vars (`VIBE_GARDEN_NTFY_DISCORD_WEBHOOK`), not config files
3. **.gitignore guidance**: Suggest adding `.claude/notify-config.json` to `.gitignore` if it contains webhooks

**No automatic enforcement**: Plugin doesn't scan git status (out of scope), relies on user awareness

### Input Validation

**Hook input**: Validate JSON schema before processing
```python
required_fields = ["hook_event_name", "message"]
if not all(field in hook_input for field in required_fields):
    log_error("Missing required fields in hook input")
    sys.exit(0)
```

**Config validation**: Ensure webhook URLs are valid HTTPS URLs (if enabled)
```python
if discord_enabled and not discord_webhook.startswith("https://"):
    log_error("Discord webhook must be HTTPS URL")
    # Disable Discord backend, continue
```

## Testing Strategy

### Unit Testing (Python)

**Test coverage**:
1. **Config loading**: Hierarchy (env > repo > user > defaults), validation
2. **Message sanitization**: Path stripping, code stripping, truncation
3. **Message filtering**: Include/exclude patterns, regex matching
4. **Rate limiting**: Timestamp tracking, cooldown logic
5. **Git repo detection**: HTTPS/SSH URL parsing, fallback logic

**Framework**: `pytest` (standard in Python ecosystem)

**Test structure** (aligned with simplified architecture):
```
notify-hook/
├── scripts/
│   ├── notify.py      (~200 lines)
│   ├── lib.py         (~250 lines)
│   ├── backends.py    (~100 lines)
│   └── git.py         (~50 lines)
├── tests/
│   ├── test_lib.py         (config, sanitization, filtering, rate limiting)
│   ├── test_backends.py    (ntfy, discord, slack dispatchers)
│   ├── test_git.py         (repo detection)
│   ├── test_notify.py      (main script integration)
│   └── test_integration.py (end-to-end scenarios)
└── pyproject.toml (pytest config)
```

**Example test**:
```python
def test_sanitize_removes_file_paths():
    input_msg = "Error in /home/user/project/file.py line 42"
    config = PrivacyConfig(strip_paths=True, max_message_length=100)
    result = sanitize_message(input_msg, config)
    assert "/home/user" not in result
    assert "file.py" not in result  # Path removed
```

### Integration Testing

**Scope**: End-to-end hook execution with mock backends

**Test scenarios**:
1. **Hook receives notification** → dispatches to ntfy.sh (mock HTTP endpoint)
2. **Multi-backend dispatch** → ntfy + Discord + Slack (all mocked)
3. **Rate limiting** → 2 notifications 30s apart, second dropped
4. **Config hierarchy** → env var overrides repo config
5. **Git repo detection** → auto-generates topic from remote URL

**Mock approach**: Python `unittest.mock` for HTTP requests, subprocess calls

### Manual Testing

**Acceptance test checklist** (from spec):
1. Trigger notification in Claude Code → verify ntfy.sh delivery within 2s
2. Check git repo → verify topic is `claude-{owner}-{repo}`
3. Set `VIBE_GARDEN_NTFY_TOPIC=custom` → verify custom topic used
4. Configure Discord webhook → verify multi-backend dispatch
5. Set exclude pattern `^Debug:` → verify Debug messages filtered
6. Send message with file path → verify path stripped

**Test environment**:
- Local Claude Code session
- Test ntfy.sh topic (or local ntfy server)
- ngrok webhook URLs for Discord/Slack (or real test webhooks)

## Validation Strategy

### How Validation Works

**Manual testing approach**:
1. Install plugin locally (test marketplace)
2. Trigger notifications in Claude Code (wait for idle timeout or permission prompt)
3. Verify notifications arrive on ntfy.sh (web UI or mobile app)
4. Check logs for errors (`claude --debug`)

**Evidence of completion**:
- Notification received on ntfy.sh within 2 seconds
- Message content sanitized (no file paths, code snippets)
- Rate limiting works (multiple notifications throttled)
- Config hierarchy respected (env vars override files)

### What Requires Validation

**Critical path**:
1. Hook registration (appears in `/hooks` menu)
2. Notification dispatch to ntfy.sh (default backend)
3. Message sanitization (privacy rules applied)
4. Rate limiting (max 1/min enforced)
5. Git repo detection (topic auto-generated)

**Non-critical** (can defer to post-release):
- Discord/Slack backends (optional features)
- Advanced filtering (edge cases)

### Environment Requirements

**Local development**:
- Claude Code installed
- Python 3.x available
- Git repository with remote configured
- ntfy.sh subscription (mobile app or web)

**No staging/production deployment**: Plugin runs locally, no server-side components

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Network latency blocks Claude** | Medium | High | Enforce 5s timeout per backend, async dispatch |
| **Sensitive data leaked in notifications** | Medium | High | Default sanitization rules, max 100 char limit, privacy config |
| **Webhook URLs committed to git** | Medium | Medium | Documentation warning, recommend env vars, .gitignore guidance |
| **ntfy.sh service unavailable** | Low | Medium | Graceful failure (log error, continue), fallback to other backends |
| **Rate limiting too aggressive** | Low | Low | Configurable `max_per_minute`, default 1 is conservative |
| **Git remote detection fails** | Low | Low | Fallback topic `claude-unknown-unknown`, log warning |
| **Config file conflicts (repo vs user)** | Low | Low | Clear hierarchy (env > repo > user > defaults), documented in README |

**Mitigation strategy for top risk** (network latency):
- Implementation: `subprocess.run(..., timeout=5)` for all HTTP requests
- Testing: Simulate slow network (delay in mock), verify timeout enforced
- Fallback: If timeout exceeded, log error and skip backend

## Dependencies

### Technical Dependencies

- **Python 3.7+**: Type hints, dataclasses (stdlib)
- **Git**: For `git remote get-url origin` command
- **curl** (optional): For HTTP POST to backends (can use Python stdlib `urllib` if curl unavailable)
- **Claude Code**: Plugin system with `Notification` event support

**No external Python packages required** (stdlib only):
- `json` - Config and hook input parsing
- `re` - Regex filtering and sanitization
- `subprocess` - Git commands, curl HTTP requests
- `dataclasses` - Config data structures
- `pathlib` - File path handling

### Team Dependencies

- **User approval**: Plugin must be enabled via `/plugin install`
- **Config setup** (optional): User provides webhook URLs if using Discord/Slack

### Infrastructure Dependencies

- **ntfy.sh service**: Default backend (public, no setup required)
- **Discord/Slack** (optional): User-provided webhook URLs

## Open Questions

- [ ] **Should we support email notifications in v1.0?** (Spec says out of scope, confirm with user)
- [ ] **Should rate limiting be per-backend or global?** (Current design: per-backend, allows 1 ntfy + 1 Discord per minute)
- [ ] **Should we add a `--dry-run` mode for testing config?** (Spec mentions it, not yet designed)
- [ ] **Should webhook URLs be encrypted in config files?** (Adds complexity, user can use env vars instead)
- [ ] **Should we support custom ntfy.sh servers (self-hosted)?** (Easy to add: `ntfy.server_url` config field)
