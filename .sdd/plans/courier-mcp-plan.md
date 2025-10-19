# Courier MCP - Technical Plan

**Specification**: [.sdd/specs/courier-mcp.md](./../specs/courier-mcp.md)
**Version**: 1.0.0
**Status**: Approved
**Created**: 2025-10-18
**Last Updated**: 2025-10-18

## Overview

Courier MCP is a Python-based stdio MCP server that enables Claude Code users to retrieve Gmail messages and export them as markdown files with YAML frontmatter. The implementation will follow the established wyrd-gen-mcp pattern already in the repository, adapting successful architectural decisions to the email-specific domain.

The server will be read-only, stateless, and support concurrent message fetches with exponential backoff for Gmail API rate limiting and a 20-second timeout guarantee for all operations.

## Architecture

### System Context

```
User (Claude Code)
    ↓
Courier MCP Server (stdio-based)
    ├─→ Gmail API (REST)
    ├─→ Local File System (markdown export)
    └─→ Environment Config (.env variables)
```

**Integration Points**:
- **Gmail API**: OAuth 2.0 refresh tokens for single user authentication
- **Local FS**: User-specified directory for markdown exports
- **Claude Code**: Via MCP protocol over stdio
- **Configuration**: Environment variables + optional config.yaml for defaults

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│  Courier MCP Server (src/courier_mcp/server.py)        │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Tool Handlers                                       │ │
│  ├─ get_messages() - Query + export emails             │ │
│  └─ get_folders() - List labels with counts            │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Gmail Service Layer (courier_mcp/gmail_service.py) │ │
│  ├─ fetch_labels()                                     │ │
│  ├─ fetch_messages()                                   │ │
│  ├─ fetch_message_detail()                             │ │
│  └─ with exponential backoff + timeout handling        │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Markdown Export Layer (courier_mcp/export.py)      │ │
│  ├─ format_message_to_markdown()                       │ │
│  ├─ generate_filename()                                │ │
│  ├─ safe_file_write() [collision detection]            │ │
│  └─────────────────────────────────────────────────────┘ │
│                          ↓                                │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Authentication Layer (courier_mcp/auth.py)         │ │
│  ├─ load_credentials()                                 │ │
│  ├─ ensure_valid_token()                               │ │
│  └─ build_gmail_service()                              │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

## Technical Decisions

### Decision 1: Language & Framework

**Context**: Courier MCP must follow existing project conventions and integrate with Claude Code workflow.

**Options Considered**:
- **Python** (selected): Matches wyrd-gen-mcp precedent, google-auth libraries are mature, easier Gmail API integration
- **TypeScript/Node.js**: Requires TypeScript google-auth library, less established patterns in repository

**Decision**: Python
**Rationale**: Reuses existing wyrd-gen-mcp infrastructure (project structure, deployment scripts, venv patterns). Google's Python libraries for Gmail API and OAuth are production-grade. Consistency with project conventions reduces onboarding friction.

---

### Decision 2: Authentication Method

**Context**: Spec requires single Gmail account per instance, with credentials stored securely via environment variables.

**Options Considered**:
- **OAuth 2.0 with Refresh Tokens**: User grants access; tokens refresh automatically. Requires initial interactive flow. ✅ User-delegated
- **Service Account**: No user interaction; credentials in JSON file. Less secure for interactive users. ✗ Only for backend servers
- **Legacy App Passwords**: Simpler setup but less secure. ✗ Deprecated by Google

**Decision**: OAuth 2.0 with Refresh Tokens
**Rationale**: Spec FR-7 requires "single Gmail account via OAuth 2.0 with refresh tokens". User delegates access via `GMAIL_CREDENTIALS_PATH` env var pointing to stored credentials.json + optional token.pickle for refresh tokens. Follows established pattern from gmail-api-authentication.md reference material.

---

### Decision 3: Concurrency & Rate Limit Handling

**Context**: Spec requires 20-second timeout, handle rate limits transparently, support up to 100 messages.

**Options Considered**:
- **Sequential Fetching**: Simple, but may exceed 20s under rate limits
- **Concurrent Requests with Asyncio** (selected): Parallel message fetches; exponential backoff for 429 errors; timeout guarantees
- **Request Queuing**: Adds complexity without timeout guarantees

**Decision**: Concurrent Requests with Asyncio + Exponential Backoff
**Rationale**:
- Asyncio allows concurrent gmail.users().messages().get() calls for individual messages
- Exponential backoff: 2^attempt seconds, max 10 attempts (implements spec FR-11)
- Timeout wrapper on all operations (spec FR-12): If timeout reached, return partial results + error list
- Gmail API quota: 250 units/sec per user; batch strategy limits impact

