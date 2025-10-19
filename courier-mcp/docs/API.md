# Courier MCP - API Reference

Complete tool specifications, input/output schemas, and error responses.

---

## MCP Server Information

**Server Name**: `courier-mcp`
**Version**: 1.1.0
**Protocol**: stdio-based Model Context Protocol
**Tools**: 2 (get-folders, get-messages)

---

## Tool 1: `get-folders`

List all available Gmail labels/folders with message counts.

### Input Schema

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

No parameters required.

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "folders": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string", "description": "Gmail label ID" },
          "name": { "type": "string", "description": "Human-readable folder name" },
          "message_count": { "type": "integer", "description": "Total messages in folder" },
          "unread_count": { "type": "integer", "description": "Unread messages in folder" }
        },
        "required": ["id", "name", "message_count", "unread_count"]
      }
    }
  },
  "required": ["folders"]
}
```

### Example Response

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

### Performance

- **Response Time**: < 1 second (cached after first call)
- **Cache TTL**: 1 hour (configurable via `COURIER_LABEL_CACHE_TTL_SECONDS`)
- **API Quota**: 1 quota unit per call

### Error Responses

```json
{
  "error": "AUTH_ERROR",
  "message": "Failed to authenticate with Gmail API",
  "details": {
    "type": "AuthenticationError",
    "guidance": "Check GMAIL_CREDENTIALS_PATH and re-authenticate"
  }
}
```

---

## Tool 2: `get-messages`

Query Gmail inbox, filter by criteria, and export matching messages to directory as markdown files.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "export_directory": {
      "type": "string",
      "description": "Directory path where markdown files will be saved (absolute or relative)"
    },
    "search_query": {
      "type": "string",
      "description": "Gmail search query syntax (e.g., 'is:unread from:boss@example.com')"
    },
    "folder": {
      "type": "string",
      "description": "Friendly folder/label name (e.g., 'INBOX', 'Project Docs'). Get list from get-folders tool."
    },
    "date_start": {
      "type": "string",
      "description": "Start date in YYYY-MM-DD format (optional)"
    },
    "date_end": {
      "type": "string",
      "description": "End date in YYYY-MM-DD format (optional)"
    },
    "max_results": {
      "type": "integer",
      "description": "Maximum messages to retrieve (1-100, default from config)",
      "minimum": 1,
      "maximum": 100
    }
  },
  "required": ["export_directory"]
}
```

### Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `export_directory` | string | ✅ Yes | - | Path to save markdown files (absolute or relative) |
| `search_query` | string | No | `""` | Gmail search syntax (e.g., `"is:unread"`) |
| `folder` | string | No | `"INBOX"` | Folder/label name (friendly name, not ID) |
| `date_start` | string | No | `null` | Start date (YYYY-MM-DD) |
| `date_end` | string | No | `null` | End date (YYYY-MM-DD) |
| `max_results` | integer | No | `10` | Max messages (1-100, from config) |

### Output Schema

```json
{
  "type": "object",
  "properties": {
    "files_saved": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of file paths where messages were saved"
    },
    "summary": {
      "type": "string",
      "description": "Human-readable summary (count, duration, warnings)"
    },
    "errors": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "message_id": { "type": "string" },
          "error": { "type": "string" }
        }
      },
      "description": "Non-fatal errors encountered during export"
    }
  },
  "required": ["files_saved", "summary", "errors"]
}
```

### Example Response (Success)

```json
{
  "files_saved": [
    "/tmp/emails/20251019_143210_inbox_from_alice-johnson.md",
    "/tmp/emails/20251019_143211_inbox_from_bob-smith.md"
  ],
  "summary": "Retrieved and exported 2 messages in 1.3 seconds",
  "errors": []
}
```

### Example Response (With Errors)

