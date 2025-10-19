# Courier MCP Specification

**Version**: 1.0.0
**Status**: Approved
**Created**: 2025-10-18
**Last Updated**: 2025-10-18

## Executive Summary

Courier MCP is a lightweight Model Context Protocol server that enables Claude Code users to access and export Gmail inbox messages as structured markdown files. The tool integrates seamlessly into Claude's workflow, allowing users to perform complex email analysis tasks—summarizing recent messages, filtering by criteria, searching for specific patterns—and automatically saving results to their local file system for further processing and archival.

## User Story

As a Claude Code user leveraging Claude as a note-taking and analysis tool, I want to retrieve emails from my Gmail inbox matching specific criteria (date range, search terms, folders) and automatically export them to my note directory, so that I can analyze, summarize, and organize email content alongside my other research and notes without manually copying emails.

## Stakeholders

- **Primary**: Claude Code users who use Claude for note-taking, research, and analysis
- **Secondary**: Developers building Claude Code workflows that need email context
- **Tertiary**: Team leads managing Claude Code integration strategies

## Success Criteria

1. Users can retrieve up to 100 emails in a single request with arbitrary Gmail search filters
2. All retrieved emails are automatically exported to a user-specified directory as markdown files with YAML frontmatter
3. Export completes within 20 seconds, even under Gmail API rate limiting
4. No emails are ever overwritten; duplicate filenames use `_1`, `_2` suffixes
5. Users can query email across multiple folders (labels) using full Gmail search syntax
6. Tool output is concise (filenames only) to avoid context bloat—message content is in exported files
7. Authentication is managed via environment variables for a single Gmail account
8. All attachment metadata is included; binary content is not downloaded

## Functional Requirements

### Core Email Retrieval
- **FR-1**: Support retrieving messages with up to 100 results per call
- **FR-2**: Support Gmail's full search query syntax (date ranges, sender, subject keywords, labels, etc.)
- **FR-3**: Filter by folder/label (INBOX, SENT, DRAFTS, custom labels, etc.)
- **FR-4**: Export all retrieved messages to a user-specified directory
- **FR-5**: Include attachment metadata (filename, size, MIME type) but not binary content
- **FR-6**: Export format is Markdown with YAML frontmatter

### Folder Discovery
- **FR-7**: Provide a tool to list all available folders/labels with message counts

### Markdown Export Format
- **FR-8**: YAML frontmatter includes: `from`, `to`, `subject`, `date`, `message-id`, `labels`, `attachments` (list)
- **FR-9**: Message body follows frontmatter as markdown-formatted content
- **FR-10**: One file per message, named with timestamp + sequential ID to prevent overwrites

### Rate Limit & Timeout Handling
- **FR-11**: Handle Gmail API rate limits transparently with exponential backoff
- **FR-12**: Enforce maximum 20-second timeout regardless of rate limits or slow responses
- **FR-13**: Return partial results if timeout is reached (save files before timeout)

## Non-Functional Requirements

### Performance
- Target response time: < 20 seconds for up to 100 messages (including export)
  - Configurable via `COURIER_TIMEOUT_SECONDS` environment variable (default: 20)
- Batch API calls to minimize quota consumption
- Cache folder/label list for the duration of the session

### Configuration
- Server stores default configuration in repository (e.g., `config.yaml` or `courier.config`)
- Configuration values can be overridden via environment variables:
  - `COURIER_TIMEOUT_SECONDS`: Request timeout in seconds (default: 20)
  - `COURIER_MAX_RESULTS_DEFAULT`: Default max results per request (default: 10)
  - Any other configurable parameters documented in config file
- Follows pattern used in wyrd-gen-mcp: config in repo, instance-specific overrides via `.env` files

### Security
- **Authentication**: Single Gmail account via OAuth 2.0 with refresh tokens (or Service Account with domain delegation)
- Credentials stored in environment variables (`GMAIL_CREDENTIALS_PATH` or equivalent)
- Never log or expose authentication tokens
- Credentials must be securely stored locally and not committed to version control

### Reliability
- Implement exponential backoff for transient errors (429, 503)
- Retry failed message fetches up to 3 times before reporting error
- Partial export on timeout: save what was retrieved, report which messages failed
- Graceful handling of deleted messages (skip with warning)

