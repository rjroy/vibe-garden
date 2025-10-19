# Courier MCP - Technical Plan

**Specification**: [.sdd/specs/courier-mcp.md](./../specs/courier-mcp.md)
**Version**: 1.1.0
**Status**: Draft
**Created**: 2025-10-18
**Last Updated**: 2025-10-19

## Overview

Courier MCP is a Python-based stdio MCP server that enables Claude Code users to retrieve Gmail messages and export them as markdown files with YAML frontmatter. The implementation will follow the established wyrd-gen-mcp pattern already in the repository, adapting successful architectural decisions to the email-specific domain.

The server will be read-only, stateless, and support concurrent message fetches with exponential backoff for Gmail API rate limiting and a 20-second timeout guarantee for all operations.

**v1.1.0 Updates**: This version adds Claude Code plugin packaging, marketplace integration via the vibe-garden repository, and a setup assistance Skill that automatically activates when authentication failures occur, guiding users through OAuth setup troubleshooting.

## Architecture

### System Context

```
User (Claude Code)
    ↓
Claude Code Plugin System
    ├─→ Marketplace Discovery (vibe-garden)
    ├─→ Setup Skill (courier-setup-helper)
    └─→ MCP Server Integration
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
- **Plugin System**: Via `.claude-plugin/plugin.json` with `${CLAUDE_PLUGIN_ROOT}` variable
- **Marketplace**: Registered in vibe-garden `.claude-plugin/marketplace.json`
- **Setup Skill**: Auto-invoked on authentication errors
- **Configuration**: Environment variables + optional config.yaml for defaults

### Component Overview

```
┌────────────────────────────────────────────────────────────┐
│  Claude Code Plugin (courier-mcp/)                         │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Plugin Manifest (.claude-plugin/plugin.json)         │  │
│  ├─ MCP server command with ${CLAUDE_PLUGIN_ROOT}       │  │
│  └─ Metadata (name, version, author, repository)        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Setup Skill (skills/courier-setup-helper/)           │  │
│  ├─ SKILL.md: Auth troubleshooting instructions         │  │
│  ├─ Auto-invoked on credential/OAuth errors             │  │
│  └─ References: docs/SETUP.md                           │  │
│  └──────────────────────────────────────────────────────┘  │
│                          ↓                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Courier MCP Server (servers/src/courier_mcp/)        │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ Tool Handlers (server.py)                       │ │  │
│  │  ├─ get_messages() - Query + export emails         │ │  │
│  │  └─ get_folders() - List labels with counts        │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                      ↓                               │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ Gmail Service Layer (gmail_service.py)          │ │  │
│  │  ├─ fetch_labels()                                 │ │  │
│  │  ├─ fetch_messages()                               │ │  │
│  │  ├─ fetch_message_detail()                         │ │  │
│  │  └─ with exponential backoff + timeout handling    │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                      ↓                               │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ Markdown Export Layer (export.py)               │ │  │
│  │  ├─ format_message_to_markdown()                   │ │  │
│  │  ├─ generate_filename()                            │ │  │
│  │  ├─ safe_file_write() [collision detection]        │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                      ↓                               │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │ Authentication Layer (auth.py)                  │ │  │
│  │  ├─ load_credentials()                             │ │  │
│  │  ├─ ensure_valid_token()                           │ │  │
│  │  └─ build_gmail_service()                          │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
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

### Decision 10: Plugin Distribution Strategy (v1.1.0)

**Context**: Spec FR-14-16 require Claude Code plugin packaging, marketplace registration, and setup assistance.

**Options Considered**:
- **Standalone MCP Server**: No plugin packaging, manual configuration required
- **Claude Code Plugin with Marketplace** (selected): Discoverable via `/plugin install`, portable via `${CLAUDE_PLUGIN_ROOT}`, integrated setup Skill
- **npm/PyPI Package**: Requires additional packaging infrastructure, doesn't integrate with Claude Code plugin system

**Decision**: Claude Code Plugin with vibe-garden Marketplace Registration
**Rationale**:
- Aligns with existing vibe-garden repository structure (spiral-grove, wyrd-gen-mcp already packaged as plugins)
- `${CLAUDE_PLUGIN_ROOT}` variable ensures plugin portability across installations
- Marketplace registration enables `/plugin install courier-mcp@vibe-garden` for easy discovery
- Plugin manifest provides version management and metadata
- Follows established patterns in wyrd-gen-mcp (same author, same repo structure)
- Setup Skill integration provides better user experience for OAuth troubleshooting

---

### Decision 11: Setup Skill Design (v1.1.0)

**Context**: Spec FR-14-16 require automatic invocation of setup assistance when authentication fails.

**Options Considered**:
- **Static Documentation Only**: User manually reads SETUP.md
- **Error Messages with Links**: Point to docs, but no active guidance
- **Setup Skill with Auto-Invocation** (selected): Skill activates on auth errors, presents contextual troubleshooting