```json
{
  "files_saved": [
    "/tmp/emails/20251019_143210_inbox_from_alice-johnson.md"
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

### Performance

- **10 messages**: < 2 seconds
- **50 messages**: < 10 seconds
- **100 messages**: < 20 seconds
- **Timeout**: 20 seconds (configurable via `COURIER_TIMEOUT_SECONDS`)
- **API Quota**: ~1 unit for list + ~5 units per message detail

### Error Responses

#### Missing Required Parameter

```json
{
  "error": "INVALID_INPUT",
  "message": "export_directory is required",
  "details": {
    "parameter": "export_directory",
    "guidance": "Provide a valid directory path"
  }
}
```

#### Export Directory Permission Denied

```json
{
  "error": "EXPORT_ERROR",
  "message": "Cannot write to directory /root/emails (permission denied)",
  "details": {
    "type": "PermissionError",
    "guidance": "Choose a different directory or check permissions"
  }
}
```

#### Timeout Exceeded

```json
{
  "error": "TIMEOUT",
  "message": "Operation exceeded 20s timeout",
  "details": {
    "timeout_seconds": 20
  },
  "files_saved": [/* partial results */],
  "summary": "Exported 23 messages before timeout"
}
```

#### Authentication Failure

```json
{
  "error": "AUTH_ERROR",
  "message": "Failed to authenticate with Gmail API",
  "details": {
    "type": "AuthenticationError",
    "guidance": "Check GMAIL_CREDENTIALS_PATH and re-authenticate"
  }
}
```

#### Rate Limit (429)

**Note**: Rate limits are handled transparently with exponential backoff. Users should not see this error under normal circumstances.

If backoff fails after max retries:
```json
{
  "error": "RATE_LIMITED",
  "message": "Gmail API quota exhausted after 3 retry attempts",
  "details": {
    "retry_attempts": 3,
    "guidance": "Wait a few minutes and try again"
  }
}
```

---

## Error Codes

| Code | Description | Retry? | User Action |
|------|-------------|--------|-------------|
| `AUTH_ERROR` | Authentication failed | No | Check credentials, re-authenticate |
| `INVALID_INPUT` | Missing or invalid parameter | No | Fix parameter and retry |
| `EXPORT_ERROR` | File write failure | No | Check directory permissions |
| `TIMEOUT` | Operation exceeded time limit | Yes | Reduce max_results or increase timeout |
| `RATE_LIMITED` | API quota exhausted | Yes | Wait and retry (rare, handled automatically) |
| `INTERNAL_ERROR` | Unexpected server error | No | Check logs, report bug |

---

## Common Error Patterns

### Configuration Not Loaded

```json
{
  "error": "INTERNAL_ERROR",
  "message": "Configuration not yet loaded. Call load_config() first.",
  "details": {
    "type": "RuntimeError",
    "guidance": "Restart MCP server"
  }
}
```

**Solution**: Restart the MCP server. This should not occur after bug fix in v1.1.0.

### Credentials Not Found

```json
{
  "error": "AUTH_ERROR",
  "message": "GMAIL_CREDENTIALS_PATH environment variable not set",
  "details": {
    "guidance": "Set GMAIL_CREDENTIALS_PATH to your credentials.json path"
  }
}
```

**Solution**: Set environment variable and restart.

### Invalid Token

```json
{
  "error": "AUTH_ERROR",
  "message": "Token expired or invalid",
  "details": {
    "type": "google.auth.exceptions.RefreshError",
    "guidance": "Delete token.pickle and re-authenticate"
  }
}
```

**Solution**: Delete `token.pickle` file and re-authenticate via OAuth flow.

---

## Gmail Search Syntax Reference

Full Gmail search syntax is supported in `search_query` parameter.

### Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:alice@example.com` | Sender email |
| `to:` | `to:bob@example.com` | Recipient email |
| `subject:` | `subject:[URGENT]` | Subject keyword |
| `label:` | `label:important` | Gmail label |
| `is:unread` | `is:unread` | Unread status |
| `is:read` | `is:read` | Read status |
| `is:starred` | `is:starred` | Starred |
| `has:attachment` | `has:attachment` | Has attachments |
| `after:` | `after:2025-10-01` | Date after |
| `before:` | `before:2025-10-31` | Date before |
| `newer_than:` | `newer_than:7d` | Relative date (days) |
| `older_than:` | `older_than:1m` | Relative date (months) |
| `larger:` | `larger:5M` | Size larger than |
| `smaller:` | `smaller:1M` | Size smaller than |

### Combining Operators

- **AND**: Use spaces (implicit)
  ```
  from:alice@example.com is:unread
  ```

- **OR**: Use `OR` keyword
  ```
  from:alice@example.com OR from:bob@example.com
  ```

- **NOT**: Use `-` prefix
  ```
  -from:spam@example.com
  ```

- **Grouping**: Use parentheses
  ```
  (from:alice@example.com OR from:bob@example.com) is:unread
  ```

### Examples

```
# Recent unread from boss
from:boss@company.com is:unread newer_than:7d

# Urgent emails with attachments
subject:[URGENT] has:attachment

# Large emails from last month
larger:5M after:2025-09-01 before:2025-09-30

# Specific label, not spam
label:"Project Alpha" -is:spam
```

---

## Markdown Export Format

