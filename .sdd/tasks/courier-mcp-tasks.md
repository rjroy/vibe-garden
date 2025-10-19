# Courier MCP - Task Breakdown

**Specification**: [.sdd/specs/courier-mcp.md](./../specs/courier-mcp.md)
**Plan**: [.sdd/plans/courier-mcp-plan.md](./../plans/courier-mcp-plan.md)
**Version**: 1.1.0
**Status**: Ready for Implementation
**Created**: 2025-10-18
**Last Updated**: 2025-10-19

## Task Summary

Total Tasks: 23
Estimated Timeline: ~43 hours (5-6 days full-time)

*Note: v1.0.0 plan estimate was 16-21 hours. Detailed task breakdown reveals ~38 hours due to granular decomposition of complex async/retry logic and comprehensive testing requirements. v1.1.0 adds ~5 hours for plugin distribution, marketplace integration, and setup Skill.*

## Task Categories

- **Foundation**: 3 tasks - Project setup, configuration, dependencies
- **Authentication**: 2 tasks - OAuth flow, credential management
- **Gmail Service**: 3 tasks - Label fetching, message fetching, rate limit handling
- **Markdown Export**: 2 tasks - Message formatting, filename collision handling
- **Tool Handlers**: 2 tasks - Tool registration, input validation
- **Timeout & Concurrency**: 2 tasks - Async execution, timeout enforcement
- **Testing**: 2 tasks - Unit and integration tests, E2E validation
- **Documentation & Polish**: 2 tasks - Setup guides, error messages, final testing
- **Plugin Distribution (v1.1.0)**: 4 tasks - Plugin manifest, setup Skill, marketplace registration, portability testing

---

## Foundation Tasks

### Task 1: Project Setup & Configuration
**ID**: TASK-001
**Category**: Foundation
**Priority**: Critical
**Estimate**: 1.5 hours
**Dependencies**: None
**Assigned To**: Unassigned

**Description**:
Initialize the Courier MCP project structure with configuration management. Create project directory, Python package structure, configuration file, and environment variable handling following the wyrd-gen-mcp pattern already established in the repository.

**Acceptance Criteria**:
- [ ] Project directory structure created: `courier-mcp/src/courier_mcp/`, `courier-mcp/tests/`, `courier-mcp/docs/`
- [ ] `courier.config` file created with defaults:
  - `COURIER_TIMEOUT_SECONDS: 20` (max operation time)
  - `COURIER_MAX_RESULTS_DEFAULT: 10` (messages per request)
  - `COURIER_MAX_FILE_SIZE_KB: 10` (max markdown file size, splits large messages)
  - `COURIER_NETWORK_RETRY_ATTEMPTS: 3` (retry count on network failures)
  - `COURIER_NETWORK_RETRY_BACKOFF_FACTOR: 2` (exponential backoff multiplier)
- [ ] `config.py` module implements config loading: ENV var overrides, yaml parsing, defaults
- [ ] `.env.example` file documents required variables: `GMAIL_CREDENTIALS_PATH`, `COURIER_TIMEOUT_SECONDS`, etc.
- [ ] `__init__.py` files set up Python package structure
- [ ] `.gitignore` includes `.env`, `credentials.json`, `token.pickle`, `*.pyc`
- [ ] Config loading tested with sample ENV vars (in unit tests)

**Technical Details**:
- Files to create/modify:
  - `courier-mcp/courier.config` (YAML config)
  - `courier-mcp/src/courier_mcp/__init__.py`
  - `courier-mcp/src/courier_mcp/config.py`
  - `courier-mcp/.env.example`
  - `courier-mcp/.gitignore`
- Key considerations:
  - Match wyrd-gen-mcp directory structure for consistency
  - Config must support both hardcoded defaults and ENV overrides
  - Ensure security: credentials paths not hardcoded
- Related spec sections: NFR-2 (Configuration), NFR-3 (Security)

**Testing Requirements**:
- Unit tests for config loading with mock ENV vars
- Verify defaults applied when ENV vars missing
- Verify ENV vars override YAML defaults

**Notes**:
- Reference: `wyrd-gen-mcp/src/wyrd_gen_mcp/config.py` for pattern

---

### Task 2: Project Dependencies & Virtual Environment
**ID**: TASK-002
**Category**: Foundation
**Priority**: Critical
**Estimate**: 1 hour
**Dependencies**: TASK-001
**Assigned To**: Unassigned

**Description**:
Create `setup.py` and `requirements.txt` with all necessary Python dependencies. Set up virtual environment and install editable mode for development.

**Acceptance Criteria**:
- [ ] `setup.py` created with package metadata and install requirements
- [ ] `requirements.txt` lists: mcp, google-auth-oauthlib, google-auth-httplib2, google-api-python-client, html2text, python-dateutil, pyyaml, pytest, pytest-asyncio
- [ ] `requirements-dev.txt` includes dev tools: pytest, black, pylint, mypy
- [ ] Virtual environment created and documented in README
- [ ] All dependencies install successfully with `pip install -e .`
- [ ] Import test passes: `python -c "import courier_mcp"` succeeds

**Technical Details**:
- Files to create:
  - `courier-mcp/setup.py`
  - `courier-mcp/requirements.txt`
  - `courier-mcp/requirements-dev.txt`
  - `courier-mcp/README.md` (basic setup instructions)
- Key considerations:
  - Pin major versions for stability (e.g., `google-api-python-client>=2.90.0`)
  - Python 3.10+ requirement per plan
  - Match wyrd-gen-mcp dependency patterns
- Related spec sections: Technical Context (dependencies)

**Testing Requirements**:
- All packages install without errors
- Import all packages in a test script

**Notes**:
- Reference: `wyrd-gen-mcp/setup.py` for similar setup

---

### Task 3: Logging & Error Handling Framework
**ID**: TASK-003
**Category**: Foundation
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-001
**Assigned To**: Unassigned

**Description**:
Create logging infrastructure and base error classes. Set up file-based logging (courier-mcp.log), structured error responses for MCP protocol, and exception hierarchy.

**Acceptance Criteria**:
- [ ] `logger.py` module sets up file-based logging to `courier-mcp.log`
- [ ] Logger configured with DEBUG level, rotating file handler
- [ ] Base exception class `CourierError` created
- [ ] Specific exceptions: `AuthenticationError`, `GmailAPIError`, `ExportError`, `TimeoutError`
- [ ] MCP error response format defined: `{"error": "message", "code": "error_code"}`
- [ ] All exceptions include proper logging before JSON response
- [ ] Log file location configurable via ENV var `COURIER_LOG_PATH` (default: `./courier-mcp.log`)

**Technical Details**:
- Files to create:
  - `courier-mcp/src/courier_mcp/logger.py`
  - `courier-mcp/src/courier_mcp/errors.py`
- Key considerations:
  - Match wyrd-gen-mcp logging patterns
  - Never log authentication tokens or credentials
  - Structured logging for easier debugging
- Related spec sections: NFR-3 (Security), Reliability

**Testing Requirements**:
- Unit tests verify logger writes to file
- Verify sensitive data not logged
- Verify exception hierarchy works

**Notes**:
- Reference: `wyrd-gen-mcp/src/wyrd_gen_mcp/logger.py` for patterns

---

## Authentication Tasks

### Task 4: OAuth 2.0 Credential Management
**ID**: TASK-004
**Category**: Authentication
**Priority**: Critical
**Estimate**: 2.5 hours
**Dependencies**: TASK-001, TASK-003
**Assigned To**: Unassigned

**Description**:
Implement OAuth 2.0 authentication flow for Gmail API. Handle credential loading, token refresh, and secure storage. Follow google-auth-oauthlib patterns for user delegation.