---

### Decision 4: File Export & Collision Handling

**Context**: Spec FR-9 requires markdown with YAML frontmatter; FR-10 requires no overwrites.

**Options Considered**:
- **Timestamp + Sequential Suffixes** (selected): `YYYYMMDD_HHMMSS_[folder]_[sender]_[n].md`
- **UUID suffixes**: Less human-readable
- **Skip existing**: Loses data silently

**Decision**: Timestamp + Sequential ID Suffixes
**Rationale**: Matches spec filename convention and no-overwrite requirement. Easy to track export time and deduplication order. Scales for multiple exports of same query.

---

### Decision 5: Message Body Encoding & Format

**Context**: Spec FR-8 requires markdown export with YAML frontmatter. Gmail API returns base64url-encoded message bodies.

**Options Considered**:
- **HTML to Markdown Conversion** (selected): Use `html2text` or `markdownify` library for rich formatting
- **Plain Text Only**: Loses formatting but simpler
- **Raw MIME**: Overcomplicated for users

**Decision**: HTML to Markdown Conversion
**Rationale**: User-friendly markdown output preserves email structure. Gmail API returns HTML bodies for most messages; converting to markdown ensures portable, readable content. Use `html2text` library (lightweight, well-maintained).

---

### Decision 6: Configuration Management

**Context**: Spec NFR-2 requires config file in repo + env variable overrides (matching wyrd-gen pattern).

**Options Considered**:
- **YAML config.yaml + ENV overrides** (selected): Follows wyrd-gen pattern
- **Dotenv file only**: Less discoverable defaults
- **Hardcoded defaults**: Inflexible

**Decision**: YAML `courier.config` + ENV Variable Overrides
**Rationale**: Spec calls for "config in repo, instance-specific overrides via `.env`". Matches wyrd-gen precedent. Default values in courier.config; env vars override (COURIER_TIMEOUT_SECONDS, COURIER_MAX_RESULTS_DEFAULT, etc.).

---

### Decision 7: Session Caching Strategy

**Context**: Spec NFR-1 states "Cache folder/label list for the duration of the session".

**Options Considered**:
- **In-Memory Cache (TTL-based)** (selected): Fast, sufficient for single-user session
- **Redis/Memcached**: Over-engineered for stdio server
- **No Cache**: Wastes quota on repeated label fetches

**Decision**: In-Memory Cache with 1-Hour TTL
**Rationale**: Single stdio session typically lasts minutes to hours. Cache labels in memory during server lifetime. Refresh on timeout/expiration. Quota savings: labels.list() = 1 quota unit; repeated calls in session avoided.

---

### Decision 8: Error Reporting Strategy

**Context**: Spec FR-13 requires partial results on timeout; tool output must be concise (filenames only in tool output).

**Options Considered**:
- **Partial Results + Error List** (selected): Return files_saved + errors array
- **Fail Fast**: Loses partial progress under rate limits
- **Full Message Bodies in Output**: Bloats context per spec FR-6

**Decision**: Partial Results + Error List
**Rationale**: Tool output includes only filenames + summary (context efficiency). Full email bodies are in exported files. Error array captures transient issues, rate-limit scenarios, deleted messages. Example output:
```json
{
  "files_saved": ["emails/20251018_145032_inbox_from_alice.md"],
  "summary": "Retrieved and exported 1 of 2 messages in 8.5 seconds. 1 message deleted.",
  "errors": ["Message xyz was deleted"]
}
```

---

### Decision 9: Attachment Handling

**Context**: Spec FR-5 requires attachment metadata but explicitly forbids binary download.

**Options Considered**:
- **Metadata Only** (selected): filename, size, MIME type, download URL (no binary)
- **Download & Store**: Violates spec constraint; disk/security issues
- **Remove Attachment Info**: Loses useful metadata

**Decision**: Metadata Only with Optional Download URLs (no validation)
**Rationale**: Frontmatter includes attachment list with metadata. Gmail API `message.payload.parts` provides MIME structure; return URLs as-is without validation. Gmail URLs are reliable within session, and validation adds unnecessary latency. Users can discover broken/expired URLs naturally if needed. Complies with spec constraints.

---

## Data Model

### Gmail Message to Markdown Mapping

**Input** (Gmail API Message object):
```json
{
  "id": "abc123",
  "threadId": "def456",
  "labelIds": ["INBOX", "Label_789"],
  "payload": {
    "headers": [...],
    "mimeType": "text/plain",
    "body": {"data": "base64url..."}
  },
  "internalDate": "1729285200000"
}
```

