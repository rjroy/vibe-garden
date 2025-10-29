# Gmail API Methods Reference

## Base URL
```
https://gmail.googleapis.com/gmail/v1/users/
```

All endpoints use `{userId}` where `me` represents the authenticated user.

---

## Messages API

### List Messages

**Endpoint**: `GET /users/{userId}/messages`

**Purpose**: List all messages in user's mailbox

**Common Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query (like Gmail search box) |
| `maxResults` | integer | Max messages to return (1-500, default 100) |
| `pageToken` | string | Page token from previous request |
| `labelIds` | string[] | Filter by label IDs (all must match) |
| `includeSpamTrash` | boolean | Include spam/trash (default false) |

**Example Query Operators**:
```
q=is:unread
q=from:sender@example.com
q=subject:important
q=newer_than:3d (newer than 3 days)
q=before:2025-01-01
q=filename:pdf
q=has:attachment
q=is:starred
q=label:custom-label-name
```

**Response**: Returns array of Message objects with `id` and `threadId` only

```json
{
  "messages": [
    {
      "id": "18a0b9e2d3c4e5f6",
      "threadId": "18a0b9e2d3c4e5f6"
    }
  ],
  "resultSizeEstimate": 42
}
```

**Quota Cost**: 1 unit per request

**Example - Python**:
```python
results = service.users().messages().list(
    userId='me',
    q='is:unread',
    maxResults=10
).execute()

for message in results.get('messages', []):
    print(f"Message ID: {message['id']}")
```

**Example - Node.js**:
```javascript
const results = await gmail.users.messages.list({
    userId: 'me',
    q: 'is:unread',
    maxResults: 10
});

for (const message of results.data.messages || []) {
    console.log(`Message ID: ${message.id}`);
}
```

---

### Get Message

**Endpoint**: `GET /users/{userId}/messages/{id}`

**Purpose**: Retrieve full message content

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Output format: `minimal`, `full`, `raw` (default: `full`) |
| `metadataHeaders` | string[] | With format=metadata, which headers to return |

**Format Options**:

- `minimal`: Only returns `id`, `threadId`, `labelIds`
- `full`: Complete message with `payload` containing headers and body
- `raw`: Base64url encoded RFC 2822 message
- `metadata`: Only specified headers (e.g., From, Subject, To)

**Response with format=full**:

```json
{
  "id": "18a0b9e2d3c4e5f6",
  "threadId": "18a0b9e2d3c4e5f6",
  "labelIds": ["INBOX", "CATEGORY_SOCIAL"],
  "internalDate": "1696272847000",
  "payload": {
    "partId": "",
    "mimeType": "multipart/mixed",
    "filename": "",
    "headers": [
      {
        "name": "From",
        "value": "sender@example.com"
      },
      {
        "name": "To",
        "value": "recipient@example.com"
      },
      {
        "name": "Subject",
        "value": "Hello World"
      },
      {
        "name": "Date",
        "value": "Mon, 2 Oct 2023 14:47:27 -0700"
      }
    ],
    "body": {
      "size": 5000,
      "data": "PEhUTUw+PEJPRFlePkhlbGxvIFdvcmxkPC9CT0RZPjwvSFRNTD4="
    },
    "parts": [
      {
        "partId": "0",
        "mimeType": "text/plain",
        "filename": "",
        "headers": [],
        "body": {
          "size": 145,
          "data": "R3JlZXRpbmdzIGZyb20gSmFjay4="
        }
      },
      {
        "partId": "1",
        "mimeType": "application/pdf",
        "filename": "document.pdf",
        "headers": [],
        "body": {
          "attachmentId": "ANGjdJ9N3U5N8Q9R1S2T3V4W5X6Y7Z"
        }
      }
    ]
  }
}
```

**Quota Cost**: 5 units per request

**Example - Python**:
```python
message = service.users().messages().get(
    userId='me',
    id='18a0b9e2d3c4e5f6',
    format='full'
).execute()

# Extract headers
headers = {}
for header in message['payload']['headers']:
    headers[header['name']] = header['value']

print(f"From: {headers.get('From')}")
print(f"Subject: {headers.get('Subject')}")
```

