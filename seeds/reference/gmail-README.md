# Gmail API Research & Reference

**Research Date**: October 2025
**Purpose**: Comprehensive documentation for building a Gmail MCP (Model Context Protocol) server

## Quick Start

If you're building an MCP server to retrieve emails from Gmail inbox, start here:

### 1. Understand the API
- Read: [`gmail-api-overview.md`](gmail-api-overview.md)
- Key concept: Gmail API is a REST API for reading/managing Gmail mailboxes
- For MCP inbox access: Use `gmail.readonly` or `gmail.metadata` scopes

### 2. Setup Authentication
- Read: [`gmail-api-authentication.md`](gmail-api-authentication.md)
- Choose method:
  - **OAuth 2.0** (if MCP serves interactive users)
  - **Service Account** (if MCP is a server backend)
- Create Google Cloud project and enable Gmail API
- Generate and securely store credentials

### 3. Learn Available Methods
- Read: [`gmail-api-methods.md`](gmail-api-methods.md)
- Key endpoints for inbox retrieval:
  - `users.messages.list()` - List messages
  - `users.messages.get()` - Get full message
  - `users.labels.list()` - List labels
  - `users.threads.get()` - Get conversation

### 4. Implement with Code Examples
- Read: [`gmail-api-implementation.md`](gmail-api-implementation.md)
- Complete Python and Node.js examples included
- Error handling patterns
- Performance optimization techniques

### 5. Handle Limitations & Quotas
- Read: [`gmail-api-limitations.md`](gmail-api-limitations.md)
- Per-user rate limit: 250 quota units/second
- Different methods consume different quota
- Common errors and recovery strategies

---

## File Guide

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **gmail-api-overview.md** | Architecture, concepts, data models | 10 min |
| **gmail-api-authentication.md** | Setup credentials, OAuth flow, scopes | 20 min |
| **gmail-api-methods.md** | API endpoints, parameters, responses | 15 min |
| **gmail-api-implementation.md** | Working code examples, best practices | 20 min |
| **gmail-api-limitations.md** | Quotas, errors, solutions | 15 min |

---

## For MCP Development

### MCP-Specific Considerations

1. **Tool vs Resource Design**
   - Consider if inbox retrieval should be a **resource** (reading mailbox) or **tool** (action)
   - For reading inbox: Likely a **resource** (queryable mailbox)

2. **Authentication Approach**
   - **User delegation (OAuth)**: Each user's own credentials
   - **Service account**: Single shared service account
   - **Hybrid**: Service account with domain-wide delegation

3. **MCP Tool Examples**

   **List Inbox Messages Tool**:
   ```
   Tool: get_messages
   Input: {
     q: "search query (optional)",
     maxResults: 10,
     format: "minimal|full"
   }
   Output: Array of messages with headers/content
   ```

   **Get Message Details Tool**:
   ```
   Tool: get_message_content
   Input: {
     messageId: "...",
     format: "full"
   }
   Output: Complete message with headers, body, attachments
   ```

   **Search Messages Tool**:
   ```
   Tool: search_inbox
   Input: {
     query: "is:unread from:boss@company.com",
     maxResults: 10
   }
   Output: Matching messages
   ```

4. **Rate Limit Handling in MCP**
   - Implement request queuing
   - Add exponential backoff for 429 errors
   - Monitor quota consumption
   - Inform Claude Code about rate limits

5. **Error Handling Strategy**
   - Handle 403 errors (permission/quota)
   - Handle 404 errors (message not found)
   - Handle 401 errors (token expired)
   - Provide meaningful error messages to Claude Code

---

## API Quick Reference

### Authentication
```
OAuth 2.0 + refresh tokens (interactive)
Service Account (background/server)
```

### Scopes
```
gmail.readonly       - Read-only full access (recommended)
gmail.metadata       - Headers only (lightweight)
gmail.modify         - Read + modify labels
```

### Main Endpoints
```
GET /users/{userId}/messages              # List messages (1 quota)
GET /users/{userId}/messages/{id}         # Get message (5 quota)
GET /users/{userId}/labels                # List labels (1 quota)
GET /users/{userId}/threads/{id}          # Get thread (5 quota)
```

### Rate Limits
```
Per-project: 1B quota units/day
Per-user: 250 quota units/second (average)
Recommended batch size: ≤50 requests
```