**Decision**: Setup Skill (`courier-setup-helper`) with Progressive Disclosure
**Rationale**:
- Follows spiral-grove-guide pattern: YAML frontmatter for discovery, main content in SKILL.md, reference materials in separate files
- Skill description matches common error patterns: "credential", "authentication", "OAuth", "GMAIL_CREDENTIALS_PATH"
- Claude automatically invokes when error messages match description
- Progressive disclosure: Level 1 (metadata) always loaded, Level 2 (SKILL.md) loaded on trigger, Level 3 (SETUP.md) referenced as needed
- Minimal context overhead (~100 tokens for metadata, ~2-3k for instructions when activated)
- Skill references existing `docs/SETUP.md` rather than duplicating content
- User-friendly: presents step-by-step guidance without leaving Claude conversation

**Skill Structure**:
```
skills/courier-setup-helper/
├── SKILL.md (setup troubleshooting workflow)
└── No additional references (uses ../docs/SETUP.md via relative path)
```

---

### Decision 12: Plugin Portability Strategy (v1.1.0)

**Context**: Plugin must work regardless of installation location for marketplace distribution.

**Options Considered**:
- **Hardcoded Paths**: Breaks when installed via marketplace
- **Relative Paths from CWD**: Unreliable, depends on invocation directory
- **`${CLAUDE_PLUGIN_ROOT}` Environment Variable** (selected): Claude Code sets this automatically, resolves to plugin installation directory

**Decision**: Use `${CLAUDE_PLUGIN_ROOT}` for All Path References
**Rationale**:
- Claude Code automatically sets `${CLAUDE_PLUGIN_ROOT}` to plugin installation directory when invoked via plugin system
- Server startup script path: `${CLAUDE_PLUGIN_ROOT}/servers/scripts/courier.sh`
- Ensures plugin works whether installed locally or via marketplace
- Follows wyrd-gen-mcp precedent (same pattern used successfully)
- No hardcoded paths in `plugin.json`; all paths relative to plugin root
- Enables `/plugin install courier-mcp@vibe-garden` to work out-of-box

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

**Via Plugin Marketplace (Recommended - v1.1.0)**:
1. Add vibe-garden marketplace: `/plugin marketplace add rjroy/vibe-garden`
2. Install plugin: `/plugin install courier-mcp@vibe-garden`
3. Setup Google Cloud project + OAuth credentials (one-time) - guided by setup Skill if errors occur
4. Create `.env` with `GMAIL_CREDENTIALS_PATH=...`
5. Restart Claude Code

**Manual Installation (Development)**:
1. Clone repo or pull updates
2. Create/activate Python venv
3. Install dependencies: `pip install -e .`
4. Setup Google Cloud project + OAuth credentials (one-time)
5. Create `.env` with `GMAIL_CREDENTIALS_PATH=...`
6. Configure Claude Code `.claude/mcp.json`
7. Restart Claude Code

## Plugin Distribution & Setup Skill Design (v1.1.0)

### Plugin Structure

```
courier-mcp/
├── .claude-plugin/
│   └── plugin.json                   # Plugin manifest with metadata
├── skills/
│   └── courier-setup-helper/
│       └── SKILL.md                  # Setup assistance Skill
├── docs/
│   ├── SETUP.md                      # Complete OAuth setup guide
│   └── reference/                    # Technical reference docs
├── servers/
│   ├── scripts/
│   │   └── courier.sh                # MCP server startup script
│   ├── src/courier_mcp/              # Python server implementation
│   ├── setup.py                      # Python package definition
│   └── requirements.txt              # Python dependencies
└── README.md                         # Plugin overview
```

### Plugin Manifest Design

**File**: `.claude-plugin/plugin.json`

```json
{
  "name": "courier-mcp",
  "description": "Provides a MCP which accesses Gmail service for a specific user.",
  "version": "1.1.0",
  "author": {
    "name": "Ronald Roy",
    "email": "gsdwig@gmail.com"
  },
  "repository": "https://github.com/rjroy/vibe-garden.git",
  "license": "MIT",
  "mcpServers": {
    "courier": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/scripts/courier.sh",
      "args": [""]
    }
  }
}
```

**Key Design Decisions**:
- `${CLAUDE_PLUGIN_ROOT}` ensures portability across installation locations
- Version matches spec version (1.1.0)
- MCP server name: "courier" (matches tool namespace)
- Startup script handles venv activation and Python execution

### Marketplace Registration

**File**: `/.claude-plugin/marketplace.json` (vibe-garden root)

Entry for courier-mcp:
```json
{
  "name": "courier-mcp",
  "source": "./courier-mcp",
  "description": "Provides a MCP which accesses Gmail service for a specific user.",
  "repository": "https://github.com/rjroy/vibe-garden.git",
  "license": "MIT"
}
```

