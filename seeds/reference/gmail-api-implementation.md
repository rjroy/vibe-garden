# Gmail API Implementation Guide

## Installation

### Python

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Node.js / TypeScript

```bash
npm install googleapis
# For TypeScript
npm install --save-dev @types/googleapis
```

---

## Complete Examples

### Python: List and Read Inbox

```python
#!/usr/bin/env python3
"""Gmail API client to read inbox messages."""

import pickle
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate():
    """Authenticate user and return Gmail service."""
    creds = None

    # Load existing credentials
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service


def get_labels(service):
    """Get all labels in mailbox."""
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    label_map = {}
    for label in labels:
        label_map[label['id']] = label['name']
        print(f"Label: {label['name']} (ID: {label['id']})")

    return label_map


def get_message_headers(service, message_id):
    """Get headers from a message."""
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='metadata',
        metadataHeaders=['From', 'To', 'Subject', 'Date']
    ).execute()

    headers = {}
    for header in message['payload']['headers']:
        headers[header['name']] = header['value']

    return headers


def decode_message_body(payload):
    """Decode message body from payload."""
    if 'parts' in payload:
        # Multipart message - look for text part
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    return base64.urlsafe_b64decode(
                        part['body']['data']).decode('utf-8')
    else:
        # Single part message
        if 'body' in payload and 'data' in payload['body']:
            return base64.urlsafe_b64decode(
                payload['body']['data']).decode('utf-8')

    return None


def get_message_full(service, message_id):
    """Get full message content."""
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    headers = {}
    for header in message['payload']['headers']:
        headers[header['name']] = header['value']

    body = decode_message_body(message['payload'])

    return {
        'id': message['id'],
        'headers': headers,
        'body': body,
        'internalDate': message.get('internalDate'),
        'labelIds': message.get('labelIds', [])
    }


def get_inbox_messages(service, max_results=10):
    """Get recent messages from inbox."""
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    print(f"Found {len(messages)} messages in inbox\n")

    for message in messages:
        headers = get_message_headers(service, message['id'])
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', '(No Subject)')}")
        print(f"Date: {headers.get('Date', 'Unknown')}")
        print(f"ID: {message['id']}")
        print("---")


def search_messages(service, query, max_results=10):
    """Search messages with Gmail query syntax."""
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

    messages = results.get('messages', [])
    print(f"Search '{query}' found {len(messages)} messages\n")

    for message in messages:
        headers = get_message_headers(service, message['id'])
        print(f"From: {headers.get('From', 'Unknown')}")
        print(f"Subject: {headers.get('Subject', '(No Subject)')}")
        print("---")


def main():
    """Main function."""
    print("Gmail API Client\n")

    service = authenticate()

    # Get labels
    print("\n=== LABELS ===")
    labels = get_labels(service)

    # Get inbox messages
    print("\n=== INBOX MESSAGES ===")
    get_inbox_messages(service, max_results=5)

    # Search for unread messages
    print("\n=== UNREAD MESSAGES ===")
    search_messages(service, 'is:unread', max_results=5)

    # Get specific message details
    print("\n=== DETAILED MESSAGE ===")
    results = service.users().messages().list(
        userId='me',
        maxResults=1
    ).execute()

    if results.get('messages'):
        message_id = results['messages'][0]['id']
        full_message = get_message_full(service, message_id)
        print(f"ID: {full_message['id']}")
        print(f"From: {full_message['headers'].get('From')}")
        print(f"Subject: {full_message['headers'].get('Subject')}")
        print(f"Body Preview: {full_message['body'][:200] if full_message['body'] else 'No body'}")


if __name__ == '__main__':
    main()
```

---

### Node.js / TypeScript: List and Read Inbox