### Compatibility
- Runs as a stdio-based MCP server (no long-running HTTP server required)
- Cross-platform support (Linux, macOS, Windows)
- No external service dependencies (all computation local)

## Explicit Constraints (DO NOT)

- Do NOT send emails, create drafts, or modify message state (read-only)
- Do NOT download attachment binaries (metadata only)
- Do NOT support multiple Gmail accounts in a single instance (single user only)
- Do NOT keep raw message content in memory longer than necessary
- Do NOT return full message bodies in tool output (only filenames)
- Do NOT commit credentials to version control
- Do NOT create files without checking for collisions (use `_1`, `_2` suffixes)

## Technical Context

- **Existing Stack**: Gmail API (REST), Python or TypeScript for MCP implementation
- **Integration Points**:
  - Google Cloud project with Gmail API enabled
  - Local file system for markdown export
  - Claude Code environment for tool invocation
- **Auth Method**: OAuth 2.0 with user's own Gmail account (or Service Account for server deployments)
- **Reference Materials**: See `/seeds/reference/gmail-README.md` and related docs for API specifics

## Tool Specifications

### Tool 1: `get-messages`

**Purpose**: Query Gmail inbox, filter by criteria, and export matching messages to a directory.

**Input Schema**:
```json
{
  "search_query": "is:unread from:boss@example.com",
  "folder": "INBOX",
  "export_directory": "/home/user/notes/emails/",
  "date_start": "2025-10-01",
  "date_end": "2025-10-18",
  "max_results": 50
}
```

**Input Parameters**:
- `search_query` (string, optional): Full Gmail search syntax (e.g., `is:unread`, `has:attachment`, `subject:[VOICE]`). Use label names, not IDs (e.g., `label:ProjectDocs`, not `label:Label_789`)
- `folder` (string, optional): Friendly label/folder name (e.g., "INBOX", "Project Docs", "Team Review"); default: "INBOX". Use the names returned by `get-folders` tool
- `export_directory` (string, required): Directory path where markdown files are saved (absolute or relative to invocation directory)
- `date_start` (string, optional): ISO 8601 date (YYYY-MM-DD) or Gmail date query format
- `date_end` (string, optional): ISO 8601 date or Gmail date query format
- `max_results` (integer, optional): 1-100, default from config (via `COURIER_MAX_RESULTS_DEFAULT` env var, default 10)

**Output Schema**:
```json
{
  "files_saved": [
    "emails/20251018_145032_inbox_from_alice.md",
    "emails/20251018_145033_inbox_from_bob.md"
  ],
  "summary": "Retrieved and exported 2 messages in 3.2 seconds",
  "errors": []
}
```

**Output Fields**:
- `files_saved` (array): Relative or absolute paths to saved markdown files
- `summary` (string): Human-readable summary of operation (count, duration, any warnings)
- `errors` (array): List of any non-fatal errors (e.g., "Message ID xyz was deleted", "Rate limited after 45 messages")

**Side Effects**:
- Creates markdown files in `export_directory`
- Skips files that already exist (appends `_1`, `_2`, etc. to prevent overwrites)

---

### Tool 2: `get-folders`

**Purpose**: List available Gmail labels/folders with message counts.

**Input Schema**:
```json
{}
```

**Output Schema**:
```json
{
  "folders": [
    {"id": "INBOX", "name": "Inbox", "message_count": 1245, "unread_count": 42},
    {"id": "SENT", "name": "[Gmail]/Sent Mail", "message_count": 523, "unread_count": 0},
    {"id": "Label_123", "name": "Project Docs", "message_count": 89, "unread_count": 12}
  ]
}
```

**Output Fields**:
- `folders` (array): List of available folders
  - `id` (string): Gmail label ID (used in `get-messages` folder parameter)
  - `name` (string): Human-readable folder name
  - `message_count` (integer): Approximate number of messages in folder
  - `unread_count` (integer): Number of unread messages in folder (if available from API)

---

## Markdown Export Format

**Example exported file** (`emails/20251018_145032_inbox_from_alice.md`):