### Key Query Parameters
```
q=search_query                    # Gmail search syntax
maxResults=100                    # Results per page (1-500)
format=full|minimal|raw|metadata  # Response format
labelIds=INBOX                    # Filter by label
pageToken=...                     # Pagination
```

---

## Common Patterns for Inbox Retrieval

### Get Latest Unread Messages
```python
service.users().messages().list(
    userId='me',
    q='is:unread',
    maxResults=10
).execute()
```

### Get Messages with Attachments
```python
service.users().messages().list(
    userId='me',
    q='has:attachment',
    maxResults=20
).execute()
```

### Get Inbox Messages in Date Range
```python
service.users().messages().list(
    userId='me',
    q='after:2025-01-01 before:2025-02-01',
    maxResults=50
).execute()
```

### Search by Sender
```python
service.users().messages().list(
    userId='me',
    q='from:specific@email.com',
    maxResults=10
).execute()
```

### Get Full Message Content
```python
message = service.users().messages().get(
    userId='me',
    id=message_id,
    format='full'
).execute()

# Extract headers
for header in message['payload']['headers']:
    print(f"{header['name']}: {header['value']}")
```

---

## Setup Checklist for MCP Development

- [ ] Read gmail-api-overview.md
- [ ] Create Google Cloud project
- [ ] Enable Gmail API
- [ ] Choose authentication method (OAuth or Service Account)
- [ ] Configure OAuth consent screen
- [ ] Create and download credentials
- [ ] Test authentication in Python/Node.js
- [ ] Implement message retrieval functions
- [ ] Add error handling with retries
- [ ] Test rate limiting behavior
- [ ] Implement MCP tools/resources
- [ ] Document available MCP operations
- [ ] Add comprehensive error messages
- [ ] Test with real Gmail accounts
- [ ] Monitor quota usage during testing

---

## Key Insights

### Why Gmail API for MCP?

1. **Official & Stable**: Google-maintained, widely used
2. **Feature-Rich**: More than just email retrieval
3. **Well-Documented**: Extensive examples and guides
4. **Flexible**: OAuth for users or service accounts for servers
5. **Reliable**: Enterprise-grade API with SLAs

### Limitations to Keep in Mind

1. **Rate limits**: 250 units/second per user (can add up quickly)
2. **Batch size**: Don't exceed 100 per batch (50 recommended)
3. **Large attachments**: 25MB limit per file
4. **Message body encoding**: Base64url encoded, needs decoding
5. **Multipart messages**: Complex structure, need parsing

### Best Practices for MCP

1. **Cache labels**: Don't fetch labels on every request
2. **Pagination**: Always implement pageToken handling
3. **Minimal format**: Use `format=metadata` when possible
4. **Batch operations**: Group requests together
5. **Error recovery**: Implement exponential backoff
6. **Monitor quota**: Track consumption in your MCP
7. **User feedback**: Report rate limit/permission errors clearly
8. **Secure storage**: Never commit credentials
9. **Token refresh**: Handle automatic token expiration
10. **Test thoroughly**: Test with real Gmail accounts and rate limits

---

## Resources Used

- Official Google Workspace documentation
- Gmail API Reference: https://developers.google.com/gmail/api/reference/rest
- OAuth 2.0 Guide: https://developers.google.com/identity/protocols/oauth2
- Quotas Documentation: https://developers.google.com/workspace/gmail/api/reference/quota
- Community resources and tutorials

---

## Next Steps

1. **Start with Authentication**: Follow the detailed setup in `gmail-api-authentication.md`
2. **Write Test Code**: Use examples from `gmail-api-implementation.md` to test access
3. **Design MCP Interface**: Decide what tools/resources Claude Code needs
4. **Implement Core Functions**: Build message retrieval, searching, filtering
5. **Handle Errors**: Implement retry logic and user-friendly error messages
6. **Performance Test**: Verify behavior under rate limiting
7. **Document**: Create MCP documentation for end users

---

## Contact & Support

For issues with:
- **Gmail API**: Check official docs or Stack Overflow tag `gmail-api`
- **OAuth flow**: Consult Google Identity docs
- **Rate limiting**: Check Cloud Console quotas page
- **MCP integration**: Refer to MCP documentation

---

**Last Updated**: October 18, 2025
**Status**: Research Complete - Ready for Implementation