**Output** (Markdown file):
```yaml
---
from: Alice Johnson <alice@example.com>
to: Me <user@gmail.com>
cc: []
bcc: []
subject: "Q4 Planning"
date: 2025-10-18T14:00:00Z
message-id: <CABcDEF1234@mail.gmail.com>
labels: [INBOX, Project Docs]
attachments:
  - filename: "notes.pdf"
    size: 245678
    mime_type: "application/pdf"
    url: "https://mail.google.com/..."
---

# Email from Alice Johnson

[HTML converted to markdown]
```

### Label/Folder Entity

**Input** (Gmail Label):
```json
{
  "id": "INBOX",
  "name": "Inbox",
  "messageListVisibility": "show",
  "labelListVisibility": "labelShow",
  "messagesTotal": 1245,
  "messagesUnread": 42
}
```

**Output** (API Response):
```json
{
  "id": "INBOX",
  "name": "Inbox",
  "message_count": 1245,
  "unread_count": 42
}
```

## API Design

### Tool 1: `get_messages`

**Input Schema**:
```json
{
  "search_query": "is:unread from:boss@example.com",
  "folder": "INBOX",
  "export_directory": "/path/to/notes/",
  "date_start": "2025-10-01",
  "date_end": "2025-10-18",
  "max_results": 50
}
```

**Processing Flow**:
1. Validate export_directory (create if missing, check write permissions)
2. Normalize folder/label names to IDs (users provide friendly names; we look up IDs via `get_folders` cache)
3. Build Gmail search query (combine search_query + date_start/date_end + label ID)
4. Call gmail.users().messages().list() with maxResults parameter
5. For each message ID, fetch full message with concurrent requests (asyncio)
6. Convert each message to markdown file
7. Handle collisions (append _1, _2, etc.)
8. Return results before timeout expires

**Output Schema**:
```json
{
  "files_saved": ["20251018_145032_inbox_from_alice.md"],
  "summary": "Retrieved and exported 1 message in 2.3 seconds",
  "errors": []
}
```

### Tool 2: `get_folders`

**Input Schema**:
```json
{}
```

**Processing Flow**:
1. Check in-memory cache for labels (TTL check)
2. If expired/empty, call gmail.users().labels().list()
3. Parse results, extract message_count and unread_count
4. Cache in memory
5. Return structured array

**Output Schema**:
```json
{
  "folders": [
    {
      "id": "INBOX",
      "name": "Inbox",
      "message_count": 1245,
      "unread_count": 42
    }
  ]
}
```

## Integration Points

### Internal Systems

**Gmail API** (googleapis python client):
- Endpoint: `users.messages.list()`, `users.messages.get()`, `users.labels.list()`
- Auth: OAuth 2.0 with refresh tokens
- Scopes: `gmail.readonly` (read-only access)
- Rate Limit: 250 quota units/sec per user
- Strategies:
  - Batch message list() calls (avoid per-message overhead where possible)
  - Use `format=metadata` for headers-only fetches when possible
  - Implement exponential backoff on 429 responses
  - Track quota consumption in logs

### External Systems

**None** (intentionally limited to Gmail API per spec constraints)

## State Management

**No persistent state** (stateless stdio server).

**In-Memory Session State**:
- Gmail service instance (authenticated)
- Label cache (dict with TTL): Includes both system labels (INBOX, SENT, DRAFTS, etc.) and all custom user labels to reduce API back-and-forth for CLI usage
- Timeout tracking (start time + deadline)
- Current export operation context

**Per-Request State**:
- Message ID queue
- Partial results (files_saved, errors)
- Concurrent fetch tasks

## Error Handling Strategy

### Validation Errors
- **Invalid export_directory**: Return error, do not create files
- **Invalid search_query syntax**: Gmail API returns 400; catch and report
- **max_results out of range**: Clamp to 1-100

### External Service Failures
- **Gmail API 429 (Rate Limited)**: Exponential backoff, partial results on timeout
- **Gmail API 403 (Permission Denied)**: Return error (likely scope issue)
- **Gmail API 401 (Token Expired)**: Attempt token refresh; if fails, return auth error
- **Gmail API 404 (Message Not Found)**: Skip message, add informational error to errors array (e.g., "Message ABC was deleted (possibly by another client)") to indicate race condition without implying implementation error

### Unexpected Errors
- **Unhandled exceptions**: Log with full traceback, return error JSON
- **File I/O failures**: Catch permission/disk errors, return meaningful message