**Acceptance Criteria**:
- [ ] `auth.py` module implements credential loading from `GMAIL_CREDENTIALS_PATH`
- [ ] OAuth flow supports refresh tokens: load from `credentials.json` and `token.pickle`
- [ ] `ensure_valid_token()` function checks token expiration and refreshes if needed
- [ ] `build_gmail_service()` returns authenticated gmail API service object
- [ ] Credentials validated at server startup; error if missing/invalid
- [ ] Security: no credentials logged, no hardcoded secrets, tokens stored locally only
- [ ] Scope: `gmail.readonly` (read-only access per spec)
- [ ] Error handling: `AuthenticationError` raised on auth failures with helpful messages

**Technical Details**:
- Files to create:
  - `courier-mcp/src/courier_mcp/auth.py`
- Key considerations:
  - Use `google.oauth2.service_account` or `google-auth-oauthlib` based on credential type
  - Support both OAuth 2.0 refresh tokens (for users) and Service Accounts (future)
  - Credentials path from ENV var; never commit credentials
  - Token pickle file for session caching
- Related spec sections: FR-7 (Authentication), NFR-3 (Security)

**Testing Requirements**:
- Unit tests with mock credentials
- Test token refresh logic
- Test error cases (expired token, invalid creds, missing scope)
- Verify no sensitive data in logs

**Notes**:
- Reference: Gmail API reference materials in `/seeds/reference/`
- Will be mocked in unit tests; integration tests use real test account

---

### Task 5: Service Account & Credential Setup Documentation
**ID**: TASK-005
**Category**: Authentication
**Priority**: High
**Estimate**: 1.5 hours
**Dependencies**: TASK-004
**Assigned To**: Unassigned

**Description**:
Create comprehensive setup guide for users to configure Gmail OAuth credentials. Document the one-time setup process: Google Cloud project creation, OAuth app setup, credentials.json generation, and environment variable configuration.

**Acceptance Criteria**:
- [ ] `docs/SETUP.md` created with step-by-step OAuth setup guide
- [ ] Includes screenshots/CLI commands for:
  - Creating Google Cloud project
  - Enabling Gmail API
  - Creating OAuth 2.0 credentials
  - Running OAuth flow to generate credentials.json
- [ ] `.env.example` clearly shows required variables
- [ ] Security warnings: never commit credentials, use `.gitignore`
- [ ] Troubleshooting section addresses common errors
- [ ] Quickstart section: 5 minutes to get running
- [ ] Tested: new user can follow guide and authenticate successfully

**Technical Details**:
- Files to create:
  - `courier-mcp/docs/SETUP.md`
  - Update `courier-mcp/.env.example`
- Key considerations:
  - Make it beginner-friendly
  - Include screenshots for non-technical users
  - Highlight security best practices
- Related spec sections: Technical Context, Security

**Testing Requirements**:
- Have a test user follow guide end-to-end
- Verify all links and screenshots are current
- Verify credentials.json successfully used

**Notes**:
- Reference: Gmail API documentation and reference materials
- Spec explicitly requires this per security requirements

---

## Gmail Service Tasks

### Task 6: Label Caching & Folder Discovery
**ID**: TASK-006
**Category**: Gmail Service
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-004
**Assigned To**: Unassigned

**Description**:
Implement label fetching and in-memory caching with TTL. Cache all available Gmail folders/labels with message counts to support folder discovery tool and label name→ID translation.

**Acceptance Criteria**:
- [ ] `gmail_service.py` module created with `GmailService` class
- [ ] `fetch_labels()` method calls Gmail API `users.labels.list()`
- [ ] In-memory cache stores labels with 1-hour TTL
- [ ] Cache includes: id, name, message_count, unread_count
- [ ] `get_label_id(friendly_name)` translates user-facing folder names to IDs
- [ ] Cache invalidation on TTL or explicit refresh
- [ ] `normalize_label_name()` handles both system labels (INBOX, SENT, DRAFTS) and custom labels
- [ ] Error handling: `GmailAPIError` on API failures
- [ ] Logging: cache hit/miss events, API quota consumption

**Technical Details**:
- Files to create:
  - `courier-mcp/src/courier_mcp/gmail_service.py`
- Key considerations:
  - Gmail system labels: INBOX, SENT, DRAFTS, SPAM, TRASH, IMPORTANT, STARRED, UNREAD
  - Custom labels may have special characters; normalize for user input
  - Cache memory cost negligible (~10KB even with hundreds of labels)
  - TTL: 1 hour per plan
- Related spec sections: FR-7 (Folder discovery), FR-5 (Label support), NFR-1 (Caching)

**Testing Requirements**:
- Unit tests with mocked Gmail API
- Test cache TTL expiration
- Test label name→ID translation
- Test error cases (API failures, missing labels)
- Test system vs. custom labels

**Notes**:
- Gmail API quota: 1 unit per labels.list() call
- Cache avoids repeated calls during single session

---

### Task 7: Message List & Fetch with Rate Limiting
**ID**: TASK-007
**Category**: Gmail Service
**Priority**: Critical
**Estimate**: 3 hours
**Dependencies**: TASK-006, TASK-004
**Assigned To**: Unassigned

**Description**:
Implement message fetching from Gmail with search query support and exponential backoff for rate limiting. Handle Gmail API pagination, search query building, and graceful error handling for rate limits.

**Acceptance Criteria**:
- [ ] `fetch_messages()` method in `GmailService`
- [ ] Search query building: combine search_query + label ID + date range filters
- [ ] Gmail API `users.messages.list()` with maxResults parameter (1-100)
- [ ] Returns list of message IDs matching criteria
- [ ] Pagination support: handle nextPageToken if results > maxResults
- [ ] Error handling for malformed search queries (400 errors)
- [ ] Rate limit handling: detect 429 responses
- [ ] Exponential backoff: 2^attempt seconds, max 10 attempts per plan spec
- [ ] Logging: quota consumption, backoff attempts, rate limit hits
- [ ] Returns partial results on timeout (handled in caller)

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/gmail_service.py`
- Key considerations:
  - Gmail search query syntax: `is:unread`, `from:email@example.com`, `before:2025-10-01`, etc.
  - API quota: ~1 unit per messages.list() call
  - Rate limit quota: 250 quota units/sec per user
  - Don't fetch full message bodies yet (done in next task)
- Related spec sections: FR-1 (Retrieval), FR-2 (Search), FR-11 (Rate limits)

**Testing Requirements**:
- Unit tests with mocked Gmail API
- Test various search queries
- Test pagination (>100 results)
- Test rate limit (simulate 429 response)
- Test exponential backoff timing
- Test malformed queries

**Notes**:
- Exponential backoff formula: `min(2^attempt, max_backoff)`
- Gmail API docs: https://developers.google.com/gmail/api/guides/manage-labels

---

### Task 8: Concurrent Message Detail Fetching & Timeout
**ID**: TASK-008
**Category**: Gmail Service
**Priority**: Critical
**Estimate**: 3 hours
**Dependencies**: TASK-007
**Assigned To**: Unassigned

**Description**:
Implement concurrent message detail fetching using asyncio. Fetch full message bodies, headers, and attachments in parallel with timeout enforcement. Return partial results if timeout reached.

**Acceptance Criteria**:
- [ ] `fetch_message_details()` method uses asyncio for concurrent fetches
- [ ] Concurrent tasks limited to 5-10 (balance quota vs. timeout)
- [ ] Fetch full message with `format=full` to get payload structure
- [ ] Extract: headers (from, to, cc, bcc, subject, date), body (plain or HTML), attachments metadata
- [ ] Attachment metadata: filename, size, MIME type, download URL (no binary)
- [ ] Global timeout wrapper: all operations must complete within `COURIER_TIMEOUT_SECONDS` (default 20s)
- [ ] Timeout handling: return partial results + timeout error
- [ ] Error handling: 404 (deleted messages), 403 (permission), 401 (expired token)
- [ ] Logging: concurrent task count, timeout occurrences, fetch duration

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/gmail_service.py`
- Key considerations:
  - Asyncio event loop management
  - `asyncio.gather()` for parallel tasks with timeout
  - Gmail API `users.messages.get()` quota: ~5 units per call (rough estimate)
  - Timeout budget: ~5-8 seconds for 100 message fetches
  - Deleted messages: catch 404, log as informational error