**Example - Node.js**:
```javascript
const message = await gmail.users.messages.get({
    userId: 'me',
    id: '18a0b9e2d3c4e5f6',
    format: 'full'
});

const headers = {};
for (const header of message.data.payload.headers) {
    headers[header.name] = header.value;
}

console.log(`From: ${headers['From']}`);
```

---

### Get Message Attachment

**Endpoint**: `GET /users/{userId}/messages/{messageId}/attachments/{id}`

**Purpose**: Download attachment from message

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `messageId` | string | Parent message ID |
| `id` | string | Attachment ID (from message payload) |

**Response**:

```json
{
  "size": 524288,
  "data": "JVBERi0xLjQKJeLjz9MNCjEgMCBvYmo..."
}
```

Data is base64url encoded.

**Quota Cost**: 1 unit per request

---

### Batch Get Messages

**Method**: `batchGet()`

**Purpose**: Retrieve multiple messages in single request (more efficient than individual calls)

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `ids` | string[] | Message IDs to retrieve (max 100) |
| `format` | string | Output format (default: `minimal`) |

**Important**: Batch requests up to 50 are recommended. Larger batches may trigger rate limiting.

**Example - Python**:
```python
message_ids = ['id1', 'id2', 'id3']

# Note: Gmail API doesn't have direct batchGet for messages
# Use individual gets or implement parallel requests
import concurrent.futures

def get_message(msg_id):
    return service.users().messages().get(
        userId='me',
        id=msg_id,
        format='minimal'
    ).execute()

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    messages = list(executor.map(get_message, message_ids))
```

---

## Labels API

### List Labels

**Endpoint**: `GET /users/{userId}/labels`

**Purpose**: List all labels in mailbox

**Parameters**: None

**Response**:

```json
{
  "labels": [
    {
      "id": "INBOX",
      "name": "INBOX",
      "messageListVisibility": "show",
      "labelListVisibility": "labelShowIfUnread",
      "type": "system"
    },
    {
      "id": "Label_1",
      "name": "Work",
      "messageListVisibility": "show",
      "labelListVisibility": "labelShow",
      "type": "user"
    }
  ]
}
```

**System Labels**:

| Label ID | Name | Description |
|----------|------|-------------|
| `INBOX` | Inbox | Unarchived messages |
| `SENT` | Sent Mail | Sent messages |
| `DRAFT` | Drafts | Draft messages |
| `STARRED` | Starred | Starred messages |
| `UNREAD` | Unread | Unread messages |
| `SPAM` | Spam | Spam messages |
| `TRASH` | Trash | Deleted messages |
| `IMPORTANT` | Important | Marked as important |
| `CATEGORY_PROMOTIONS` | Promotions | Auto-categorized promotions |
| `CATEGORY_SOCIAL` | Social | Auto-categorized social |
| `CATEGORY_UPDATES` | Updates | Auto-categorized updates |
| `CATEGORY_FORUMS` | Forums | Auto-categorized forums |
| `CATEGORY_PERSONAL` | Personal | Auto-categorized personal |

**Quota Cost**: 1 unit per request

**Example - Python**:
```python
results = service.users().labels().list(userId='me').execute()

label_map = {}
for label in results.get('labels', []):
    label_map[label['id']] = label['name']
    print(f"{label['name']} ({label['id']})")
```

---

### Get Label

**Endpoint**: `GET /users/{userId}/labels/{id}`

**Purpose**: Get single label details

**Response**: Single Label object (same format as list)

**Quota Cost**: 1 unit per request

---

## Threads API

### List Threads

**Endpoint**: `GET /users/{userId}/threads`

**Purpose**: List message threads (conversations)

**Parameters**: Same as messages.list()

**Response**: Array of Thread objects with `id` only

```json
{
  "threads": [
    {
      "id": "thread123",
      "snippet": "This is a snippet of the latest message..."
    }
  ]
}
```

---

### Get Thread

**Endpoint**: `GET /users/{userId}/threads/{id}`

**Purpose**: Get all messages in thread

**Query Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `format` | string | Output format: `minimal`, `full` |

**Response**: Thread object with messages array

