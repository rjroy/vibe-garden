# Courier MCP

**A lightweight Model Context Protocol (MCP) server for exporting Gmail messages to markdown files**

Courier MCP enables Claude Code users to retrieve, filter, and export Gmail messages as structured markdown files with YAML frontmatter. Perfect for email analysis, note-taking, and archival workflows.

[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/rjroy/vibe-garden/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Features

- 🔍 **Powerful Search** - Full Gmail search syntax support (dates, senders, labels, keywords)
- 📧 **Bulk Export** - Retrieve up to 100 emails per request
- 📝 **Markdown Format** - Clean YAML frontmatter + markdown body
- 🔒 **Read-Only** - Never modifies your Gmail account
- ⚡ **Fast** - Concurrent fetching with 20-second timeout
- 🛡️ **Rate Limit Handling** - Transparent exponential backoff
- 📎 **Attachment Metadata** - Filename, size, MIME type (no binary downloads)
- 🔐 **OAuth 2.0** - Secure authentication with your own Gmail account
- 🎯 **Claude Code Plugin** - Install via `/plugin install courier-mcp@vibe-garden`

---

## Quick Start (5 Minutes)

### 1. Install Plugin

```bash
# In Claude Code, run:
/plugin install courier-mcp@vibe-garden
```

### 2. Set Up Gmail OAuth

Follow the [Setup Guide](docs/SETUP.md) to:
1. Create a Google Cloud project
2. Enable Gmail API
3. Download OAuth credentials
4. Set environment variable: `GMAIL_CREDENTIALS_PATH=/path/to/credentials.json`

### 3. Use in Claude Code

```
You: Export my last 10 unread emails to /tmp/emails

Claude: [Uses courier-mcp get-messages tool]
✓ Exported 10 messages in 3.2 seconds:
  - /tmp/emails/20251019_143210_inbox_from_alice.md
  - /tmp/emails/20251019_143211_inbox_from_bob.md
  - ...
```

---

## Use Cases

### Email Analysis & Summarization

```
You: Export all emails from boss@company.com from last week and summarize key action items

Claude: [Exports emails, then summarizes content]
```

### Research & Note-Taking

```
You: Find all emails with subject [VOICE] and export to my notes directory

Claude: [Exports to notes/emails/ with full markdown formatting]
```

### Project Documentation

```
You: Export all emails labeled "Project Docs" and create a timeline

Claude: [Exports messages, analyzes dates, creates timeline]
```

### Archival & Backup

```
You: Export the last 100 emails from INBOX for backup

Claude: [Bulk export with collision prevention]
```

---

## Tools Available

### `get-folders`

List all Gmail labels/folders with message counts.

**Example**:
```json
{
  "folders": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "message_count": 1245,
      "unread_count": 42
    },
    ...
  ]
}
```

### `get-messages`

Query Gmail and export to markdown files.

**Parameters**:
- `export_directory` (required): Where to save files
- `search_query` (optional): Gmail search syntax (e.g., `"is:unread from:boss@example.com"`)
- `folder` (optional): Folder/label name (default: "INBOX")
- `date_start`, `date_end` (optional): ISO 8601 dates (YYYY-MM-DD)
- `max_results` (optional): 1-100 messages (default: 10)

**Example Output**:
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

---

## Markdown Export Format

Each email is saved as a markdown file with YAML frontmatter:

```markdown
---
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
    url: "https://mail.google.com/mail/u/0/?...."
---

# Email from Alice Johnson

Here's the email body converted to markdown...

**Key Points:**
- Item 1
- Item 2
```

**Filename Convention**: `YYYYMMDD_HHMMSS_<folder>_from_<sender>.md`

---

## Configuration

Configuration is stored in `courier.config` (YAML) and can be overridden with environment variables:

```yaml
# courier.config (default values)
COURIER_TIMEOUT_SECONDS: 20             # Max operation time
COURIER_MAX_RESULTS_DEFAULT: 10         # Default messages per request
COURIER_MAX_FILE_SIZE_KB: 10            # Max markdown file size
COURIER_NETWORK_RETRY_ATTEMPTS: 3       # Retry count on network failures
COURIER_NETWORK_RETRY_BACKOFF_FACTOR: 2 # Exponential backoff multiplier
COURIER_LABEL_CACHE_TTL_SECONDS: 3600   # Label cache duration
COURIER_LOG_PATH: "./courier-mcp.log"   # Log file location
COURIER_LOG_LEVEL: "DEBUG"              # Log verbosity
```

**Environment Variable Override**:
```bash
export COURIER_TIMEOUT_SECONDS=30
export COURIER_MAX_RESULTS_DEFAULT=50
```

---

## Documentation

- **[Setup Guide](docs/SETUP.md)** - OAuth configuration and first-time setup
- **[Usage Examples](docs/USAGE.md)** - Detailed tool usage and search queries
- **[API Reference](docs/API.md)** - Full tool specifications and schemas
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[E2E Test Results](docs/E2E_TEST_RESULTS.md)** - Testing validation and performance
- **[Contributing Guide](CONTRIBUTING.md)** - Development setup and guidelines

---

## Requirements

- **Python**: 3.10 or higher
- **Claude Code**: Latest version
- **Gmail Account**: With OAuth 2.0 credentials
- **Google Cloud Project**: Free tier sufficient

---

## Installation (for Developers)

```bash
# Clone repository
git clone https://github.com/rjroy/vibe-garden.git
cd vibe-garden/courier-mcp

# Create virtual environment
python -m venv server/venv
source server/venv/bin/activate  # On Windows: server\venv\Scripts\activate

# Install dependencies
pip install -e server/

# Set up OAuth credentials (see docs/SETUP.md)
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

# Run MCP server (for testing)
python -m courier_mcp
```

---

## Performance

- **10 messages**: < 2 seconds
- **50 messages**: < 10 seconds
- **100 messages**: < 20 seconds
- **Label fetch**: < 1 second (cached)

Actual performance depends on network speed, Gmail API quota, and message size.

---

## Security

- ✅ **Read-only access** - Never sends emails or modifies Gmail state
- ✅ **OAuth 2.0** - Standard Google authentication
- ✅ **Local storage** - Credentials stored locally, never shared
- ✅ **No secrets in logs** - Sensitive data automatically sanitized
- ✅ **No binary downloads** - Attachment metadata only (no files)

**IMPORTANT**: Never commit `credentials.json` or `token.pickle` to version control!

---

## Troubleshooting

Common issues and solutions:

| Issue | Solution |
|-------|----------|
| "Configuration not yet loaded" | Restart MCP server; ensure `courier.config` exists |
| "GMAIL_CREDENTIALS_PATH not set" | Set environment variable or see [SETUP.md](docs/SETUP.md) |
| "Invalid grant" (token expired) | Delete `token.pickle` and re-authenticate |
| "Rate limit exceeded" | Tool handles automatically; wait and retry |
| "Permission denied" (export) | Check directory permissions or use different path |

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for full guide.

---

## FAQ

**Q: Does this modify my Gmail account?**
A: No. Courier MCP is **read-only**. It only fetches and exports messages.

**Q: How many emails can I export at once?**
A: Up to 100 per request. Use multiple requests for larger exports.

**Q: What happens if the request times out?**
A: Partial results are returned (files saved so far + error message).

**Q: Can I use multiple Gmail accounts?**
A: Not in a single instance. Run separate server instances with different credentials.

**Q: Are attachments downloaded?**
A: No. Only metadata (filename, size, MIME type) is included.

**Q: Does this use my Gmail API quota?**
A: Yes. Free tier quota (250 units/second/user) is more than sufficient for typical use.

---

## Limitations

- **Read-only**: Cannot send emails, create drafts, or modify message state
- **No attachment downloads**: Metadata only (by design)
- **Single account per instance**: Use separate server instances for multiple accounts
- **20-second timeout**: Configurable, but enforced to prevent hangs
- **100 message limit per request**: Use multiple requests for larger exports

---

## Roadmap (v2.0+)

- [ ] Thread/conversation grouping (export related messages together)
- [ ] Real-time sync and polling for new messages
- [ ] Multiple Gmail account support (multi-instance orchestration)
- [ ] Attachment binary downloads (opt-in)
- [ ] Email template generation (bulk email composition)

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Running tests
- Code style guidelines
- Pull request process

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Credits

**Author**: Ronald Roy (gsdwig@gmail.com)
**Repository**: https://github.com/rjroy/vibe-garden
**Plugin**: `courier-mcp@vibe-garden`

**Built with**:
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- [Gmail API](https://developers.google.com/gmail/api)
- [Claude Code](https://claude.com/claude-code)

---

## Support

- 📖 **Documentation**: [docs/](docs/)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/rjroy/vibe-garden/issues)
- 💬 **Questions**: Open a discussion on GitHub
- 🔧 **Setup Help**: See [docs/SETUP.md](docs/SETUP.md) and [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Happy emailing! 📬**