- Related spec sections: FR-12 (20-second timeout), FR-13 (Partial results), FR-5 (Attachments)

**Testing Requirements**:
- Unit tests with mocked Gmail API (asyncio)
- Test concurrent fetch of 10, 50, 100 messages
- Test timeout behavior (mock slow API)
- Test partial results on timeout
- Test error handling (404, 403, 401)
- Performance test: 100-message fetch should complete in <8s

**Notes**:
- Use `asyncio.wait_for()` for timeout enforcement
- Limit concurrency with semaphore to prevent quota exhaustion

---

## Markdown Export Tasks

### Task 9: Message Formatting & HTML to Markdown Conversion
**ID**: TASK-009
**Category**: Markdown Export
**Priority**: High
**Estimate**: 2.5 hours
**Dependencies**: TASK-008
**Assigned To**: Unassigned

**Description**:
Implement message formatting to markdown with YAML frontmatter. Handle HTML to markdown conversion, extract email headers, and structure output with attachment metadata.

**Acceptance Criteria**:
- [ ] `export.py` module created with message formatting functions
- [ ] `format_message_to_markdown()` converts Gmail message to markdown string
- [ ] YAML frontmatter includes: from, to, cc, bcc, subject, date, message-id, labels, attachments
- [ ] HTML body conversion using `html2text` library
- [ ] Fallback to plain text if HTML unavailable
- [ ] Date format: ISO 8601 (2025-10-18T14:00:00Z)
- [ ] Message ID format: Gmail message ID
- [ ] Attachments metadata: filename, size, MIME type, download URL
- [ ] Email header parsing: extract sender name/email, recipients, subject
- [ ] Markdown formatting: proper escaping, section headers, list formatting
- [ ] Output matches spec example format
- [ ] **NEW**: File size limit enforced: max 10KB per markdown file (configurable via `COURIER_MAX_FILE_SIZE_KB`)
- [ ] **NEW**: If message body exceeds limit, truncate with note: "[Message truncated - exceeded 10KB limit. Full message available in Gmail.]"
- [ ] **NEW**: Truncation preserves YAML frontmatter and attachment list completely

**Technical Details**:
- Files to create:
  - `courier-mcp/src/courier_mcp/export.py`
- Key considerations:
  - Gmail message payload structure: headers array + body + MIME parts
  - Base64url decoding for body data
  - HTML emails very common; html2text handles most cases
  - Multipart messages: extract text/plain and text/html parts
  - Attachment extraction from MIME structure
- Related spec sections: FR-6 (Format), FR-8 (Frontmatter), FR-5 (Attachments), FR-9 (Filename)

**Testing Requirements**:
- Unit tests with sample Gmail messages
- Test various email types: plain text, HTML, multipart
- Test YAML frontmatter parsing (ensure valid YAML)
- Test markdown output matches spec example
- Test edge cases: special characters, very long subjects, many recipients
- Test attachment metadata extraction
- **NEW**: Test file size limit (10KB truncation)
- **NEW**: Test truncation preserves frontmatter and attachments
- **NEW**: Test truncation note added to output

**Notes**:
- Reference spec example: lines 189-223 in spec file
- Use `pyyaml` for frontmatter generation

---

### Task 10: Filename Generation & Collision Prevention
**ID**: TASK-010
**Category**: Markdown Export
**Priority**: High
**Estimate**: 1.5 hours
**Dependencies**: TASK-009
**Assigned To**: Unassigned

**Description**:
Implement filename generation and safe file writing with collision detection. Generate human-readable filenames with timestamp + sender name, append `_1`, `_2` suffixes for duplicates, and prevent overwrites.

**Acceptance Criteria**:
- [ ] `generate_filename()` creates format: `YYYYMMDD_HHMMSS_[folder]_from_[sender-name].md`
- [ ] Sender name extracted from email sender header (friendly name preferred)
- [ ] Timestamp from email date (not current time)
- [ ] Folder name derived from label list (prefer INBOX, then first label)
- [ ] Sanitization: remove special characters from sender name
- [ ] `safe_file_write()` function checks for existing files
- [ ] Collision handling: append `_1`, `_2`, etc. to filename (not overwrite)
- [ ] Check returns full path where file will be written
- [ ] Directory creation: create if missing (with error handling)
- [ ] Atomic write: write to temp file, then rename (prevent partial writes)
- [ ] Permission checking: verify write access before starting export

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/export.py`
- Key considerations:
  - Filename length limits (some filesystems): truncate sender name if needed
  - Timestamp format matches spec: `YYYYMMDD_HHMMSS` (e.g., `20251018_145032`)
  - Sanitization rules: alphanumeric, underscore, hyphen only
  - Atomic writes prevent corruption on process crash
- Related spec sections: FR-10 (Collision handling), FR-9 (Filename convention)

**Testing Requirements**:
- Unit tests for filename generation
- Test collision detection and suffix appending
- Test sanitization (special chars, unicode, spaces)
- Test directory creation and permission errors
- Test atomic write behavior
- Test timestamp extraction from message date

**Notes**:
- Reference spec naming: lines 240-242 in spec file
- Max suffix count: reasonable limit (e.g., 1000 to avoid infinite loop)

---

## Tool Handlers Tasks

### Task 11: Tool Registration & MCP Server Setup
**ID**: TASK-011
**Category**: Tool Handlers
**Priority**: Critical
**Estimate**: 2 hours
**Dependencies**: TASK-003, TASK-004, TASK-006
**Assigned To**: Unassigned

**Description**:
Create main MCP server with tool registration. Define `get-messages` and `get-folders` tools with JSON schemas, set up async handlers, and configure stdio transport for Claude Code integration.

**Acceptance Criteria**:
- [ ] `server.py` created with MCP Server initialization
- [ ] Server name: `"courier-mcp"`
- [ ] Tool 1 registered: `get-messages` with input schema
- [ ] Tool 2 registered: `get-folders` with input schema
- [ ] Input schemas match spec tool specs (lines 115-165)
- [ ] Tools registered as async handlers
- [ ] Stdio transport configured: `stdio_server(server)`
- [ ] Server startup logging: version, config loaded, auth verified
- [ ] Error handling: graceful shutdown, error JSON responses
- [ ] Tool validation: input parameters checked before processing
- [ ] Follows wyrd-gen-mcp MCP server patterns

**Technical Details**:
- Files to create:
  - `courier-mcp/src/courier_mcp/server.py`
- Key considerations:
  - MCP protocol over stdio (no HTTP server)
  - Tool input validation before calling handlers
  - Proper MCP error response format
  - Async/await for long-running operations
- Related spec sections: Tool specifications, Integration with Claude Code

**Testing Requirements**:
- Unit tests: verify tool schemas are valid JSON
- Unit tests: tool handler signatures correct
- Integration test: start server, call each tool with sample input
- Verify MCP protocol compliance

**Notes**:
- Reference: `wyrd-gen-mcp/src/wyrd_gen_mcp/server.py` for MCP server patterns
- Tool input validation includes type checking, required fields, valid ranges

---

### Task 12: `get-folders` Tool Handler Implementation
**ID**: TASK-012
**Category**: Tool Handlers
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-011, TASK-006
**Assigned To**: Unassigned

**Description**:
Implement the `get-folders` tool handler. List all Gmail labels/folders with message counts and unread counts. Return cached results if available.

**Acceptance Criteria**:
- [ ] `handle_get_folders()` async function registered as tool handler
- [ ] Takes no input parameters (empty schema)
- [ ] Calls `gmail_service.fetch_labels()` with cache check
- [ ] Returns JSON array with fields: id, name, message_count, unread_count
- [ ] Output format matches spec (lines 168-175)
- [ ] Error handling: catch `GmailAPIError`, return error JSON
- [ ] Logging: cache hit/miss, API calls, duration
- [ ] Response time: <1 second (mostly cached)
- [ ] All labels returned: system + custom user labels

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/server.py`
- Key considerations:
  - Very lightweight operation (mostly cache lookup)
  - Cache hit in most cases (within 1-hour TTL)
  - Friendly label names for users (INBOX, not "INBOX" ID)