### Timeout Handling
```python
async def call_with_timeout(coro, timeout_sec):
    try:
        return await asyncio.wait_for(coro, timeout=timeout_sec)
    except asyncio.TimeoutError:
        # Return partial results + timeout error
        return partial_results_so_far
```

## Performance Considerations

### Expected Load
- **Typical**: 10-50 messages per request
- **Peak**: 100 messages (spec limit)
- **Frequency**: 1-5 requests per session (users retrieve emails once, then analyze)
- **Session Duration**: 5-30 minutes

### Optimization Strategy

**Quota Efficiency**:
- Batch list() calls (1 quota unit each, max 100 results per call)
- Use `format=metadata` for headers-only when full body not needed
- Cache labels for session lifetime (avoid repeated 1-quota calls)

**Concurrency**:
- Fetch message details concurrently (asyncio)
- Limit concurrent tasks to 5-10 (balance quota vs. timeout)

**I/O**:
- Write markdown files sequentially (simpler, avoids contention)
- No network delays once messages fetched

### Timeout Budget (20 seconds)
```
Gmail API list call:        ~0.5s
Fetch 100 message details:  ~5-8s (with backoff)
HTML to markdown convert:   ~1-2s
File writes:               ~0.5-1s
Overhead:                  ~1-2s
Contingency:               ~5-7s (rate limit backoff)
```

### Monitoring
- Log API quota consumption per operation
- Track timeout occurrences
- Record concurrent task counts

## Security Design

### Authentication
- **Method**: OAuth 2.0 with refresh tokens
- **Storage**: credentials.json (provided by user, not committed)
- **Token Refresh**: Automatic on expiration
- **Scope**: `gmail.readonly` (minimal required permissions)

### Authorization
- **Single User**: No multi-tenant logic; one Gmail account per server instance
- **Folder Access**: User can only query folders they have access to (Gmail API enforces)

### Data Protection
- **In Transit**: Gmail API uses HTTPS
- **At Rest**: Markdown files stored locally on user's machine
- **Credential Handling**:
  - Never log tokens
  - Credentials path from env var only
  - No credentials in code or git

### Rate Limiting
- Built-in Gmail API limits enforced server-side
- Client-side backoff ensures compliance
- Timeout prevents infinite retries

## Testing Strategy

### Unit Tests
- `test_auth.py`: Token refresh, credential loading
- `test_export.py`: Markdown formatting, filename generation, collision handling
- `test_gmail_service.py`: Message fetching, label parsing (mock Gmail API)

### Integration Tests
- `test_end_to_end.py`:
  - Fetch real messages from test Gmail account
  - Export to temp directory
  - Verify markdown files are valid
  - Check YAML frontmatter parsing

### E2E Tests (Manual)
1. User authenticates with OAuth (credentials.json created)
2. Query inbox: last 5 unread emails
3. Verify files exported to specified directory
4. Verify no overwrites on second export
5. Test rate limiting (retrieve 100 emails, monitor timeout)
6. Verify folder list returns correct counts

### Performance Tests
- Measure 100-message export time (target < 20s)
- Measure label fetch time (target < 1s)
- Measure timeout behavior (simulate slow network)

## Deployment Considerations

### Database Migrations
- **None** (stateless, no persistence)

### Feature Flags
- **None** initially; could add later for experimental features (e.g., thread grouping)

### Rollback Plan
- Each server instance is stateless
- Simply restart with new code
- No data consistency concerns

### Monitoring
- Log file: `courier-mcp.log` (follows wyrd-gen pattern)
- Track in stderr:
  - API rate limit events
  - Timeout occurrences
  - Auth failures

### Deployment Steps
1. Clone repo or pull updates
2. Create/activate Python venv
3. Install dependencies: `pip install -e .`
4. Setup Google Cloud project + OAuth credentials (one-time)
5. Create `.env` with `GMAIL_CREDENTIALS_PATH=...`
6. Configure Claude Code `.claude/mcp.json`
7. Restart Claude Code

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Gmail API rate limit prevents export completion** | Medium | High | Implement exponential backoff (spec FR-11), partial results on timeout, inform user of partial export |
| **OAuth token expires during long export** | Low | Medium | Auto-refresh tokens before expiration, retry on 401 with fresh token |
| **User credentials leak if `.env` committed** | Low | Critical | Document `.gitignore` rule, warn in setup; provide clear security guidance |
| **Message body encoding issues (base64/multipart)** | Medium | Medium | Test with various email types (plain, HTML, multipart); use battle-tested html2text library |
| **File system permissions block export** | Low | Medium | Check write permissions before starting export, provide clear error message |
| **Memory spike with 100 concurrent requests** | Low | Low | Limit concurrent tasks to 5-10, sequential file writes |
| **Export_directory doesn't exist** | Low | Low | Create directory with appropriate permissions, or return error if path invalid |
| **Timeout too aggressive (< 20s real-world)** | Medium | Medium | Configurable via COURIER_TIMEOUT_SECONDS; default 20s, document tuning guidance |