```javascript
/**
 * Gmail API client to read inbox messages
 */

const fs = require('fs').promises;
const path = require('path');
const { google } = require('googleapis');

const SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'];
const TOKEN_PATH = path.join(process.cwd(), 'token.json');

/**
 * Load or request or refresh the access token
 */
async function authorize() {
  const auth = new google.auth.GoogleAuth({
    keyFile: 'credentials.json',
    scopes: SCOPES,
  });

  const authClient = await auth.getClient();
  return authClient;
}

/**
 * Get all labels
 */
async function getLabels(gmail) {
  const result = await gmail.users.labels.list({ userId: 'me' });

  const labels = {};
  for (const label of result.data.labels || []) {
    labels[label.id] = label.name;
    console.log(`Label: ${label.name} (ID: ${label.id})`);
  }

  return labels;
}

/**
 * Get message headers
 */
async function getMessageHeaders(gmail, messageId) {
  const message = await gmail.users.messages.get({
    userId: 'me',
    id: messageId,
    format: 'metadata',
    metadataHeaders: ['From', 'To', 'Subject', 'Date']
  });

  const headers = {};
  for (const header of message.data.payload.headers) {
    headers[header.name] = header.value;
  }

  return headers;
}

/**
 * Decode message body from payload
 */
function decodeBody(payload) {
  if (payload.parts) {
    // Multipart message
    for (const part of payload.parts) {
      if (part.mimeType === 'text/plain' && part.body.data) {
        return Buffer.from(part.body.data, 'base64').toString('utf8');
      }
    }
  } else if (payload.body && payload.body.data) {
    // Single part
    return Buffer.from(payload.body.data, 'base64').toString('utf8');
  }

  return null;
}

/**
 * Get full message with content
 */
async function getFullMessage(gmail, messageId) {
  const message = await gmail.users.messages.get({
    userId: 'me',
    id: messageId,
    format: 'full'
  });

  const headers = {};
  for (const header of message.data.payload.headers) {
    headers[header.name] = header.value;
  }

  const body = decodeBody(message.data.payload);

  return {
    id: message.data.id,
    headers,
    body,
    internalDate: message.data.internalDate,
    labelIds: message.data.labelIds || []
  };
}

/**
 * Get inbox messages
 */
async function getInboxMessages(gmail, maxResults = 10) {
  const result = await gmail.users.messages.list({
    userId: 'me',
    labelIds: ['INBOX'],
    maxResults
  });

  const messages = result.data.messages || [];
  console.log(`\nFound ${messages.length} messages in inbox\n`);

  for (const message of messages) {
    const headers = await getMessageHeaders(gmail, message.id);
    console.log(`From: ${headers.From || 'Unknown'}`);
    console.log(`Subject: ${headers.Subject || '(No Subject)'}`);
    console.log(`Date: ${headers.Date || 'Unknown'}`);
    console.log(`ID: ${message.id}`);
    console.log('---');
  }
}

/**
 * Search messages with Gmail query
 */
async function searchMessages(gmail, query, maxResults = 10) {
  const result = await gmail.users.messages.list({
    userId: 'me',
    q: query,
    maxResults
  });

  const messages = result.data.messages || [];
  console.log(`\nSearch '${query}' found ${messages.length} messages\n`);

  for (const message of messages) {
    const headers = await getMessageHeaders(gmail, message.id);
    console.log(`From: ${headers.From || 'Unknown'}`);
    console.log(`Subject: ${headers.Subject || '(No Subject)'}`);
    console.log('---');
  }
}

/**
 * Main function
 */
async function main() {
  console.log('Gmail API Client\n');

  const auth = await authorize();
  const gmail = google.gmail({ version: 'v1', auth });

  // Get labels
  console.log('=== LABELS ===');
  const labels = await getLabels(gmail);

  // Get inbox messages
  console.log('\n=== INBOX MESSAGES ===');
  await getInboxMessages(gmail, 5);

  // Search unread
  console.log('\n=== UNREAD MESSAGES ===');
  await searchMessages(gmail, 'is:unread', 5);

  // Get detailed message
  console.log('\n=== DETAILED MESSAGE ===');
  const result = await gmail.users.messages.list({
    userId: 'me',
    maxResults: 1
  });

  if (result.data.messages && result.data.messages.length > 0) {
    const messageId = result.data.messages[0].id;
    const fullMessage = await getFullMessage(gmail, messageId);

    console.log(`ID: ${fullMessage.id}`);
    console.log(`From: ${fullMessage.headers.From}`);
    console.log(`Subject: ${fullMessage.headers.Subject}`);
    if (fullMessage.body) {
      console.log(`Body Preview: ${fullMessage.body.substring(0, 200)}`);
    }
  }
}

main().catch(console.error);
```

---

## Error Handling

### Retry with Exponential Backoff

```python
import time
import random

def api_call_with_retry(api_func, max_retries=5):
    """Execute API call with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            return api_func()
        except Exception as e:
            error_code = getattr(e, 'resp', {}).status if hasattr(e, 'resp') else None

            # Retry on 429 (rate limit) or 500 (server error)
            if error_code in [429, 500] and attempt < max_retries - 1:
                # Exponential backoff with jitter
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited or server error. Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
            else:
                raise

# Usage
try:
    result = api_call_with_retry(
        lambda: service.users().messages().list(userId='me').execute()
    )
except Exception as e:
    print(f"API call failed: {e}")
```