- Related spec sections: FR-7 (Folder discovery), Tool 2 spec

**Testing Requirements**:
- Unit tests with mocked Gmail API
- Test cache hit (no API call)
- Test cache miss (API call triggered)
- Test output format matches spec
- Test error handling

**Notes**:
- Tool called before `get-messages` to discover available folders

---

### Task 13: `get-messages` Tool Handler Implementation
**ID**: TASK-013
**Category**: Tool Handlers
**Priority**: Critical
**Estimate**: 3 hours
**Dependencies**: TASK-011, TASK-007, TASK-008, TASK-009, TASK-010
**Assigned To**: Unassigned

**Description**:
Implement the `get-messages` tool handler. Query Gmail with search filters, retrieve messages, export to markdown files, and return concise results. Orchestrate entire workflow from search to export.

**Acceptance Criteria**:
- [ ] `handle_get_messages()` async function registered as tool handler
- [ ] Input parameter validation:
  - `export_directory` required and valid path
  - `search_query` optional (full Gmail syntax supported)
  - `folder` optional, translates to label ID via cache
  - `date_start` and `date_end` optional, added to search query
  - `max_results` optional (1-100, default from config)
- [ ] Full workflow orchestration:
  1. Validate inputs
  2. Build search query (combine search_query + date filters + label)
  3. Call `fetch_messages()` to get message IDs
  4. Call `fetch_message_details()` with concurrent fetching
  5. Convert each message to markdown
  6. Write files with collision handling
  7. Return results before timeout
- [ ] Output format matches spec (lines 135-144)
- [ ] Timeout enforcement: all operations within `COURIER_TIMEOUT_SECONDS`
- [ ] Partial results on timeout: return files saved so far + error
- [ ] Error handling: graceful degradation, informative error messages
- [ ] Logging: query, message count, duration, quota usage, errors
- [ ] Rate limit handling: transparent backoff, users don't see backoff
- [ ] Path handling: both absolute and relative paths supported

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/server.py`
- Key considerations:
  - Timeout wrapper around entire operation
  - Partial results returned before timeout expires
  - Path resolution: relative paths → absolute from invocation directory
  - Directory creation: create export_directory if missing
  - Error handling: catch all exceptions, return meaningful errors
  - Search query building: proper escaping and quoting
- Related spec sections: Tool 1 spec (lines 111-155), All functional requirements

**Testing Requirements**:
- Integration tests with real Gmail account (small test dataset)
- Test various search queries (unread, from, subject, etc.)
- Test date filtering
- Test folder filtering
- Test max_results clamping (1-100)
- Test export directory creation
- Test collision prevention (export same query twice)
- Test timeout behavior (simulate slow API)
- Test error handling (invalid path, permission denied, etc.)
- Test rate limit handling (100 messages)
- Test output format and logging
- Performance test: 50-100 message export in <20s

**Notes**:
- Most complex tool; orchestrates multiple components
- Extensive error handling needed
- Reference spec acceptance test #1 (lines 246-255)

---

## Timeout & Concurrency Tasks

### Task 14: Global Timeout Wrapper & Async Management
**ID**: TASK-014
**Category**: Timeout & Concurrency
**Priority**: Critical
**Estimate**: 2 hours
**Dependencies**: TASK-008
**Assigned To**: Unassigned

**Description**:
Implement global timeout enforcement for all operations. Create timeout wrapper utilities, task cancellation on timeout, and partial result collection. Ensure all operations complete within 20-second deadline.

**Acceptance Criteria**:
- [ ] `timeout_context()` async context manager created
- [ ] Configurable timeout from `COURIER_TIMEOUT_SECONDS` (default: 20)
- [ ] All long-running operations wrapped: message fetches, file writes, API calls
- [ ] `asyncio.wait_for()` used for timeout enforcement
- [ ] On timeout: cancel remaining tasks, return partial results
- [ ] Partial results captured: files_saved list + errors array
- [ ] Timeout error includes: count of messages processed, partial file list, reason
- [ ] Graceful degradation: operations complete incrementally (not all-or-nothing)
- [ ] Logging: timeout events, remaining tasks cancelled, partial result count
- [ ] Testing: simulate timeout scenarios, verify partial results returned

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/server.py`
  - `courier-mcp/src/courier_mcp/gmail_service.py`
- Key considerations:
  - Timeout budget allocation (see plan page 423-430)
  - Task cancellation: use `asyncio.CancelledError` handling
  - Partial results must be usable (valid markdown files)
  - No partial files left behind on cancellation
  - Timeout applies to entire operation, not per-request
- Related spec sections: FR-12 (20-second timeout), FR-13 (Partial results)

**Testing Requirements**:
- Unit tests with short timeout values (simulate timeout)
- Test task cancellation
- Test partial results collected correctly
- Test timeout error message format
- Performance test: verify <20s timeout enforced
- Test no partial files created on timeout

**Notes**:
- Critical for meeting spec requirements
- Extensive timeout testing needed before release

---

### Task 15: Async Error Recovery & Graceful Degradation
**ID**: TASK-015
**Category**: Timeout & Concurrency
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-014
**Assigned To**: Unassigned

**Description**:
Implement error recovery during async operations. Handle task failures gracefully, collect partial results, report which operations succeeded/failed, and provide helpful error messages for users. Implement automatic retry with exponential backoff for transient network failures.

**Acceptance Criteria**:
- [ ] Individual message fetch failures don't crash entire operation
- [ ] Failed message fetches logged with message ID and error reason
- [ ] Failed messages excluded from export (no partial markdown files)
- [ ] Error list returned to user: `[{"message_id": "123", "error": "Rate limited"}, ...]`
- [ ] Rate limit errors (429) distinguished from permanent failures
- [ ] Transient network errors (timeout, connection refused) trigger automatic retry
- [ ] Retry logic uses exponential backoff: `min(2^attempt * factor, max_backoff)`
- [ ] Retry attempts: configurable via `COURIER_NETWORK_RETRY_ATTEMPTS` (default: 3)
- [ ] Backoff factor: configurable via `COURIER_NETWORK_RETRY_BACKOFF_FACTOR` (default: 2)
- [ ] Retry transparent to user (no user-facing mention unless all retries exhausted)
- [ ] Deleted messages reported as informational (not critical error)
- [ ] Auth errors (401, 403) reported with guidance (no retry)
- [ ] File write errors caught and reported per-file
- [ ] Quota exhaustion handled: partial export completed, user informed
- [ ] Error messages user-friendly and actionable
- [ ] Logging: retry attempts logged for debugging

**Technical Details**:
- Files to modify:
  - `courier-mcp/src/courier_mcp/gmail_service.py`
  - `courier-mcp/src/courier_mcp/server.py`
- Key considerations:
  - Don't fail entire operation on single message failure
  - Track error type: transient (retry) vs. permanent (skip)
  - Transient errors: connection timeout, connection refused, temporary unavailable (503)
  - Permanent errors: auth failures (401, 403), invalid request (400)
  - Network retry logic separate from rate limit backoff
  - Deleted messages: expected, not error
  - Rate limit (429): expected under load, transparent to user (existing backoff applies)
  - Config loaded from courier.config: retry attempts, backoff factor
