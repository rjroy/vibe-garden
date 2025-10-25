# Notify Hook Plugin Specification

**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-25
**Last Updated**: 2025-10-25

## Executive Summary
A Claude Code plugin that sends desktop/mobile notifications when Claude needs user attention, enabling users to context-switch away during long-running tasks without missing when input is required.

## User Story
As a Claude Code user performing lengthy tasks, I want to receive notifications when Claude needs my attention or input, so that I can context-switch away without having to watch the screen continuously.

## Stakeholders
- **Primary**: Claude Code users who run long-running operations (builds, tests, multi-file refactors)
- **Secondary**: Teams using Claude Code collaboratively (shared notification channels)
- **Tertiary**: Plugin maintainers (configuration support, backend integrations)

## Success Criteria
1. User receives notification within 2 seconds of Claude triggering a Notification event
2. Notification message contains no sensitive code/data, only high-level status
3. Plugin works out-of-box with ntfy.sh without configuration
4. User can configure custom notification topics/channels via environment variables
5. User can filter notifications using regex patterns to reduce noise
6. Rate limiting prevents notification spam (max 1 per minute)

## Functional Requirements

### Core Notification Handling
- Hook into Claude Code `Notification` event (all notification types)
- Extract notification metadata (message, title, timestamp)
- Sanitize message content to remove sensitive information
- Send notification to configured backend(s)
- Log notification delivery status (success/failure)
- Default notification format: "Claude needs you: [context]" with minimal detail

### Backend Support
- **ntfy.sh** (default, no auth required)
  - Auto-generate topic from git repository (`claude-{owner}-{repo}`)
  - Support custom topic override via configuration
  - Include timestamp, priority tags
- **Discord** (optional, requires webhook URL)
  - Send message to webhook URL
  - Support custom message formatting
- **Slack** (optional, requires webhook URL)
  - Send message to webhook URL
  - Support custom message formatting

### Configuration System
- Support configuration via:
  - Repository-level: `.claude/notify-config.json`
  - User-level: `~/.claude/notify-config.json`
  - Environment variables (highest priority)
- Configuration hierarchy: env vars > repo config > user config > defaults
- Configuration schema includes:
  - Notification backends (ntfy, discord, slack)
  - Topic/channel identifiers
  - Webhook URLs (for Discord/Slack)
  - Message filtering rules (regex patterns)
  - Priority levels

### Message Filtering
- Support regex-based filtering to ignore/allow notifications
- Filter configuration includes:
  - `include_patterns`: Only send if message matches (optional)
  - `exclude_patterns`: Never send if message matches (optional)
- Filtering applied before sending to any backend
- Provide sensible defaults (e.g., exclude overly verbose debug messages)

### Rate Limiting
- Limit notification frequency to max 1 per minute
- Track last notification timestamp per backend
- Drop notifications that exceed rate limit (no queuing)
- Rate limit applied after filtering, before backend delivery

### Git Repository Detection
- Extract git remote URL to determine repository context
- Support both HTTPS and SSH remote formats
- Parse owner and repository name from URL
- Fallback to generic topic if not in git repository or remote not configured

## Non-Functional Requirements

### Security & Privacy
- **No sensitive data in notifications**: Strip code snippets, file paths, error details
- **Message content limit**: Max 100 characters per notification
- **Sanitization rules**:
  - Remove file paths (absolute or relative)
  - Remove code snippets
  - Remove error stack traces
  - Keep only high-level status ("task complete", "input needed")
- **Configuration security**:
  - Webhook URLs stored in config files (not committed to repo)
  - Support `.gitignore` patterns to exclude config files
  - Warn if config files contain URLs and are tracked by git

### Performance
- Notification delivery must not block Claude Code execution
- Send notifications asynchronously (fire-and-forget)
- Timeout for notification delivery: 5 seconds max
- Failed notifications logged but do not halt Claude operation

### Reliability
- Handle network failures gracefully (log and continue)
- Validate configuration on plugin load (warn about invalid settings)
- Support offline mode (skip notifications if network unavailable)

### Usability
- Zero configuration required for basic use (ntfy.sh default)
- Clear error messages for misconfiguration
- Support `--dry-run` mode to test configuration without sending

## Explicit Constraints (DO NOT)

- Do NOT send notification content that includes:
  - Code snippets or diffs
  - File paths or directory structures
  - API keys, tokens, or credentials
  - Error stack traces or debug output
  - User data or business logic
- Do NOT require authentication for default backend (ntfy.sh)
- Do NOT block Claude Code execution while sending notifications
- Do NOT retry failed notifications (log and move on)
- Do NOT support email notifications (out of scope for v1.0)
- Do NOT create UI for configuration management (config files only)