### Handle Common Errors

```python
from googleapiclient.errors import HttpError

def safe_get_message(service, message_id):
    """Get message with error handling."""
    try:
        message = service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()
        return message

    except HttpError as error:
        error_code = error.resp.status

        if error_code == 404:
            print(f"Message {message_id} not found")
        elif error_code == 403:
            print("Permission denied - check scopes")
        elif error_code == 429:
            print("Rate limit exceeded - back off")
        elif error_code == 500:
            print("Server error - retry later")
        else:
            print(f"Error {error_code}: {error.content}")

        return None
```

---

## Performance Optimization

### Batch Requests

```python
from googleapiclient.http import BatchHttpRequest

def get_multiple_messages(service, message_ids):
    """Get multiple messages efficiently."""
    batch = service.new_batch_http_request()
    messages = {}

    def callback(request_id, response, exception):
        if exception is None:
            messages[request_id] = response
        else:
            print(f"Error retrieving message: {exception}")

    # Add requests to batch (max 100 per batch)
    for msg_id in message_ids[:100]:
        batch.add(
            service.users().messages().get(
                userId='me',
                id=msg_id,
                format='minimal'
            ),
            callback=callback,
            request_id=msg_id
        )

    batch.execute()
    return messages
```

### Pagination Loop

```python
def get_all_messages_paginated(service, query=None, max_total=None):
    """Get all messages with pagination."""
    page_token = None
    count = 0

    while True:
        try:
            results = service.users().messages().list(
                userId='me',
                q=query,
                pageToken=page_token,
                maxResults=500  # Max allowed
            ).execute()

            for message in results.get('messages', []):
                yield message
                count += 1
                if max_total and count >= max_total:
                    return

            page_token = results.get('nextPageToken')
            if not page_token:
                break

        except Exception as e:
            print(f"Error: {e}")
            break

# Usage
for message in get_all_messages_paginated(service, query='has:attachment'):
    print(f"Processing message {message['id']}")
    if count >= 1000:
        break
```

---

## Message Body Extraction

### Extract Text from Complex Multipart Messages

```python
def extract_text_from_message(message):
    """Extract all text content from message."""
    texts = []

    def process_payload(payload):
        if payload.get('mimeType') == 'text/plain':
            if 'data' in payload.get('body', {}):
                text = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
                texts.append(text)

        elif payload.get('mimeType') == 'text/html':
            # Could parse HTML here
            pass

        if 'parts' in payload:
            for part in payload['parts']:
                process_payload(part)

    process_payload(message['payload'])
    return '\n'.join(texts)
```

---

## Attachment Handling

### List Attachments

```python
def get_attachments_info(service, message_id):
    """Get info about attachments without downloading."""
    message = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()

    attachments = []

    def process_parts(parts):
        for part in parts:
            if part.get('filename'):
                attachments.append({
                    'filename': part['filename'],
                    'mimeType': part.get('mimeType'),
                    'size': part.get('body', {}).get('size'),
                    'attachmentId': part.get('body', {}).get('attachmentId')
                })

            if 'parts' in part:
                process_parts(part['parts'])

    if 'parts' in message['payload']:
        process_parts(message['payload']['parts'])

    return attachments
```

### Download Attachment

```python
import base64

def download_attachment(service, message_id, attachment_id, filename):
    """Download attachment to file."""
    attachment = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment_id
    ).execute()

    data = base64.urlsafe_b64decode(attachment['data'])

    with open(filename, 'wb') as f:
        f.write(data)

    print(f"Saved to {filename}")
```

---

## Best Practices

1. **Always validate input**: Check message IDs, label IDs exist
2. **Cache labels**: Don't fetch labels repeatedly
3. **Handle pagination**: Use pageToken for large result sets
4. **Rate limit awareness**: Monitor quota, implement backoff
5. **Error recovery**: Retry transient errors with exponential backoff
6. **Minimal format**: Use `format=minimal` when you don't need body
7. **Metadata scope**: Use `gmail.metadata` scope with `metadataHeaders` for lightweight access
8. **Batch operations**: Group up to 100 requests per batch (don't exceed 50 recommended)
9. **Token refresh**: Implement automatic token refresh before expiration
10. **Secure credentials**: Never commit credentials or tokens to version control