See [USAGE.md - Markdown File Format](USAGE.md#markdown-file-format) for complete details.

### Filename Convention

```
YYYYMMDD_HHMMSS_<folder>_from_<sender>.md
```

Examples:
- `20251019_143210_inbox_from_alice-johnson.md`
- `20251020_091530_project-docs_from_bob-smith.md`

### YAML Frontmatter Fields

| Field | Type | Example | Description |
|-------|------|---------|-------------|
| `from` | string | `"Alice <alice@example.com>"` | Sender |
| `to` | string | `"user@gmail.com"` | Primary recipient |
| `cc` | array | `["bob@example.com"]` | CC recipients |
| `bcc` | array | `[]` | BCC recipients |
| `subject` | string | `"Meeting Notes"` | Subject line |
| `date` | ISO 8601 | `"2025-10-15T14:32:00Z"` | Sent timestamp |
| `message-id` | string | `"<CAB...@mail.gmail.com>"` | Gmail message ID |
| `labels` | array | `["INBOX", "Project Docs"]` | Gmail labels |
| `attachments` | array | See below | Attachment metadata |

### Attachment Metadata Schema

```yaml
attachments:
  - filename: "document.pdf"
    size: 245678                    # Bytes
    mime_type: "application/pdf"
    url: "https://mail.google.com/mail/..."  # Optional
```

---

## Configuration Reference

### courier.config (YAML)

```yaml
# Timeout and Performance
COURIER_TIMEOUT_SECONDS: 20             # Max operation time (seconds)
COURIER_MAX_RESULTS_DEFAULT: 10         # Default max messages per request

# File Export
COURIER_MAX_FILE_SIZE_KB: 10            # Max markdown file size (KB)

# Network Resilience
COURIER_NETWORK_RETRY_ATTEMPTS: 3       # Retry count for transient errors
COURIER_NETWORK_RETRY_BACKOFF_FACTOR: 2 # Exponential backoff multiplier

# Caching
COURIER_LABEL_CACHE_TTL_SECONDS: 3600   # Label cache duration (1 hour)

# Logging
COURIER_LOG_PATH: "./courier-mcp.log"   # Log file path
COURIER_LOG_LEVEL: "DEBUG"              # DEBUG | INFO | WARNING | ERROR | CRITICAL

# Gmail API
GMAIL_API_QUOTA_UNITS_PER_SECOND: 250   # Free tier quota limit
```

### Environment Variable Overrides

All config values can be overridden with environment variables:

```bash
export COURIER_TIMEOUT_SECONDS=30
export COURIER_MAX_RESULTS_DEFAULT=50
export COURIER_MAX_FILE_SIZE_KB=50
export COURIER_LOG_LEVEL=INFO
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
```

---

## Rate Limiting & Quotas

### Gmail API Quota

**Free Tier**: 250 quota units/second/user

**Quota Consumption**:
- `users.labels.list()`: 1 unit (cached for 1 hour)
- `users.messages.list()`: 1 unit per call
- `users.messages.get()`: ~5 units per message (estimate)

**Example Calculation** (100-message export):
- Label list: 1 unit (cached)
- Message list: 1 unit (pagination handled)
- Message details: 100 × 5 = 500 units
- **Total**: ~502 units in <20 seconds (~25 units/second)

Well within free tier limits (250 units/second).

### Rate Limit Handling

**Automatic Exponential Backoff**:
- Initial request → 429 response
- Wait 2^1 = 2 seconds, retry
- Still rate limited → wait 2^2 = 4 seconds, retry
- Still rate limited → wait 2^3 = 8 seconds, retry
- Max retries: 3 (configurable via `COURIER_NETWORK_RETRY_ATTEMPTS`)

**Transparent to Users**: Rate limiting is handled automatically. Users only see errors if max retries exhausted (rare).

---

## Performance Characteristics

| Operation | Target | Typical | Notes |
|-----------|--------|---------|-------|
| Label fetch | < 1s | ~200ms | Cached after first call |
| 10-message export | < 2s | ~1.5s | Network dependent |
| 50-message export | < 10s | ~8s | Concurrent fetching (5 tasks) |
| 100-message export | < 20s | ~17s | May hit rate limits (transparent) |
| Server startup | < 3s | ~1s | Config + auth initialization |

**Variables Affecting Performance**:
- Network latency
- Gmail API response time
- Message size (larger emails take longer)
- Attachment count (more metadata to parse)
- Rate limiting (transparent backoff adds time)

---

## Versioning

**Current Version**: 1.1.0

**Semantic Versioning**: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

**Version History**:
- **1.1.0** (2025-10-19): Added plugin distribution, setup Skill
- **1.0.0** (2025-10-18): Initial release

---

## Further Documentation

- **[Setup Guide](SETUP.md)** - OAuth configuration
- **[Usage Examples](USAGE.md)** - Detailed usage patterns
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues
- **[E2E Test Results](E2E_TEST_RESULTS.md)** - Testing and validation

---

**Questions? See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or open a GitHub issue.**