- Related spec sections: Error Handling Strategy (plan pages 373-388), Reliability

**Testing Requirements**:
- Unit tests simulating various failures:
  - Individual message fetch failures
  - Rate limit on 50th message (429 errors)
  - Network errors (connection timeout, connection refused)
  - Retry backoff timing (verify exponential backoff formula)
  - Auth errors (no retry on 401, 403)
  - Deleted messages (404 handled gracefully)
  - Verify retry attempts logged correctly
- Integration tests with real Gmail (if possible)
- Verify partial exports on errors
- Verify error messages are helpful
- Performance test: verify retries don't exceed timeout

**Notes**:
- Graceful degradation key to good UX
- Users prefer partial results to complete failure

---

## Testing Tasks

### Task 16: Comprehensive Unit & Integration Test Suite
**ID**: TASK-016
**Category**: Testing
**Priority**: High
**Estimate**: 3 hours
**Dependencies**: TASK-001 through TASK-015
**Assigned To**: Unassigned

**Description**:
Create comprehensive test suite covering all components. Unit tests with mocked Gmail API, integration tests with real test account, and acceptance tests mapping to spec requirements.

**Acceptance Criteria**:
- [ ] Unit test files created:
  - `tests/test_auth.py` - credential loading, token refresh
  - `tests/test_gmail_service.py` - label fetching, message fetching, rate limits
  - `tests/test_export.py` - markdown formatting, filename generation, collision handling
  - `tests/test_server.py` - tool handlers, error responses
- [ ] All unit tests use mocked Gmail API (no credentials needed)
- [ ] Test coverage >85% for core modules
- [ ] Integration test file: `tests/test_integration.py`
  - Real Gmail API calls (requires test credentials)
  - End-to-end workflow: query → fetch → export → verify files
  - Rate limit simulation (if possible)
- [ ] Acceptance test file: `tests/test_acceptance.py`
  - Maps to spec acceptance tests (spec lines 244-255)
  - 10 acceptance criteria verified
- [ ] Pytest configuration: `pytest.ini` with asyncio support
- [ ] Test data: sample Gmail messages, mock API responses
- [ ] CI/CD ready: tests run with `pytest` command
- [ ] All tests passing before merge

**Technical Details**:
- Files to create:
  - `tests/test_auth.py`
  - `tests/test_gmail_service.py`
  - `tests/test_export.py`
  - `tests/test_server.py`
  - `tests/test_integration.py`
  - `tests/test_acceptance.py`
  - `tests/conftest.py` (pytest fixtures)
  - `tests/fixtures/sample_messages.json` (mock data)
- Key considerations:
  - Mock all Gmail API calls in unit tests
  - Use `pytest-asyncio` for async test support
  - Fixtures for common test data (messages, labels, etc.)
  - Integration tests optional (requires real Gmail account)
- Related spec sections: Testing Strategy (plan pages 463-488)

**Testing Requirements**:
- All tests passing
- Coverage report generated
- Async tests working correctly
- Mock data representative of real Gmail API responses

**Notes**:
- Reference: pytest and pytest-asyncio documentation
- Mock Gmail API responses from real API examples

---

### Task 17: E2E Testing & Performance Validation
**ID**: TASK-017
**Category**: Testing
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-016
**Assigned To**: Unassigned

**Description**:
End-to-end testing with real Gmail account (test account), performance validation, and timeout behavior verification. Manual testing of full user workflow from setup to export.

**Acceptance Criteria**:
- [ ] Manual E2E workflow validation:
  1. User authenticates with OAuth (credentials.json created)
  2. Query inbox: last 5 unread emails
  3. Verify files exported to specified directory
  4. Verify markdown files valid YAML + markdown
  5. Export same query again
  6. Verify no overwrites (files have `_1`, `_2` suffixes)
  7. Test large export (50-100 emails)
  8. Verify completes within 20 seconds
  9. Retrieve with rate limiting (100 emails, monitor quota)
  10. Verify partial results on timeout (simulated)
- [ ] Performance tests:
  - 10-message export: <2 seconds
  - 50-message export: <10 seconds
  - 100-message export: <20 seconds
  - Label fetch: <1 second
- [ ] Error scenarios tested:
  - Invalid export directory
  - Permission denied errors
  - Rate limit handling
  - Network timeout simulation
  - Deleted messages
- [ ] Test report documented: `docs/E2E_TEST_RESULTS.md`
- [ ] All scenarios pass

**Technical Details**:
- Files to create:
  - `docs/E2E_TEST_RESULTS.md` (test report)
  - `scripts/test-e2e.sh` (optional, manual test guide)
- Key considerations:
  - Requires real Gmail test account (can use shared test account)
  - Timing measurements with timestamps
  - Quota monitoring during tests
  - Network simulation for timeout testing (optional)
- Related spec sections: Testing Strategy (plan pages 477-488)

**Testing Requirements**:
- All 10 E2E scenarios pass
- Performance targets met
- Error scenarios handled gracefully
- Test report completed and reviewed

**Notes**:
- Use real Gmail test account (separate from personal)
- Document results in test report for team
- May be manual or scripted depending on setup complexity

---

## Documentation & Polish Tasks

### Task 18: Documentation, Setup Guides, & Examples
**ID**: TASK-018
**Category**: Documentation & Polish
**Priority**: High
**Estimate**: 2 hours
**Dependencies**: TASK-005, TASK-017
**Assigned To**: Unassigned

**Description**:
Create comprehensive documentation covering setup, usage examples, API reference, and troubleshooting. Include README, API docs, and example workflows.

**Acceptance Criteria**:
- [ ] `README.md` created:
  - Project overview and use cases
  - Quick start (5-minute setup)
  - Features overview
  - Links to detailed docs
- [ ] `docs/SETUP.md` (from TASK-005) - OAuth setup guide
- [ ] `docs/USAGE.md` - Tool usage examples:
  - `get-messages` with various search queries
  - `get-folders` output
  - Export directory handling
  - Markdown file examples
- [ ] `docs/API.md` - Tool specifications:
  - Input/output schemas
  - Parameter descriptions
  - Error responses
- [ ] `docs/TROUBLESHOOTING.md`:
  - Common auth issues
  - Rate limit handling
  - File permission errors
  - Network issues
- [ ] `CONTRIBUTING.md` - development setup for contributors
- [ ] Code comments: complex logic documented
- [ ] Inline type hints: functions annotated with types
- [ ] Example workflow: `.sdd/examples/courier-mcp-workflow.md`

**Technical Details**:
- Files to create:
  - `courier-mcp/README.md`
  - `courier-mcp/docs/USAGE.md`
  - `courier-mcp/docs/API.md`
  - `courier-mcp/docs/TROUBLESHOOTING.md`
  - `courier-mcp/CONTRIBUTING.md`
  - `courier-mcp/.sdd/examples/courier-mcp-workflow.md`
- Key considerations:
  - Documentation should be user-friendly
  - Examples should be copy-paste ready
  - Troubleshooting section should cover 80% of issues
  - Type hints improve code readability
- Related spec sections: All sections

**Testing Requirements**:
- Documentation reviewed for accuracy
- Example code tested (copy-paste works)
- Links verified (no broken references)

**Notes**:
- Reference: wyrd-gen-mcp documentation for style/format
- Keep docs up-to-date as code evolves

---

### Task 19: Error Messages, Logging, & Final Polish
**ID**: TASK-019
**Category**: Documentation & Polish
**Priority**: Medium
**Estimate**: 1.5 hours
**Dependencies**: TASK-018
**Assigned To**: Unassigned

**Description**:
Polish error messages, improve logging, add helpful user guidance, and prepare for release. Ensure all errors are actionable and logs are useful for debugging.