**Integration Flow**:
1. User adds marketplace: `/plugin marketplace add rjroy/vibe-garden`
2. User browses plugins: `/plugin` → sees courier-mcp listed
3. User installs: `/plugin install courier-mcp@vibe-garden`
4. Claude Code clones vibe-garden repo, extracts courier-mcp subdirectory
5. Plugin manifest is read, MCP server configured automatically
6. Skills are discovered via YAML frontmatter

### Setup Skill Design

**Purpose**: Automatically assist users when Gmail OAuth setup fails

**File**: `skills/courier-setup-helper/SKILL.md`

**YAML Frontmatter** (Level 1 - always loaded):
```yaml
---
name: courier-setup-helper
description: Assist users when Gmail OAuth setup fails for Courier MCP. Use when authentication errors occur, credentials are missing, or GMAIL_CREDENTIALS_PATH is invalid. Guides through Google Cloud Console setup, OAuth 2.0 credential creation, and troubleshooting.
---
```

**Invocation Triggers** (detected in error messages):
- "credentials not found"
- "GMAIL_CREDENTIALS_PATH"
- "OAuth"
- "authentication failed"
- "invalid_grant"
- "token expired"
- "Permission denied" (Gmail API)

**Skill Content Structure** (Level 2 - loaded when triggered):

```markdown
# Courier MCP Setup Helper

You are assisting a user who encountered an authentication error with Courier MCP.

## Common Error Scenarios

### Error: "GMAIL_CREDENTIALS_PATH not set"
**Cause**: Environment variable missing
**Solution**:
1. Check `.env` file in project root
2. Add: `GMAIL_CREDENTIALS_PATH=/path/to/credentials.json`
3. Restart Claude Code

### Error: "credentials.json not found"
**Cause**: File path incorrect or file doesn't exist
**Solution**:
1. Verify file exists at path specified in GMAIL_CREDENTIALS_PATH
2. If missing, follow OAuth setup steps below

### Error: "invalid_grant" or "Token has expired"
**Cause**: Refresh token invalid or revoked
**Solution**:
1. Delete `token.pickle` file (usually in same directory as credentials.json)
2. Next run will trigger re-authentication flow
3. Browser window will open to grant access again

## First-Time OAuth Setup

For complete setup instructions, see [SETUP.md](../../docs/SETUP.md).

**Quick Start**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Gmail API
3. Create OAuth 2.0 Client ID (Desktop application type)
4. Download credentials.json
5. Set GMAIL_CREDENTIALS_PATH environment variable
6. First run will open browser for authentication

## Troubleshooting Steps

1. **Verify credentials file exists**: `ls -la $GMAIL_CREDENTIALS_PATH`
2. **Check file permissions**: File must be readable
3. **Verify Gmail API is enabled**: Check Google Cloud Console
4. **Check OAuth consent screen**: Must be configured with your email
5. **Try re-authentication**: Delete token.pickle and re-run

## Reference Documentation

- [Complete Setup Guide](../../docs/SETUP.md)
- [Gmail API Scopes](https://developers.google.com/gmail/api/auth/scopes)
- [OAuth 2.0 Troubleshooting](https://developers.google.com/identity/protocols/oauth2/native-app#troubleshooting)

---

After addressing the error, try running the Courier MCP command again.
```

**Progressive Disclosure Strategy**:
- **Level 1** (~100 tokens): Skill metadata loaded at Claude Code startup
- **Level 2** (~2-3k tokens): SKILL.md content loaded when auth error detected
- **Level 3** (0 tokens in context): References SETUP.md via filesystem; Claude reads only if needed

**User Experience Flow**:
1. User installs courier-mcp plugin
2. User attempts to use get-messages tool
3. Authentication error occurs (missing credentials)
4. Claude detects error message matches Skill description
5. Skill is automatically invoked
6. Claude presents relevant troubleshooting section from SKILL.md
7. If more detail needed, Claude reads docs/SETUP.md
8. User follows guidance, resolves issue
9. User retries command successfully

### Setup Skill Testing Strategy

**Test Scenarios**:
1. Missing `GMAIL_CREDENTIALS_PATH` → Skill presents env var setup guidance
2. `credentials.json` not found → Skill presents OAuth setup steps
3. `invalid_grant` error → Skill presents token refresh guidance
4. `Permission denied` (403) → Skill presents scope/API enablement guidance
5. Token expired (401) → Skill presents re-authentication steps

**Acceptance Criteria**:
- Skill automatically invokes when auth errors occur
- Guidance is contextual to specific error type
- User can resolve common issues without external documentation
- Skill does not interfere with normal operation (no false positives)

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

