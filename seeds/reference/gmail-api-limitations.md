# Gmail API Limitations, Quotas & Error Handling

## Rate Limits & Quotas

### Per-Project Daily Quota

- **Limit**: 1,000,000,000 quota units per day
- **Error Code**: HTTP 403 with `dailyLimitExceeded`
- **Applies To**: All requests from your application across all users

### Per-User Rate Limit

- **Limit**: 250 quota units per user per second (as moving average)
- **Allows**: Short bursts above 250
- **Error Code**: HTTP 429 or 403 with `userRateLimitExceeded`
- **Applies To**: Individual authenticated user

### Quota Unit Consumption

Different methods consume different amounts of quota:

| Method | Cost |
|--------|------|
| `labels.list` | 1 |
| `labels.get` | 1 |
| `messages.list` | 1 |
| `messages.get` | 5 |
| `messages.attachments.get` | 1 |
| `threads.list` | 1 |
| `threads.get` | 5 |
| `history.list` | 1 |
| `users.getProfile` | 1 |
| `users.drafts.send` | 100 |

### Batch Request Considerations

- **Recommended batch size**: Up to 50 requests per batch
- **Larger batches**: May trigger rate limiting
- **Each batch**: Counts as separate API calls for quota

### Quota Monitoring

Check quota usage in Google Cloud Console:
1. Go to "APIs & Services" → "Quotas"
2. Look for "Gmail API"
3. View usage graphs and peak rates

---

## HTTP Status Codes & Error Responses

### 400 Bad Request

**Causes**:
- Invalid query syntax
- Missing required parameter
- Invalid format specified
- Malformed JSON in request body

**Example**:
```json
{
  "error": {
    "code": 400,
    "message": "Invalid value for: string parameter [q]: 'invalid[query'",
    "errors": [
      {
        "message": "Invalid value for: string parameter [q]: 'invalid[query'",
        "domain": "global",
        "reason": "invalid"
      }
    ]
  }
}
```

**Recovery**: Fix request parameters and retry

### 401 Unauthorized

**Causes**:
- Missing OAuth token
- Invalid/expired token
- Missing Authorization header

**Example**:
```json
{
  "error": {
    "code": 401,
    "message": "Invalid Credentials",
    "errors": [
      {
        "message": "Invalid Credentials",
        "domain": "global",
        "reason": "authenticationRequired"
      }
    ]
  }
}
```

**Recovery**:
1. Re-authenticate user
2. Get new access token
3. Refresh expired token using refresh_token

### 403 Forbidden

**Most common for Gmail API**

#### Insufficient Permission
```json
{
  "error": {
    "code": 403,
    "message": "Insufficient Permission",
    "errors": [
      {
        "message": "Insufficient Permission",
        "domain": "global",
        "reason": "insufficientPermissions"
      }
    ]
  }
}
```

**Causes**:
- Token doesn't have required scope
- User revoked access
- Scope not granted during OAuth flow

**Recovery**:
1. Check requested scopes in code
2. Delete stored credentials/tokens
3. Force user to re-authenticate with correct scopes

#### Rate Limit Exceeded
```json
{
  "error": {
    "code": 403,
    "message": "Rate Limit Exceeded",
    "errors": [
      {
        "message": "Rate Limit Exceeded",
        "domain": "usageLimits",
        "reason": "rateLimitExceeded"
      }
    ]
  }
}
```

**Causes**: User exceeded 250 quota units/second

**Recovery**: Implement exponential backoff

#### Quota Exceeded (Daily)
```json
{
  "error": {
    "code": 403,
    "message": "Quota exceeded for quota metric 'Daily usage' and limit 'Daily usage per 100 sec per user' of service 'gmail.googleapis.com' for consumer 'projects/PROJECT_ID'.",
    "errors": [
      {
        "message": "...",
        "domain": "usageLimits",
        "reason": "dailyLimitExceeded"
      }
    ]
  }
}
```

**Causes**: Daily project quota exhausted

**Recovery**: Wait until next day or request quota increase

### 404 Not Found

**Causes**:
- Message ID doesn't exist
- Label ID doesn't exist
- Attachment not found

**Example**:
```json
{
  "error": {
    "code": 404,
    "message": "Not Found",
    "errors": [
      {
        "message": "Not Found",
        "domain": "global",
        "reason": "notFound"
      }
    ]
  }
}
```

**Recovery**: Validate IDs before requests, handle gracefully

### 429 Too Many Requests

**Causes**: Aggressive request rate (usually 429 before 403)