**Acceptance Criteria**:
- [ ] All error messages follow format: `"{error_code}: {description} ({guidance})"`
- [ ] Error codes standardized: `AUTH_ERROR`, `RATE_LIMITED`, `TIMEOUT`, `INVALID_PATH`, `EXPORT_ERROR`
- [ ] Error guidance includes remediation: "To fix: ..."
- [ ] Logging levels appropriate: DEBUG for detailed, INFO for milestones, ERROR for failures
- [ ] Log messages include context: timestamps, message IDs, quota usage
- [ ] Sensitive data never logged: credentials, tokens, personal email content
- [ ] Tool output concise and user-friendly per spec FR-6
- [ ] Performance metrics logged: API call duration, concurrent task count, quota usage
- [ ] User-facing output (tool results) formatted as readable JSON
- [ ] Internal logs detailed (courier-mcp.log) for debugging

**Technical Details**:
- Files to modify:
  - All modules for consistent error messages
  - `logger.py` for improved logging
  - `server.py` for user-facing output formatting
- Key considerations:
  - Balance between logging detail and security
  - User-facing messages vs. internal logs
  - Actionable guidance reduces user support burden
- Related spec sections: Reliability, Error Handling

**Testing Requirements**:
- All error paths tested
- Error messages reviewed for clarity and guidance
- Log files reviewed for sensitive data
- Performance metrics visible in logs

**Notes**:
- Final polish before release
- Affects user experience significantly

---

## Plugin Distribution Tasks (v1.1.0)

### Task 20: Plugin Manifest & Directory Structure
**ID**: TASK-020
**Category**: Plugin Distribution (v1.1.0)
**Priority**: High
**Estimate**: 1 hour
**Dependencies**: TASK-001
**Assigned To**: Unassigned

**Description**:
Create Claude Code plugin manifest and directory structure following plugin conventions. Package Courier MCP as a Claude Code plugin for easy installation via marketplace.

**Acceptance Criteria**:
- [ ] `.claude-plugin/plugin.json` created with plugin metadata
- [ ] Plugin name: `"courier-mcp"`
- [ ] Plugin description matches spec v1.1.0
- [ ] Version: `"1.1.0"`
- [ ] Author metadata: Ronald Roy, gsdwig@gmail.com
- [ ] Repository URL: `https://github.com/rjroy/vibe-garden.git`
- [ ] License: MIT
- [ ] `mcpServers` configuration:
  - Server name: `"courier"`
  - Command: `"${CLAUDE_PLUGIN_ROOT}/servers/scripts/courier.sh"`
  - Args: `[""]`
- [ ] Directory structure follows plugin conventions:
  - `.claude-plugin/` - Plugin manifest
  - `servers/` - MCP server implementation (existing `src/courier_mcp/`)
  - `servers/scripts/` - Launcher scripts
  - `docs/` - Documentation (existing)
  - `skills/` - Setup assistance Skill (new)
- [ ] `servers/scripts/courier.sh` launcher script created
- [ ] Launcher activates venv and runs MCP server with stdio transport
- [ ] `${CLAUDE_PLUGIN_ROOT}` variable used for portability
- [ ] Plugin manifest validated against plugin.json schema

**Technical Details**:
- Files to create:
  - `courier-mcp/.claude-plugin/plugin.json`
  - `courier-mcp/servers/scripts/courier.sh`
- Files to reference:
  - `wyrd-gen-mcp/.claude-plugin/plugin.json` (template)
  - `wyrd-gen-mcp/servers/scripts/wyrd-gen.sh` (launcher template)
- Key considerations:
  - `${CLAUDE_PLUGIN_ROOT}` resolves to plugin installation directory
  - Launcher must handle venv activation and Python path resolution
  - Server command must be executable (chmod +x)
  - Cross-platform compatibility (Linux, macOS, Windows)
- Related spec sections: NFR - Plugin Distribution, Technical Context

**Testing Requirements**:
- Validate plugin.json syntax (JSON schema)
- Test launcher script executes server successfully
- Verify `${CLAUDE_PLUGIN_ROOT}` resolves correctly
- Test plugin installation in Claude Code (if possible)

**Notes**:
- Reference: `seeds/reference/claude-plugin-basics.md`, `claude-plugin-reference.md`
- Plugin manifest follows standard Claude Code plugin conventions

---

### Task 21: Setup Assistance Skill Implementation
**ID**: TASK-021
**Category**: Plugin Distribution (v1.1.0)
**Priority**: High
**Estimate**: 2.5 hours
**Dependencies**: TASK-005 (SETUP.md), TASK-020
**Assigned To**: Unassigned

**Description**:
Create setup assistance Skill that automatically activates when Gmail OAuth authentication fails. Skill presents troubleshooting guidance from SETUP.md with progressive disclosure.

**Acceptance Criteria**:
- [ ] `skills/courier-setup-helper/SKILL.md` created
- [ ] YAML frontmatter with metadata:
  - `name: courier-setup-helper`
  - `description:` Includes trigger keywords: "Gmail OAuth", "authentication", "credential", "GMAIL_CREDENTIALS_PATH", "token", "permission"
- [ ] Skill instructions guide users through:
  1. Detecting error type from error message
  2. Presenting relevant SETUP.md sections
  3. Troubleshooting OAuth setup failures
  4. Environment variable configuration
  5. First-time authentication flow
  6. Common error scenarios (token expired, invalid credentials, permission denied)
- [ ] Progressive disclosure levels:
  - Level 1 (metadata): YAML frontmatter always loaded (~50 tokens)
  - Level 2 (instructions): SKILL.md loaded when triggered (~2-3k tokens)
  - Level 3 (reference): Links to `docs/SETUP.md` for detailed steps
- [ ] Skill invocation conditions documented:
  - Authentication errors from Gmail API (401, 403)
  - Missing `GMAIL_CREDENTIALS_PATH` environment variable
  - Expired or invalid OAuth token
  - MCP server initialization failures due to credentials
  - User explicitly asks for help with Courier MCP setup
- [ ] Skill provides actionable steps:
  - Google Cloud Console setup instructions
  - OAuth credential download process
  - Environment variable setup commands
  - Token refresh commands
  - Links to external resources (Google Cloud Console, Gmail API docs)
- [ ] Skill tested: triggers on common auth errors

**Technical Details**:
- Files to create:
  - `courier-mcp/skills/courier-setup-helper/SKILL.md`
- Files to reference:
  - `spiral-grove/skills/spiral-grove-guide/SKILL.md` (template)
  - `courier-mcp/docs/SETUP.md` (source material)
  - `seeds/reference/claude-agent-skills.md` (Skill conventions)
- Key considerations:
  - Skill description must match error patterns for auto-activation
  - YAML frontmatter used for Skill discovery
  - Instructions should be concise but actionable
  - Link to SETUP.md for detailed steps (avoid duplication)
  - Claude automatically invokes Skill when error messages match description
- Related spec sections: FR-14, FR-15, FR-16 (Setup assistance Skill)

**Testing Requirements**:
- Test Skill activation on auth errors (mock error scenarios)
- Verify YAML frontmatter is valid
- Verify Skill provides helpful guidance
- Test progressive disclosure (metadata → instructions → reference)
- User testing: can users resolve auth issues with Skill guidance?

**Notes**:
- Skill enhances UX by reducing need for external documentation searches
- Auto-activation on common errors reduces support burden

---

### Task 22: Marketplace Registration in vibe-garden
**ID**: TASK-022
**Category**: Plugin Distribution (v1.1.0)
**Priority**: Medium
**Estimate**: 30 minutes
**Dependencies**: TASK-020
**Assigned To**: Unassigned

**Description**:
Register Courier MCP plugin in the vibe-garden marketplace catalog. Update root marketplace.json to include courier-mcp plugin entry for discovery and installation.