## Technical Context

### Existing Stack
- Python 3.x for notification script
- Claude Code plugin system (hooks, commands, agents)
- Git for repository detection
- ntfy.sh for notification delivery

### Integration Points
- Claude Code `Notification` hook event
- Git CLI for remote URL extraction
- HTTP/HTTPS for notification backend APIs
- File system for configuration loading

### Must Respect
- Claude Code plugin structure (`.claude-plugin/`, `hooks/`, etc.)
- Standard hook configuration format (`hooks.json`)
- Environment variable conventions (`${CLAUDE_PLUGIN_ROOT}`)

## Configuration Schema

### notify-config.json Format
```json
{
  "backends": {
    "ntfy": {
      "enabled": true,
      "topic": "claude-{owner}-{repo}",
      "priority": "default",
      "tags": ["computer", "claude"]
    },
    "discord": {
      "enabled": false,
      "webhook_url": "https://discord.com/api/webhooks/..."
    },
    "slack": {
      "enabled": false,
      "webhook_url": "https://hooks.slack.com/services/..."
    }
  },
  "filtering": {
    "exclude_patterns": [
      "^Debug:",
      "^Trace:"
    ],
    "include_patterns": []
  },
  "privacy": {
    "max_message_length": 100,
    "strip_paths": true,
    "strip_code": true
  },
  "rate_limiting": {
    "enabled": true,
    "max_per_minute": 1
  }
}
```

### Environment Variable Overrides
- `VIBE_GARDEN_NTFY_TOPIC`: Override ntfy.sh topic
- `VIBE_GARDEN_NTFY_DISCORD_WEBHOOK`: Discord webhook URL
- `VIBE_GARDEN_NTFY_SLACK_WEBHOOK`: Slack webhook URL
- `VIBE_GARDEN_NTFY_ENABLED`: Global enable/disable (true/false)

## Acceptance Tests

### Basic Functionality
1. **Given** Claude Code triggers a Notification event with message "Task complete"
   **When** notify-hook processes the event
   **Then** notification is sent to ntfy.sh within 2 seconds
   **And** message format is "Claude needs you: Task complete"

2. **Given** repository has git remote `git@github.com:user/repo.git`
   **When** notify-hook determines topic
   **Then** topic is `claude-user-repo`

3. **Given** user sets `VIBE_GARDEN_NTFY_TOPIC=my-custom-topic`
   **When** notify-hook sends notification
   **Then** notification goes to topic `my-custom-topic`

### Multi-Backend Support
4. **Given** Discord webhook configured and enabled
   **When** notification is triggered
   **Then** notification sent to both ntfy.sh and Discord

5. **Given** Slack webhook configured but disabled in config
   **When** notification is triggered
   **Then** notification NOT sent to Slack

### Message Filtering
6. **Given** exclude pattern `^Debug:` configured
   **When** notification message is "Debug: Processing file"
   **Then** notification is NOT sent

7. **Given** include pattern `^Task` configured
   **When** notification message is "Task complete"
   **Then** notification IS sent
   **When** notification message is "Info: Ready"
   **Then** notification is NOT sent

### Privacy & Security
8. **Given** notification message contains file path `/home/user/project/file.py`
   **When** notify-hook sanitizes message
   **Then** file path is removed or replaced with placeholder

9. **Given** notification message is 150 characters long
   **When** notify-hook sanitizes message
   **Then** message is truncated to 100 characters

### Error Handling
10. **Given** network is unavailable
    **When** notify-hook attempts to send notification
    **Then** error is logged but Claude Code continues normally

11. **Given** invalid webhook URL configured
    **When** plugin loads
    **Then** warning is displayed but plugin loads successfully

### Configuration Hierarchy
12. **Given** topic defined in repo config AND env variable
    **When** notify-hook resolves configuration
    **Then** env variable value takes precedence

### Rate Limiting
13. **Given** two notifications triggered 30 seconds apart
    **When** rate limit is 1 per minute
    **Then** first notification is sent, second is dropped

14. **Given** notification dropped due to rate limit
    **When** checking logs
    **Then** dropped notification is logged with timestamp and reason

## Out of Scope
- Email notification backend (too complex for v1.0)
- UI-based configuration management (use config files)
- Notification history or dashboard
- Two-way communication (reply to notifications)
- Multi-user/team notification routing
- Custom notification sounds or vibration patterns
- Integration with system notification centers (macOS Notification Center, Windows Action Center)
- User activity detection (keyboard/mouse monitoring)
- Custom notification templates per backend
- Notification queuing or retry logic