## Dependencies

### Technical Dependencies
- **mcp**: MCP protocol implementation (1.0.0+)
- **google-auth-oauthlib**: OAuth 2.0 library for Gmail API
- **google-auth-httplib2**: HTTP transport for authenticated requests
- **google-api-python-client**: Gmail API client
- **html2text**: HTML to markdown conversion
- **python-dateutil**: Date parsing for spec date formats
- **pyyaml**: YAML frontmatter parsing/generation

### Python Version
- Requires Python 3.10+

### Environment
- Linux, macOS, Windows (cross-platform)
- Requires network access to Gmail API
- Requires local file system write access

### Infrastructure
- No servers/databases required
- Runs locally on user's machine
- Stateless (can restart anytime)

## Timeline Estimate

- **Setup & Auth**: 2-3 hours (OAuth flow, credential management)
- **Gmail Service Layer**: 3-4 hours (message fetching, label caching, error handling)
- **Markdown Export**: 2-3 hours (YAML frontmatter, HTML conversion, filename collision detection)
- **Tool Handlers**: 1-2 hours (MCP tool registration, input validation)
- **Timeout & Rate Limit**: 2-3 hours (asyncio, exponential backoff, testing)
- **Testing & Documentation**: 3-4 hours (unit tests, E2E tests, docs)
- **Integration & Polish**: 1-2 hours (final testing, script setup, error messages)

**Total**: ~16-21 hours (3-4 days full-time)

## Resolved Questions

- [x] **Label IDs vs. Names**: Normalize to label names only. Users discover friendly names via `get_folders` tool; we translate internally. Simpler UX, avoids exposing cryptic label IDs.

- [x] **Attachment URL Validation**: Return URLs as-is from Gmail API. Don't validate accessibility; Gmail URLs are reliable within session and validation adds unnecessary latency. Users discover broken URLs naturally if needed.

- [x] **Label Cache Scope**: Cache all labels (system + custom user labels). Reduces back-and-forth with Gmail API per CLI usage context. Memory cost negligible (~10KB even with hundreds of labels). Improves UX by showing complete folder list.

- [x] **Deleted Messages**: Report in errors array, but frame as informational (likely user action). Include message like "Message ABC was deleted (possibly by another client)" in errors list. Transparent to user without implying implementation error.

- [x] **Thread Support**: Implement flat message list only (per spec). Mark thread/conversation support as **potential future feature** in spec. No threading logic in v1.0; can be added if users request grouped exports in v2.0.

## Appendix: Existing Code Analysis

### wyrd-gen-mcp Reference Implementation
- **Location**: `/home/rjroy/Projects/vibe-garden/wyrd-gen-mcp/servers/src/wyrd_gen_mcp/server.py`
- **Patterns to Reuse**:
  - MCP Server structure: `Server("courier-mcp")` + async handler registration
  - Tool definition with JSON schemas
  - Error handling pattern: try/except with JSON error responses
  - Logging to file with DEBUG level
  - Environment variable validation at startup
  - Stdio transport via `stdio_server()`

### Gmail API Reference Materials
- **Location**: `/home/rjroy/Projects/vibe-garden/seeds/reference/gmail-*.md`
- **Key Findings**:
  - Scope: Use `gmail.readonly` for read-only access
  - Auth: OAuth 2.0 with refresh tokens recommended for users
  - Rate limit: 250 quota units/second per user
  - Methods: `users.messages.list()`, `users.messages.get()`, `users.labels.list()`
  - Payload structure: Headers array + base64url body + MIME parts for attachments

### Project Conventions
- **Config Pattern**: YAML file in repo + ENV variable overrides (matches wyrd-gen)
- **Directory Structure**: `src/[package-name]/`, `tests/`, `docs/reference/`
- **File Naming**: kebab-case for files, snake_case for modules
- **Logging**: File-based logging with DEBUG level
- **Virtual Environment**: Python venv, pip install -e .
- **Scripts**: Shell wrapper script (scripts/courier-mcp.sh) for orchestration

---

## Next Phase

Once this plan is approved, proceed to `/task-breakdown` to decompose architecture into implementable tasks with acceptance criteria.