```json
{
  "id": "thread123",
  "historyId": "123456",
  "messages": [
    {
      "id": "msg1",
      "threadId": "thread123",
      "payload": { ... }
    },
    {
      "id": "msg2",
      "threadId": "thread123",
      "payload": { ... }
    }
  ]
}
```

**Quota Cost**: 5 units per request

---

## History API

### List History

**Endpoint**: `GET /users/{userId}/history`

**Purpose**: Track changes to mailbox (new messages, label changes, etc.)

**Parameters**:

| Parameter | Type | Description |
|-----------|------|-------------|
| `startHistoryId` | string | Start from history ID |
| `maxResults` | integer | Max changes (default 100) |
| `labelId` | string | Only changes for this label |
| `historyTypes` | string[] | `messageAdded`, `messageDeleted`, `labelAdded`, `labelRemoved` |

**Response**:

```json
{
  "history": [
    {
      "id": "123456",
      "messages": [
        {
          "id": "msg1",
          "threadId": "thread1"
        }
      ],
      "labelsAdded": [
        {
          "message": { "id": "msg1" },
          "labelIds": ["STARRED"]
        }
      ]
    }
  ],
  "historyId": "654321"
}
```

**Quota Cost**: 1 unit per request

---

## Search Query Operators

Gmail search syntax supported in `q` parameter:

```
from:sender@example.com          # From specific sender
to:recipient@example.com          # To specific recipient
subject:keyword                   # Subject contains keyword
is:unread                          # Unread messages
is:read                            # Read messages
is:starred                         # Starred messages
is:sent                            # Sent messages
is:draft                           # Draft messages
has:attachment                     # Has attachments
filename:document.pdf              # Specific filename
before:2025-01-01                  # Before date
after:2024-12-01                   # After date
newer_than:7d                      # Newer than 7 days
older_than:30d                     # Older than 30 days
size:>1M                           # Size greater than 1MB
rfc822msgid:<msg-id>              # By message ID
label:label-name                   # By label name (spaces become dashes)
```

**Examples**:
```
q=is:unread from:boss@company.com
q=subject:invoice after:2025-01-01
q=has:attachment filename:pdf
q=label:work is:starred
```

---

## Response Pagination

Most list endpoints support pagination:

```python
# Python
page_token = None
all_messages = []

while True:
    results = service.users().messages().list(
        userId='me',
        pageToken=page_token
    ).execute()

    all_messages.extend(results.get('messages', []))

    page_token = results.get('nextPageToken')
    if not page_token:
        break
```

---

## Quota Consumption by Method

| Method | Quota Cost |
|--------|-----------|
| labels.list | 1 |
| labels.get | 1 |
| messages.list | 1 |
| messages.get | 5 |
| messages.attachments.get | 1 |
| threads.list | 1 |
| threads.get | 5 |
| history.list | 1 |
| users.getProfile | 1 |

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": 403,
    "message": "Quota exceeded for quota metric 'User-rate limit' and limit 'USER_RATE_LIMIT per user' of service 'gmail.googleapis.com' for consumer 'projects/PROJECT_ID'.",
    "errors": [
      {
        "message": "Quota exceeded for quota metric 'User-rate limit'...",
        "domain": "usageLimits",
        "reason": "userRateLimitExceeded"
      }
    ]
  }
}
```

---

## Efficient Retrieval Patterns

### Pattern 1: Get Latest Unread Messages
```python
messages = service.users().messages().list(
    userId='me',
    q='is:unread',
    maxResults=10
).execute()
```

### Pattern 2: Get Messages by Label
```python
messages = service.users().messages().list(
    userId='me',
    labelIds=['INBOX'],
    maxResults=50
).execute()
```

### Pattern 3: Get Message with All Content
```python
msg_list = service.users().messages().list(userId='me', maxResults=1).execute()
msg_id = msg_list['messages'][0]['id']

message = service.users().messages().get(
    userId='me',
    id=msg_id,
    format='full'
).execute()
```

### Pattern 4: Track Mailbox Changes
```python
# Get current history ID
profile = service.users().getProfile(userId='me').execute()
current_history_id = profile['historyId']

# Later, get changes since that point
history = service.users().history().list(
    userId='me',
    startHistoryId=current_history_id
).execute()
```