**Acceptance Criteria**:
- [ ] `.claude-plugin/marketplace.json` updated at vibe-garden root
- [ ] Courier MCP entry added to `plugins` array:
  - `name: "courier-mcp"`
  - `source: "./courier-mcp"`
  - `description:` Matches plugin.json description
  - `repository:` vibe-garden repository URL
  - `license: "MIT"`
- [ ] Entry follows same format as existing plugins (spiral-grove, wyrd-gen-mcp)
- [ ] Marketplace file validated (JSON syntax)
- [ ] Plugin discoverable via `/plugin install courier-mcp@vibe-garden`
- [ ] Marketplace listing verified (if testable)

**Technical Details**:
- Files to modify:
  - `/home/rjroy/Projects/vibe-garden/.claude-plugin/marketplace.json`
- Key considerations:
  - Marketplace is at vibe-garden repository root
  - Courier MCP already in marketplace (from file read), verify entry is complete
  - Plugin source path relative to vibe-garden root: `"./courier-mcp"`
- Related spec sections: NFR - Plugin Distribution, Marketplace Integration

**Testing Requirements**:
- Validate marketplace.json syntax
- Test plugin installation command (if Claude Code supports it)
- Verify plugin appears in marketplace listing

**Notes**:
- Courier MCP entry already exists in marketplace.json (confirmed from earlier file read)
- Task primarily verification and documentation

---

### Task 23: Plugin Portability & Installation Testing
**ID**: TASK-023
**Category**: Plugin Distribution (v1.1.0)
**Priority**: High
**Estimate**: 1.5 hours
**Dependencies**: TASK-020, TASK-021, TASK-022
**Assigned To**: Unassigned

**Description**:
Test plugin installation, portability across different installation locations, and end-to-end plugin workflow. Verify `${CLAUDE_PLUGIN_ROOT}` resolves correctly and MCP server starts successfully.

**Acceptance Criteria**:
- [ ] Plugin installs successfully via marketplace: `/plugin install courier-mcp@vibe-garden`
- [ ] Plugin works regardless of installation directory (portability verified)
- [ ] `${CLAUDE_PLUGIN_ROOT}` variable resolves to correct plugin installation path
- [ ] MCP server starts successfully after plugin installation
- [ ] Launcher script (`courier.sh`) executes without errors
- [ ] Virtual environment activates correctly in launcher
- [ ] MCP tools (`get-messages`, `get-folders`) available after installation
- [ ] Setup Skill discoverable in Claude Code
- [ ] Setup Skill triggers on authentication errors
- [ ] Plugin version matches spec version (1.1.0)
- [ ] Documentation accessible from plugin directory
- [ ] Uninstall/reinstall works without issues
- [ ] Cross-platform compatibility tested (Linux, macOS, Windows if available)
- [ ] Test report documented: `docs/PLUGIN_INSTALLATION_TEST.md`

**Technical Details**:
- Files to create:
  - `courier-mcp/docs/PLUGIN_INSTALLATION_TEST.md` (test report)
- Files to test:
  - `.claude-plugin/plugin.json`
  - `servers/scripts/courier.sh`
  - `skills/courier-setup-helper/SKILL.md`
- Key considerations:
  - `${CLAUDE_PLUGIN_ROOT}` must resolve across different installation paths
  - Launcher script must handle paths correctly
  - Virtual environment must be relative to plugin root (or handled in launcher)
  - All plugin components must work after installation
- Related spec sections: AT-11, AT-12, AT-13 (Plugin acceptance tests)

**Testing Requirements**:
- Install plugin in multiple locations (test portability)
- Verify all paths resolve correctly
- Test MCP server startup
- Test Skill activation
- Document test results
- Verify plugin uninstall/reinstall

**Notes**:
- Critical for plugin distribution success
- Portability ensures plugin works for all users regardless of installation location
- Reference spec acceptance tests: AT-11 (installation), AT-12 (portability), AT-13 (Skill activation)

---

## Dependency Graph

```
TASK-001 (Project setup)
  ├── TASK-002 (Dependencies)
  ├── TASK-003 (Logging)
  │    ├── TASK-004 (Auth)
  │    │    ├── TASK-005 (Setup docs)
  │    │    │    └── TASK-021 (Setup Skill) ──→ TASK-023 (Plugin testing)
  │    │    └── TASK-006 (Label caching)
  │    │         ├── TASK-007 (Message list)
  │    │         │    └── TASK-008 (Concurrent fetch)
  │    │         │         ├── TASK-009 (Export formatting)
  │    │         │         │    └── TASK-010 (Filename collision)
  │    │         │         └── TASK-014 (Timeout wrapper)
  │    │         │              └── TASK-015 (Error recovery)
  │    ├── TASK-011 (Server setup)
  │    │    ├── TASK-012 (get-folders handler)
  │    │    └── TASK-013 (get-messages handler)
  │    │         └── TASK-016 (Test suite)
  │    │              └── TASK-017 (E2E testing)
  │    │                   └── TASK-018 (Documentation)
  │    │                        └── TASK-019 (Polish)
  │    └── TASK-020 (Plugin manifest)
  │         ├── TASK-021 (Setup Skill)
  │         ├── TASK-022 (Marketplace registration) ──→ TASK-023 (Plugin testing)
  │         └── TASK-023 (Plugin testing)
```

## Implementation Order

**Phase 1: Foundation** (can be done in parallel)
- TASK-001: Project setup
- TASK-002: Dependencies
- TASK-003: Logging framework

**Phase 2: Authentication & Configuration** (after Phase 1)
- TASK-004: OAuth credential management
- TASK-005: Setup guide documentation
- TASK-006: Label caching

**Phase 3: Gmail Service** (after Phase 2 complete)
- TASK-007: Message list fetching
- TASK-008: Concurrent message fetching
- TASK-014: Timeout wrapper
- TASK-015: Error recovery

**Phase 4: Export & Formatting** (after Phase 3)
- TASK-009: Markdown export formatting
- TASK-010: Filename collision prevention

**Phase 5: Tool Handlers & Integration** (after Phase 4)
- TASK-011: MCP server setup
- TASK-012: get-folders handler
- TASK-013: get-messages handler (main orchestrator)

**Phase 6: Testing & Validation** (after Phase 5)
- TASK-016: Unit & integration tests
- TASK-017: E2E testing & performance

**Phase 7: Documentation & Release** (after Phase 6)
- TASK-018: Documentation & examples
- TASK-019: Error messages & polish

**Phase 8: Plugin Distribution (v1.1.0)** (can be done in parallel with Phase 1-7, but depends on TASK-001 and TASK-005)
- TASK-020: Plugin manifest & directory structure (after TASK-001)
- TASK-021: Setup assistance Skill (after TASK-005, TASK-020)
- TASK-022: Marketplace registration (after TASK-020)
- TASK-023: Plugin portability testing (after TASK-020, TASK-021, TASK-022)

## Acceptance Test Mapping

Maps specification acceptance tests (spec lines 244-255) to task tests:

**Spec Test 1: Basic retrieval** (10 unread emails → 10 markdown files)
- Covered by: TASK-013 (get-messages), TASK-009 (formatting), TASK-010 (filenames)
- Test files: `tests/test_acceptance.py::test_basic_retrieval`

**Spec Test 2: Search syntax** (from:boss, subject:[VOICE])
- Covered by: TASK-007 (search query building)
- Test files: `tests/test_gmail_service.py::test_search_queries`

**Spec Test 3: Date filtering** (date range Oct 1-15)
- Covered by: TASK-007 (date filter building), TASK-013 (date_start/end params)
- Test files: `tests/test_gmail_service.py::test_date_filtering`

**Spec Test 4: No overwrites** (second export uses _1, _2 suffixes)
- Covered by: TASK-010 (collision detection)
- Test files: `tests/test_export.py::test_collision_prevention`, `tests/test_acceptance.py::test_no_overwrites`

