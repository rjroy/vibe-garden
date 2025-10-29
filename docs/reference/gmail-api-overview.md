# Gmail API Overview & Reference

**Date Created**: October 2025
**Purpose**: Comprehensive research for creating an MCP server for Gmail inbox access

## Table of Contents
1. [API Overview](#api-overview)
2. [Key Concepts](#key-concepts)
3. [Architecture](#architecture)
4. [Use Cases for MCP Integration](#use-cases-for-mcp-integration)

## API Overview

The Gmail API is a RESTful API provided by Google that allows applications to:
- Access Gmail mailbox data (threads, messages, labels)
- Read emails with full content and attachments
- Retrieve email metadata
- Manage labels and folders
- Send emails (not covered in this research - focused on inbox retrieval)

**Official Documentation**: https://developers.google.com/workspace/gmail/api/guides
**REST Reference**: https://developers.google.com/gmail/api/reference/rest

## Key Concepts

### Base URL
```
https://gmail.googleapis.com/gmail/v1/users/{userId}
```

### Special User Identifiers
- `me` - Refers to the authenticated user (recommended)
- User email address - Can be used directly
- User numerical ID - Also supported

### API Versioning
Current stable version: **v1**

### Core Resources

| Resource | Purpose |
|----------|---------|
| `users.messages` | Retrieve, list, modify messages |
| `users.labels` | List, get, create, update labels |
| `users.threads` | Group messages in conversations |
| `users.history` | Track changes to mailbox |
| `users.drafts` | Work with draft messages |

## Architecture

### Request/Response Flow

```
Client Application
    ↓
OAuth 2.0 Authentication
    ↓
Gmail API Endpoint
    ↓
Google Authorization Server (validates token)
    ↓
Gmail Service
    ↓
Response (JSON)
```

### Message Data Model

Messages in Gmail API consist of:

```
Message
├── id (string): Unique message ID
├── threadId (string): Thread containing this message
├── labelIds (array): Applied label IDs
├── internalDate (string): Epoch milliseconds timestamp
├── payload (object): Email structure
│   ├── partId (string): MIME part identifier
│   ├── mimeType (string): Content type
│   ├── filename (string): Attachment name
│   ├── headers (array): Email headers
│   │   ├── name (string): Header name (From, To, Subject, etc.)
│   │   └── value (string): Header value
│   ├── body (object): Message content
│   │   ├── size (integer): Content size in bytes
│   │   ├── data (string): Base64 encoded content
│   │   └── attachmentId (string): For attachments
│   └── parts (array): MIME parts (recursive)
├── sizeEstimate (integer): Estimated message size
├── historyId (string): For tracking changes
└── raw (string): Raw RFC 2822 message (format=raw only)
```

### Label Model

```
Label
├── id (string): Unique label ID
├── name (string): Display name
├── messageListVisibility (string): "show" | "hide"
├── labelListVisibility (string): "labelShow" | "labelHide" | "labelShowIfUnread"
└── type (string): "system" | "user"
```

## Format Options

When retrieving messages, you can specify different formats:

| Format | Content | Use Case |
|--------|---------|----------|
| `minimal` | ID + labels only | Fast lookup, large batches |
| `full` | Complete message with body in payload | Full content access |
| `raw` | Raw RFC 2822 (base64url encoded) | Perfect message reconstruction |
| `metadata` | Headers only (specify which) | Lightweight header access |

## Use Cases for MCP Integration

### 1. Email Retrieval (Primary Use Case)
- List messages in inbox
- Filter by labels
- Retrieve full message content with attachments
- Search by sender, subject, date range

### 2. Label Management
- List all available labels
- Filter messages by label combinations
- Retrieve label statistics

### 3. Thread Operations
- View message conversations
- Access all messages in a thread
- Retrieve thread metadata

### 4. Metadata Queries
- Extract sender/recipient information
- Get subject lines
- Retrieve attachment metadata without full download

### 5. Message Analysis
- Parse email headers for authentication
- Extract structured data from email content
- Analyze attachment information

---

## Next Steps for MCP Development

1. **Review Authentication Guide** (`gmail-api-authentication.md`)
   - Required credentials setup
   - OAuth flow implementation
   - Authorization scopes

2. **Study API Methods** (`gmail-api-methods.md`)
   - Available endpoints
   - Request/response patterns
   - Query parameters

3. **Review Implementation Guide** (`gmail-api-implementation.md`)
   - Code examples
   - Error handling
   - Best practices

4. **Understand Limitations** (`gmail-api-limitations.md`)
   - Rate limits and quotas
   - Error codes
   - Performance considerations
