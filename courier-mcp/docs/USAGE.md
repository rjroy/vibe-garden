# Courier MCP - Usage Guide

Detailed examples and usage patterns for Courier MCP tools.

---

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [get-folders Tool](#get-folders-tool)
3. [get-messages Tool](#get-messages-tool)
4. [Search Query Syntax](#search-query-syntax)
5. [Export Directory Handling](#export-directory-handling)
6. [Markdown File Format](#markdown-file-format)
7. [Common Workflows](#common-workflows)
8. [Advanced Usage](#advanced-usage)

---

## Basic Usage

Courier MCP is designed to be used through Claude Code. Simply describe what you want to do, and Claude will use the appropriate tool.

**Example Conversation**:
```
You: Export my last 10 unread emails to /tmp/emails

Claude: I'll export your unread emails for you.
[Uses get-messages tool with search_query="is:unread", max_results=10]

✓ Exported 10 messages in 2.4 seconds:
  - /tmp/emails/20251019_143210_inbox_from_alice.md
  - /tmp/emails/20251019_143211_inbox_from_bob.md
  ...
```

---

## `get-folders` Tool

Lists all available Gmail labels/folders with message counts.

### Usage

```
You: What folders do I have in Gmail?
You: Show me all my Gmail labels
You: List my mailbox folders
```

### Tool Parameters

```json
{
  "tool": "get-folders",
  "arguments": {}
}
```

No parameters required.

### Output Format

```json
{
  "folders": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "message_count": 1245,
      "unread_count": 42
    },
    {
      "id": "SENT",
      "name": "SENT",
      "message_count": 523,
      "unread_count": 0
    },
    {
      "id": "Label_789",
      "name": "Project Docs",
      "message_count": 89,
      "unread_count": 12
    }
  ]
}
```

### Use Cases

1. **Discover available labels** before filtering messages
2. **Check message counts** for specific folders
3. **Verify custom labels** exist before querying

---

## `get-messages` Tool

Queries Gmail and exports matching messages to markdown files.

### Required Parameters

- `export_directory` (string): Path where markdown files will be saved

### Optional Parameters

- `search_query` (string): Gmail search syntax (default: none)
- `folder` (string): Folder/label name (default: "INBOX")
- `date_start` (string): Start date in YYYY-MM-DD format
- `date_end` (string): End date in YYYY-MM-DD format
- `max_results` (integer): 1-100 messages (default: 10)

### Basic Examples

#### Example 1: Last 5 Unread Emails

```
You: Export my last 5 unread emails to ~/notes/emails
```

Tool call:
```json
{
  "tool": "get-messages",
  "arguments": {
    "export_directory": "~/notes/emails",
    "search_query": "is:unread",
    "max_results": 5
  }
}
```

#### Example 2: Emails from Specific Sender

```
You: Export all emails from alice@example.com to /tmp/emails
```

Tool call:
```json
{
  "tool": "get-messages",
  "arguments": {
    "export_directory": "/tmp/emails",
    "search_query": "from:alice@example.com",
    "max_results": 100
  }
}
```

#### Example 3: Date Range Filter

```
You: Export emails from last week to /tmp/weekly-emails
```

Tool call:
```json
{
  "tool": "get-messages",
  "arguments": {
    "export_directory": "/tmp/weekly-emails",
    "date_start": "2025-10-12",
    "date_end": "2025-10-19",
    "max_results": 50
  }
}
```

#### Example 4: Specific Folder

```
You: Export messages from my "Project Docs" folder
```

Tool call:
```json
{
  "tool": "get-messages",
  "arguments": {
    "export_directory": "/tmp/project-emails",
    "folder": "Project Docs",
    "max_results": 50
  }
}
```

### Output Format

```json
{
  "files_saved": [
    "/tmp/emails/20251019_143210_inbox_from_alice.md",
    "/tmp/emails/20251019_143211_inbox_from_bob.md"
  ],
  "summary": "Retrieved and exported 2 messages in 1.3 seconds",
  "errors": []
}
```

With errors (partial results):
```json
{
  "files_saved": [
    "/tmp/emails/20251019_143210_inbox_from_alice.md"
  ],
  "summary": "Retrieved and exported 1 message in 18.2 seconds (1 error)",
  "errors": [
    {
      "message_id": "msg_xyz",
      "error": "Message deleted or unavailable"
    }
  ]
}
```

---

## Search Query Syntax

Courier MCP supports full Gmail search syntax.

### Common Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:alice@example.com` | Emails from specific sender |
| `to:` | `to:bob@example.com` | Emails sent to specific recipient |
| `subject:` | `subject:[URGENT]` | Emails with keyword in subject |
| `is:unread` | `is:unread` | Unread messages only |
| `is:read` | `is:read` | Read messages only |
| `is:starred` | `is:starred` | Starred messages |
| `has:attachment` | `has:attachment` | Messages with attachments |
| `label:` | `label:important` | Messages with specific label |
| `after:` | `after:2025-10-01` | Messages after date |
| `before:` | `before:2025-10-31` | Messages before date |
| `newer_than:` | `newer_than:7d` | Messages newer than 7 days |
| `older_than:` | `older_than:1m` | Messages older than 1 month |

### Combining Queries

Use spaces for AND, `OR` for OR, `-` for NOT:

```
# AND (implicit with spaces)
from:alice@example.com has:attachment

# OR
from:alice@example.com OR from:bob@example.com

# NOT
-from:spam@example.com

# Complex
from:alice@example.com subject:[URGENT] is:unread -has:attachment
```

### Examples

#### Unread from Specific Sender
```
You: Export unread emails from my boss
```
Search query: `from:boss@company.com is:unread`

#### Emails with Specific Subject Tag
```
You: Find all emails with [VOICE] in the subject
```
Search query: `subject:[VOICE]`

#### Recent Urgent Emails
```
You: Export urgent emails from last 3 days
```
Search query: `subject:[URGENT] newer_than:3d`

#### Large Emails with Attachments
```
You: Find emails over 5MB with attachments
```
Search query: `larger:5M has:attachment`

#### Emails from Multiple Senders
```
You: Export emails from Alice or Bob
```
Search query: `from:alice@example.com OR from:bob@example.com`

---

## Export Directory Handling

### Absolute Paths

```json
{
  "export_directory": "/home/user/emails"
}
```

Recommended for scripts and automation.

### Relative Paths

```json
{
  "export_directory": "./emails"
}
```

Relative to current working directory where MCP server was started.

### Home Directory Expansion

```json
{
  "export_directory": "~/notes/emails"
}
```

Expands to user's home directory.

### Directory Creation

If the export directory doesn't exist, it will be created automatically:

```
You: Export to /tmp/new-folder/emails

Claude: ✓ Created directory /tmp/new-folder/emails
✓ Exported 5 messages in 1.8 seconds
```

### Permission Errors

If the directory is not writable, you'll receive an error:

```json
{
  "error": "EXPORT_ERROR",
  "message": "Cannot write to directory /root/emails (permission denied)",
  "guidance": "Choose a different directory or check permissions"
}
```

---

## Markdown File Format

### Filename Convention

Format: `YYYYMMDD_HHMMSS_<folder>_from_<sender>.md`

Examples:
- `20251019_143210_inbox_from_alice-johnson.md`
- `20251019_143211_sent_from_you.md`
- `20251020_091530_project-docs_from_bob-smith.md`

### Collision Prevention

If a file already exists, a suffix is appended:

```
20251019_143210_inbox_from_alice.md       # First export
20251019_143210_inbox_from_alice_1.md     # Second export (same message)
20251019_143210_inbox_from_alice_2.md     # Third export
```

### File Structure

```markdown
---
# YAML Frontmatter (metadata)
from: Alice Johnson <alice@example.com>
to: user@gmail.com
cc:
  - bob@example.com
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
    url: "https://mail.google.com/mail/..."
---

# Email from Alice Johnson

[Markdown-formatted body content]

HTML emails are converted to markdown automatically.
```

### YAML Frontmatter Fields

| Field | Type | Description |
|-------|------|-------------|
| `from` | string | Sender email and display name |
| `to` | string | Primary recipient |
| `cc` | array | CC recipients |
| `bcc` | array | BCC recipients (if available) |
| `subject` | string | Email subject line |
| `date` | ISO 8601 | Timestamp when email was sent |
| `message-id` | string | Unique Gmail message ID |
| `labels` | array | Gmail labels/folders |
| `attachments` | array | Attachment metadata (no binaries) |

### Attachment Metadata

Each attachment includes:
```yaml
attachments:
  - filename: "document.pdf"      # Original filename
    size: 245678                  # Size in bytes
    mime_type: "application/pdf"  # MIME type
    url: "https://mail.google.com/mail/..."  # Download URL (optional)
```

**Note**: Binary content is **not** downloaded. Only metadata is included.

### File Size Limit

Default: 10KB per markdown file (configurable via `COURIER_MAX_FILE_SIZE_KB`).

If a message body exceeds the limit, it will be truncated:

```markdown
---
[Full frontmatter always included]
---

# Email from Sender

[Message body up to limit...]

[Message truncated - exceeded 10KB limit. Full message available in Gmail.]
```

Frontmatter and attachment list are **always** included in full.

---

## Common Workflows

### Workflow 1: Email Research & Summarization

```
You: Find all emails from my team lead about "Q4 planning" and summarize key action items

Claude:
1. [Uses get-messages to export relevant emails]
2. [Reads markdown files]
3. [Summarizes action items from all messages]

✓ Exported 12 messages in 3.1 seconds
✓ Summary of key action items:
  - Budget review due Oct 25
  - Team capacity planning meeting on Oct 28
  - ...
```

### Workflow 2: Weekly Email Digest

```
You: Export all emails from this week and create a digest organized by sender

Claude:
1. [Exports last 7 days of emails]
2. [Groups by sender]
3. [Creates summary markdown]

✓ Exported 45 messages in 8.2 seconds
✓ Created digest in weekly-digest.md
```

### Workflow 3: Project Documentation

```
You: Export all emails labeled "Project Alpha" and extract technical decisions

Claude:
1. [Exports from "Project Alpha" folder]
2. [Analyzes markdown content]
3. [Creates decision log]

✓ Exported 23 messages in 4.5 seconds
✓ Identified 8 technical decisions:
  - API design: REST over GraphQL (Oct 5)
  - Database: PostgreSQL selected (Oct 12)
  - ...
```

### Workflow 4: Attachment Inventory

```
You: Find all emails with PDF attachments from last month and list them

Claude:
1. [Exports with search: has:attachment filename:pdf]
2. [Reads frontmatter from markdown files]
3. [Lists all PDF attachments]

✓ Exported 18 messages in 5.1 seconds
✓ Found 24 PDF attachments:
  - meeting-notes-oct-5.pdf (245KB)
  - budget-proposal.pdf (1.2MB)
  - ...
```

---

## Advanced Usage

### Custom Configuration

Override defaults with environment variables:

```bash
# Increase timeout for large exports
export COURIER_TIMEOUT_SECONDS=60

# Increase default max results
export COURIER_MAX_RESULTS_DEFAULT=50

# Increase file size limit
export COURIER_MAX_FILE_SIZE_KB=50
```

### Batch Exports

Export multiple queries:

```
You: Export three sets of emails:
1. Unread from inbox to /tmp/unread
2. Starred to /tmp/starred
3. Last week's sent mail to /tmp/sent

Claude:
[Runs three separate get-messages tool calls]

✓ Batch 1: Exported 12 unread messages
✓ Batch 2: Exported 5 starred messages
✓ Batch 3: Exported 34 sent messages
```

### Quota Management

Monitor quota usage in logs:

```
2025-10-19 14:32:10 - INFO - Label fetch: 1 quota units
2025-10-19 14:32:12 - INFO - Message list: 1 quota units
2025-10-19 14:32:15 - INFO - Fetched 10 message details: ~50 quota units
```

**Gmail API Free Tier**: 250 quota units/second/user (more than sufficient).

### Performance Optimization

For large exports:

1. **Use date filters** to reduce result set
2. **Export in batches** (e.g., 100 at a time)
3. **Increase timeout** if needed (`COURIER_TIMEOUT_SECONDS`)
4. **Monitor rate limits** in logs

Example:
```
You: Export all 500 emails from October in batches

Claude:
[Runs 5 separate exports: Oct 1-6, Oct 7-12, etc.]

✓ Batch 1: 100 messages in 18.2s
✓ Batch 2: 100 messages in 17.8s
✓ Batch 3: 100 messages in 19.1s
✓ Batch 4: 100 messages in 16.5s
✓ Batch 5: 100 messages in 18.9s
Total: 500 messages in 90.5s
```

---

## Tips & Best Practices

### 1. Use Specific Searches

❌ **Don't**: Export entire inbox
```json
{"export_directory": "/tmp", "max_results": 100}
```

✅ **Do**: Use targeted searches
```json
{
  "export_directory": "/tmp/work-emails",
  "search_query": "from:work.com newer_than:7d",
  "max_results": 50
}
```

### 2. Organize Exports by Purpose

```
/tmp/
  emails/
    unread/           # Unread messages
    urgent/           # Urgent messages
    attachments/      # Messages with attachments
    weekly-digest/    # Weekly summaries
```

### 3. Check Folders First

Before exporting, use `get-folders` to see available labels:

```
You: What labels do I have?

Claude: [Shows all labels]

You: Export from "Project Alpha" label
```

### 4. Handle Timeouts Gracefully

If a request times out, partial results are still saved:

```json
{
  "error": "TIMEOUT",
  "files_saved": [/* 23 files exported before timeout */],
  "summary": "Exported 23 messages before 20s timeout"
}
```

You can then continue with remaining messages:
```
You: Resume from message 24
```

### 5. Validate Exports

Check export success by reviewing the summary:

```json
{
  "files_saved": [...],  // Should match expected count
  "summary": "...",
  "errors": []          // Should be empty
}
```

---

## Error Messages

Common errors and their meanings:

| Error Code | Message | Cause |
|------------|---------|-------|
| `AUTH_ERROR` | "Invalid credentials" | OAuth setup issue |
| `INVALID_INPUT` | "export_directory is required" | Missing required parameter |
| `EXPORT_ERROR` | "Cannot write to directory" | Permission denied |
| `TIMEOUT` | "Operation exceeded 20s timeout" | Request took too long |
| `RATE_LIMITED` | "Gmail API quota exhausted" | Too many requests |

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for solutions.

---

## Next Steps

- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Fix common issues
- **[API Reference](API.md)** - Full tool specifications
- **[Setup Guide](SETUP.md)** - OAuth configuration
- **[E2E Test Results](E2E_TEST_RESULTS.md)** - Performance metrics

---

**Happy exporting! 📬**