**Spec Test 5: Rate limit handling** (100 emails in <20s)
- Covered by: TASK-007 (backoff), TASK-008 (concurrency), TASK-014 (timeout)
- Test files: `tests/test_acceptance.py::test_rate_limit_handling`, `tests/test_integration.py`

**Spec Test 6: Attachment metadata** (list with size/MIME, no binary)
- Covered by: TASK-008 (fetch details), TASK-009 (format attachments)
- Test files: `tests/test_export.py::test_attachment_metadata`

**Spec Test 7: Folder discovery** (get-folders returns list with counts)
- Covered by: TASK-006 (label fetching), TASK-012 (get-folders handler)
- Test files: `tests/test_server.py::test_get_folders`, `tests/test_acceptance.py::test_folder_discovery`

**Spec Test 8: Timeout resilience** (files saved so far + error message)
- Covered by: TASK-014 (timeout wrapper), TASK-015 (error recovery)
- Test files: `tests/test_acceptance.py::test_timeout_resilience`

**Spec Test 9: Context efficiency** (concise output, no full bodies)
- Covered by: TASK-013 (tool output), TASK-019 (output formatting)
- Test files: `tests/test_server.py::test_output_format`

**Spec Test 10: Empty results** (no matches → empty array with summary)
- Covered by: TASK-013 (get-messages), TASK-017 (E2E testing)
- Test files: `tests/test_acceptance.py::test_empty_results`

**Spec Test 11 (v1.1.0): Plugin installation** (install via marketplace)
- Covered by: TASK-020 (plugin manifest), TASK-022 (marketplace registration), TASK-023 (installation testing)
- Test files: `docs/PLUGIN_INSTALLATION_TEST.md`

**Spec Test 12 (v1.1.0): Plugin portability** (`${CLAUDE_PLUGIN_ROOT}` resolves correctly)
- Covered by: TASK-020 (plugin manifest), TASK-023 (portability testing)
- Test files: `docs/PLUGIN_INSTALLATION_TEST.md`

**Spec Test 13 (v1.1.0): Setup assistance Skill** (auto-activation on auth failures)
- Covered by: TASK-021 (setup Skill), TASK-023 (Skill testing)
- Test files: `skills/courier-setup-helper/SKILL.md`, `docs/PLUGIN_INSTALLATION_TEST.md`

**Spec Test 14 (v1.1.0): Marketplace registration** (discoverable in vibe-garden)
- Covered by: TASK-022 (marketplace registration)
- Test files: `.claude-plugin/marketplace.json` (vibe-garden root)

## Risk Mitigation Tasks

Addressing risks identified in plan (page 521-530):

**Risk: Gmail API rate limit prevents completion**
- Mitigation Task: TASK-007, TASK-008, TASK-014, TASK-015
- Validation: TASK-17 (performance tests with 100 emails)

**Risk: OAuth token expires during export**
- Mitigation Task: TASK-004 (token refresh)
- Validation: Unit tests for token refresh, integration tests

**Risk: User credentials leak if .env committed**
- Mitigation Task: TASK-005 (security guidance in setup docs)
- Validation: Review .gitignore, document best practices

**Risk: Message body encoding issues**
- Mitigation Task: TASK-009 (html2text conversion)
- Validation: TASK-16, TASK-17 (test with various email types)

**Risk: File system permissions block export**
- Mitigation Task: TASK-010 (check write permissions)
- Validation: TASK-16 (test permission errors)

**Risk: Timeout too aggressive**
- Mitigation Task: TASK-001 (configurable via COURIER_TIMEOUT_SECONDS)
- Validation: TASK-17 (performance tests)

## Definition of Done

A task is complete when:
- [ ] All acceptance criteria are met
- [ ] Code is written and passes linting (black, pylint)
- [ ] Tests are written and passing
- [ ] Code is reviewed and approved
- [ ] PR is merged to main branch
- [ ] Task status is updated below
- [ ] No regressions in other tasks

## Progress Tracking

| Task ID | Status | PR | Notes |
|---------|--------|----|----|
| TASK-001 | Complete | - | Project setup & config |
| TASK-002 | Complete | - | Dependencies & venv |
| TASK-003 | Complete | - | Logging & errors |
| TASK-004 | Complete | - | OAuth 2.0 auth |
| TASK-005 | Complete | - | SETUP.md docs |
| TASK-006 | Complete | - | Label caching |
| TASK-007 | Complete | - | Message fetch with rate limiting |
| TASK-008 | Complete | - | Concurrent fetch & timeout |
| TASK-009 | Complete | - | Markdown export formatting |
| TASK-010 | Complete | - | Filename collision prevention |
| TASK-011 | Complete | - | MCP server setup |
| TASK-012 | Complete | - | get-folders handler |
| TASK-013 | Complete | - | get-messages handler |
| TASK-014 | Complete | - | Global timeout wrapper |
| TASK-015 | Complete | - | Error recovery & retries |
| TASK-016 | Not Started | - | Unit & integration tests |
| TASK-017 | Not Started | - | E2E & performance tests |
| TASK-018 | Not Started | - | Documentation & examples |
| TASK-019 | Not Started | - | Error polish & final QA |
| TASK-020 | Not Started | - | v1.1.0 Plugin manifest |
| TASK-021 | Not Started | - | v1.1.0 Setup Skill |
| TASK-022 | Not Started | - | v1.1.0 Marketplace |
| TASK-023 | Not Started | - | v1.1.0 Plugin testing |

**Status Options**: Not Started | In Progress | Blocked | In Review | Complete

## Resolved Questions

- [x] **Multiple Gmail accounts**: Defer to future versions. Noted as "likely never" due to scope/complexity. v1.0 focused on single user per instance per spec.
- [x] **Thread/conversation grouping**: Defer to v2.0+. Already documented as "Potential Future Features" in spec. No threading logic in v1.0; can be added if users request grouped exports later.
- [x] **Markdown file size limit**: 10KB limit per file in `courier.config`. If message body exceeds 10KB, split across multiple markdown files or truncate with note. Config key: `COURIER_MAX_FILE_SIZE_KB: 10`
- [x] **Automatic retry on network failures**: Yes, implement with exponential backoff. Retry attempts: 3 (configurable). Backoff factor: 2 (configurable). Applies to transient errors (timeout, connection refused, 503) but NOT permanent errors (401, 403, 400).

---

## Version History

### v1.1.0 (2025-10-19)
**Added Plugin Distribution and Setup Assistance Tasks**

Added 4 new tasks to align with spec v1.1.0:
- **TASK-020**: Plugin manifest and directory structure for Claude Code plugin packaging
- **TASK-021**: Setup assistance Skill for automatic OAuth troubleshooting
- **TASK-022**: Marketplace registration in vibe-garden repository
- **TASK-023**: Plugin portability and installation testing

**Updated Estimates**:
- Total tasks: 19 → 23
- Estimated timeline: ~38 hours → ~43 hours (added ~5 hours for v1.1.0)

**New Implementation Phase**:
- Phase 8 added for plugin distribution tasks
- Can be done in parallel with core implementation after TASK-001 and TASK-005

**Acceptance Test Mapping Extended**:
- AT-11: Plugin installation via marketplace
- AT-12: Plugin portability with `${CLAUDE_PLUGIN_ROOT}`
- AT-13: Setup Skill auto-activation on auth failures
- AT-14: Marketplace registration and discoverability

### v1.0.0 (2025-10-18)
- Initial task breakdown for Courier MCP spec v1.0.0
- 19 tasks across 7 implementation phases
- Comprehensive acceptance test mapping for all spec requirements

---

**Next Phase**: Begin implementation with Phase 1 tasks (TASK-001, TASK-002, TASK-003) in parallel. Use `/implementation` to track progress and execute tasks one by one.