**Recovery**: Implement exponential backoff

### 500 Internal Server Error

**Causes**: Temporary server issue

**Example**:
```json
{
  "error": {
    "code": 500,
    "message": "Backend Error",
    "errors": [
      {
        "message": "Backend Error",
        "domain": "global",
        "reason": "backendError"
      }
    ]
  }
}
```

**Recovery**: Retry with exponential backoff

### 503 Service Unavailable

**Causes**: API temporarily down for maintenance

**Recovery**: Retry with longer backoff

---

## API Limitations

### Message Retrieval Limits

| Aspect | Limit | Notes |
|--------|-------|-------|
| Max messages per list call | 500 | Use pagination for more |
| Max results parameter | 500 | Larger values ignored |
| Default results | 100 | If maxResults not specified |
| Message size | ~100MB | Very large attachments may fail |
| Total per user | 15GB | Mailbox size limit |

### Search Query Limits

| Aspect | Limit | Notes |
|--------|-------|-------|
| Query length | 2048 characters | Gmail web search limit |
| Operators supported | See Gmail search syntax | Not all Gmail web operators supported |
| Results returned | Up to 500 at a time | Paginate for more |
| Complex queries | May slow API | Limit use of OR, multiple operators |

### Attachment Limits

| Aspect | Limit | Notes |
|--------|-------|-------|
| Max attachment size | 25MB | Gmail web limit |
| File types blocked | Various | Executable files, etc. |
| Download single attachment | Via separate call | Gets one attachment by ID |
| Attachment metadata | Always available | But filename may not be |

### Thread Limits

| Aspect | Limit | Notes |
|--------|-------|-------|
| Messages per thread | Unlimited | Large threads may timeout |
| Threads to retrieve | 500 per call | Use pagination |
| Thread history | Limited | Very old messages may be affected |

---

## Feature Limitations

### What Gmail API Can Do

✅ Read emails
✅ List messages and threads
✅ Manage labels (create, update, delete - with right scope)
✅ Access attachments
✅ Track mailbox changes via history
✅ Send emails (with gmail.send scope)
✅ Create drafts
✅ Mark messages (read/unread, starred, etc.)

### What Gmail API Cannot Do

❌ Permanently delete messages (can move to trash)
❌ Create filters/rules
❌ Manage forwarding addresses
❌ Modify advanced settings
❌ Access Google Meet recordings
❌ Access Google Chat
❌ Backup entire mailbox to external service
❌ Bulk operations on thousands of messages simultaneously

---

## Common Error Scenarios & Solutions

### Scenario 1: Token Expired After Setup

**Error**:
```
401 Unauthorized - Invalid Credentials
```

**Cause**: Access token expires after 1 hour

**Solution**:
```python
from google.auth.transport.requests import Request

def refresh_token_if_needed(credentials):
    """Check and refresh token."""
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return credentials
```

### Scenario 2: User Revoked Access

**Error**:
```
403 Forbidden - Insufficient Permission
```

**Cause**: User revoked app access in Google Account settings

**Solution**:
1. Detect the error
2. Prompt user to re-authorize
3. Delete stored credentials
4. Redirect to OAuth flow

### Scenario 3: Quota Limit Hit

**Error**:
```
429 Too Many Requests or 403 Rate Limit Exceeded
```

**Cause**: Exceeding 250 quota units/second per user

**Solution**:
```python
import time
import random

def retry_with_backoff(func, max_retries=5):
    """Retry with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if getattr(e.resp, 'status', None) in [429, 500, 503]:
                if attempt < max_retries - 1:
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait)
                    continue
            raise
```

### Scenario 4: Invalid Message ID

**Error**:
```
404 Not Found
```

**Cause**: Message ID doesn't exist or was deleted

**Solution**:
```python
try:
    message = service.users().messages().get(
        userId='me',
        id=message_id
    ).execute()
except HttpError as e:
    if e.resp.status == 404:
        print("Message not found")
    else:
        raise
```

### Scenario 5: Insufficient Scope

**Error**:
```
403 Forbidden - Insufficient Permission
```

**Cause**: Token doesn't have required scope

**Solution**:
1. Check required scopes for operation:
   - List/get messages: `gmail.readonly` or `gmail.metadata`
   - Modify labels: `gmail.modify`

2. Delete stored token:
   ```bash
   rm token.pickle  # Python
   rm token.json    # Node.js
   ```

3. Re-authenticate with correct scopes:
   ```python
   SCOPES = [
       'https://www.googleapis.com/auth/gmail.readonly',
       'https://www.googleapis.com/auth/gmail.labels'
   ]
   ```