```markdown
---
from: Alice Johnson <alice@example.com>
to: Me <user@gmail.com>
cc:
  - Bob Smith <bob@example.com>
bcc: []
subject: "Q4 Planning: [VOICE] Meeting Notes"
date: 2025-10-15T14:32:00Z
message-id: <CABcDEF1234567890@mail.gmail.com>
labels:
  - INBOX
  - Project Docs
attachments:
  - filename: "meeting-notes.pdf"
    size: 245678
    mime_type: "application/pdf"
    url: "https://mail.google.com/mail/u/0/?ui=2&ik=xyz&attid=0.1&permmsgid=msg-a:r123&th=abc&view=att&disp=safe"
  - filename: "transcript.txt"
    size: 12345
    mime_type: "text/plain"
    url: "https://mail.google.com/mail/u/0/?ui=2&ik=xyz&attid=0.2&permmsgid=msg-a:r123&th=abc&view=att&disp=safe"
---

# Email from Alice Johnson

Here's the email body in markdown format. Any HTML has been converted to markdown.

**Key Points:**
- Item 1
- Item 2
```

**Frontmatter Fields**:
- `from` (string): Sender email address and display name
- `to` (string): Primary recipient email address
- `cc` (array): List of CC recipients (if any)
- `bcc` (array): List of BCC recipients (if any)
- `subject` (string): Email subject line
- `date` (ISO 8601): Timestamp when email was sent
- `message-id` (string): Unique Gmail message ID
- `labels` (array): List of Gmail labels/folders this message belongs to
- `attachments` (array, optional): List of attachments with metadata
  - `filename` (string): Attachment filename
  - `size` (integer): Size in bytes
  - `mime_type` (string): MIME type
  - `url` (string, optional): Download URL if available from Gmail API (no binary download occurs)

**Filename Convention**:
- Format: `YYYYMMDD_HHMMSS_[folder]_[sender-name].md`
- Example: `20251018_145032_inbox_from_alice.md`
- If file exists, append `_1`, `_2`, etc.: `20251018_145032_inbox_from_alice_1.md`

## Acceptance Tests

1. **Basic retrieval**: User requests last 10 unread emails → 10 markdown files appear in export directory
2. **Search syntax**: User searches `from:boss@company.com subject:[VOICE]` → Returns only matching emails
3. **Date filtering**: User retrieves emails between Oct 1-15 → Only emails in that range are exported
4. **No overwrites**: User exports same query twice → Second export uses `_1`, `_2` suffixes
5. **Rate limit handling**: Retrieve 100 emails → Operation completes within 20 seconds despite rate limits
6. **Attachment metadata**: Exported file includes attachment list with size and MIME type, but no binary
7. **Folder discovery**: `get-folders` returns list of all labels with message counts
8. **Timeout resilience**: If request exceeds 20 seconds, tool returns files saved so far + error message
9. **Context efficiency**: Tool output is concise (filenames only), not full message bodies
10. **Empty results**: Query with no matches → Returns empty `files_saved` array with summary

## Resolved Questions

- [x] **Unread counts**: Include unread count per folder alongside total message count (if easily obtained from API)
- [x] **CC/BCC fields**: Include CC and BCC in YAML frontmatter when available
- [x] **Timeout configurability**: Server has config file in repository; values can be overridden via ENV variables (timeout, max_results defaults, etc.)
- [x] **Path support**: Tool supports both absolute and relative paths; relative paths resolve relative to invocation directory (following wyrd-gen pattern)
- [x] **Attachment URLs**: Include download URLs if Gmail API provides them; fallback to metadata-only if not available (no manual binary downloads)

## Out of Scope

- Sending emails or creating drafts
- Modifying message state (marking read, archiving, deleting)
- Multiple Gmail accounts in single MCP instance
- Downloading attachment binaries
- Real-time sync or polling for new messages
- Integration with external services (Slack, databases, etc.)

## Potential Future Features (v2.0+)

- **Thread/conversation support**: Group related messages by Gmail thread ID; optional `include_thread_context` parameter for grouped exports

---

**Next Phase**: Move to `/plan-generation` to design the technical architecture, authentication flow, and implementation strategy.