### v1.0.0 Core Implementation
- **Setup & Auth**: 2-3 hours (OAuth flow, credential management)
- **Gmail Service Layer**: 3-4 hours (message fetching, label caching, error handling)
- **Markdown Export**: 2-3 hours (YAML frontmatter, HTML conversion, filename collision detection)
- **Tool Handlers**: 1-2 hours (MCP tool registration, input validation)
- **Timeout & Rate Limit**: 2-3 hours (asyncio, exponential backoff, testing)
- **Testing & Documentation**: 3-4 hours (unit tests, E2E tests, docs)
- **Integration & Polish**: 1-2 hours (final testing, script setup, error messages)

**v1.0.0 Subtotal**: ~16-21 hours (3-4 days full-time)

### v1.1.0 Plugin Distribution & Setup Skill
- **Plugin Manifest & Structure**: 1 hour (plugin.json, directory organization)
- **Marketplace Registration**: 30 minutes (update vibe-garden marketplace.json)
- **Setup Skill Development**: 2-3 hours (SKILL.md creation, error trigger testing, SETUP.md integration)
- **Plugin Portability Testing**: 1-2 hours (test ${CLAUDE_PLUGIN_ROOT}, marketplace installation)
- **Documentation Updates**: 1 hour (README, installation instructions)

**v1.1.0 Subtotal**: ~5-7 hours (1 day full-time)

**Total**: ~21-28 hours (4-5 days full-time)

## Resolved Questions

- [x] **Label IDs vs. Names**: Normalize to label names only. Users discover friendly names via `get_folders` tool; we translate internally. Simpler UX, avoids exposing cryptic label IDs.

- [x] **Attachment URL Validation**: Return URLs as-is from Gmail API. Don't validate accessibility; Gmail URLs are reliable within session and validation adds unnecessary latency. Users discover broken URLs naturally if needed.

- [x] **Label Cache Scope**: Cache all labels (system + custom user labels). Reduces back-and-forth with Gmail API per CLI usage context. Memory cost negligible (~10KB even with hundreds of labels). Improves UX by showing complete folder list.

- [x] **Deleted Messages**: Report in errors array, but frame as informational (likely user action). Include message like "Message ABC was deleted (possibly by another client)" in errors list. Transparent to user without implying implementation error.

- [x] **Thread Support**: Implement flat message list only (per spec). Mark thread/conversation support as **potential future feature** in spec. No threading logic in v1.0; can be added if users request grouped exports in v2.0.

- [x] **Plugin vs. Standalone Distribution** (v1.1.0): Package as Claude Code plugin. Better discoverability via marketplace, consistent with vibe-garden ecosystem (spiral-grove, wyrd-gen-mcp), superior UX with integrated setup Skill.

- [x] **Skill Trigger Reliability** (v1.1.0): Use comprehensive error pattern matching in Skill description. Include common keywords ("credentials", "OAuth", "authentication", "GMAIL_CREDENTIALS_PATH") to ensure Claude invokes Skill on any auth-related error.

- [x] **Skill Content Scope** (v1.1.0): SKILL.md contains common error scenarios + quick fixes; references SETUP.md for complete guide. Balances context efficiency (SKILL.md stays under 3k tokens) with comprehensive coverage (SETUP.md accessible via filesystem).

- [x] **Marketplace vs. Package Manager** (v1.1.0): Register in vibe-garden marketplace only (no npm/PyPI). Simpler distribution, consistent with other vibe-garden plugins, better integration with Claude Code plugin discovery.

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

### Claude Code Plugin Reference (v1.1.0)
- **Location**: `/home/rjroy/Projects/vibe-garden/wyrd-gen-mcp/.claude-plugin/`
- **Patterns to Reuse**:
  - Plugin manifest structure with `${CLAUDE_PLUGIN_ROOT}`
  - MCP server registration in `mcpServers` section
  - Metadata format (name, description, version, author, repository, license)
  - Shell script for server startup (handles venv activation)

### Skill Reference (v1.1.0)
- **Location**: `/home/rjroy/Projects/vibe-garden/spiral-grove/skills/spiral-grove-guide/SKILL.md`
- **Patterns to Reuse**:
  - YAML frontmatter with name and description
  - Description includes trigger keywords for auto-invocation
  - Progressive disclosure: metadata always loaded, content on-demand
  - Reference to external docs via relative filesystem paths
  - Clear structure: Problem → Solution → Reference workflow

---

## Next Phase

Once this plan is approved, proceed to `/task-breakdown` to decompose architecture into implementable tasks with acceptance criteria.

**v1.1.0 Note**: Task breakdown should include:
- v1.0.0 tasks (core MCP server implementation)
- v1.1.0 tasks (plugin packaging, setup Skill, marketplace registration)
- Dependencies between tasks clearly marked (e.g., Skill creation depends on SETUP.md being complete)