---

## Performance Considerations

### Optimization Strategies

1. **Use metadata format for headers only**
   ```python
   # Slow - unnecessary data
   message = service.users().messages().get(userId='me', id=msg_id).execute()

   # Fast - headers only
   message = service.users().messages().get(
       userId='me', id=msg_id, format='metadata',
       metadataHeaders=['From', 'Subject']
   ).execute()
   ```

2. **Batch related requests**
   ```python
   # Batch up to 100 messages (recommended ≤50)
   batch = service.new_batch_http_request()
   for msg_id in message_ids:
       batch.add(service.users().messages().get(userId='me', id=msg_id))
   batch.execute()
   ```

3. **Pagination for large result sets**
   ```python
   # Gets all 100 in one call
   results = service.users().messages().list(
       userId='me', maxResults=500
   ).execute()

   # Then use nextPageToken for subsequent pages
   ```

4. **Cache label mappings**
   ```python
   # Do once
   labels = service.users().labels().list(userId='me').execute()
   label_map = {l['id']: l['name'] for l in labels['labels']}

   # Reuse many times instead of calling API again
   label_name = label_map.get(label_id)
   ```

5. **Efficient search queries**
   ```python
   # Too broad - many results
   results = service.users().messages().list(
       userId='me', q='from:anyone'
   ).execute()

   # Better - specific criteria
   results = service.users().messages().list(
       userId='me',
       q='is:unread from:boss@company.com label:work'
   ).execute()
   ```

### Rate Limit Best Practices

1. **Monitor quota usage**: Check dashboard regularly
2. **Implement exponential backoff**: 1s → 2s → 4s → 8s → 16s
3. **Add jitter**: Prevent thundering herd
4. **Cache aggressively**: Avoid repeated API calls
5. **Batch requests**: Maximum 100 per batch
6. **Spread load**: Don't process all at once
7. **Handle 429/403 gracefully**: Implement retry logic

---

## Testing Recommendations

### Test Rate Limiting

```python
import time

def test_rate_limits():
    """Test rate limit behavior."""
    start = time.time()
    for i in range(300):  # Will hit rate limit
        try:
            service.users().messages().list(userId='me', maxResults=1).execute()
        except Exception as e:
            if hasattr(e, 'resp') and e.resp.status == 429:
                elapsed = time.time() - start
                print(f"Rate limited after {i} requests in {elapsed:.1f}s")
                break
```

### Test Quota Consumption

```python
def estimate_quota(message_count):
    """Estimate quota for operations."""
    # List messages: 1 unit each
    list_quota = 1

    # Get each message full: 5 units each
    get_quota = message_count * 5

    # Total
    total = list_quota + get_quota
    per_day_budget = 1_000_000_000

    percentage = (total / per_day_budget) * 100
    print(f"Quota for {message_count} messages: {total} units ({percentage:.6f}%)")
```

### Test with Mocking

```python
from unittest.mock import Mock, patch

def test_message_processing():
    """Test without making real API calls."""
    with patch('googleapiclient.discovery.build') as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service

        # Setup mock responses
        mock_service.users().messages().list().execute.return_value = {
            'messages': [{'id': 'test_id'}]
        }

        # Test code...
```

---

## Quota Increase Request

If you need more quota:

1. Go to Google Cloud Console
2. APIs & Services → Quotas
3. Select Gmail API
4. Click "EDIT QUOTAS"
5. Increase desired limits
6. Submit justification:
   - Use case description
   - Expected request volume
   - Target audience size
7. Google reviews and approves

Typically reviewed within 2-3 business days.

---

## Migration from Deprecated APIs

If coming from IMAP/POP3:

- Gmail IMAP/POP3 is deprecated
- Use REST API (current version)
- Check quota unit consumption carefully
- IMAP was more efficient for some operations; REST is more flexible

---

## Support & Resources

### Getting Help

- **Errors in API**: Check Gmail API issue tracker
- **Authentication issues**: OAuth 2.0 docs
- **Query syntax**: Gmail search syntax documentation
- **Performance issues**: Quotas page in Cloud Console
- **Community**: Stack Overflow tag `gmail-api`

### Useful Links

- OAuth 2.0: https://developers.google.com/identity/protocols/oauth2
- Quotas: https://developers.google.com/workspace/gmail/api/reference/quota
- Error handling: https://developers.google.com/workspace/gmail/api/guides/handle-errors
- Search syntax: https://developers.google.com/workspace/gmail/api/guides/filtering
