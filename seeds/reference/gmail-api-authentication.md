# Gmail API Authentication & Setup Guide

## Table of Contents
1. [Authentication Methods](#authentication-methods)
2. [OAuth 2.0 Setup (Web/Desktop Apps)](#oauth-20-setup)
3. [Service Account Setup](#service-account-setup)
4. [Scopes & Permissions](#scopes--permissions)
5. [Token Management](#token-management)
6. [Common Issues](#common-issues)

## Authentication Methods

Gmail API supports two primary authentication approaches:

### 1. OAuth 2.0 (User Delegation)
**Best for**: Interactive apps where the app acts on behalf of the user

**Flow**:
1. User authorizes app to access their Gmail
2. App receives authorization code
3. App exchanges code for access token
4. App uses token to access Gmail data
5. Token expires; refresh token used to get new token

**Pros**:
- User controls access
- Limited to what user grants
- Refresh tokens for long-term access

**Cons**:
- Requires user interaction
- Manual credential management
- Token expiration handling needed

### 2. Service Account (Server-to-Server)
**Best for**: Background jobs, batch processing, server apps

**Flow**:
1. Download service account JSON key
2. Create service account client directly
3. (Optional) Use domain-wide delegation for Google Workspace
4. Make API calls using service account credentials

**Pros**:
- No user interaction needed
- Automated server access
- Can access multiple mailboxes (with delegation)

**Cons**:
- Requires storing private keys securely
- No user revocation per app
- Domain-wide delegation needed for multiple users

---

## OAuth 2.0 Setup

### Step 1: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Sign in with Google account
3. Click project selector (top-left)
4. Click "NEW PROJECT"
5. Enter project name (e.g., "Gmail MCP Server")
6. Click "CREATE"

### Step 2: Enable Gmail API

1. In Google Cloud Console, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on Gmail API
4. Click "ENABLE"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" → "OAuth consent screen"
2. Choose User Type: **"External"** (for testing/development)
3. Fill in required information:
   - App name: Your application name
   - User support email: Your email
   - Developer contact info: Your email
4. Click "SAVE AND CONTINUE"

### Step 4: Add Scopes

On the "Scopes" screen:

1. Click "ADD OR REMOVE SCOPES"
2. Add the following scopes (select what your app needs):

| Scope | Purpose |
|-------|---------|
| `https://www.googleapis.com/auth/gmail.readonly` | Read-only access to all Gmail data |
| `https://www.googleapis.com/auth/gmail.metadata` | Read-only access to email headers |
| `https://www.googleapis.com/auth/gmail.labels` | Manage labels |
| `https://www.googleapis.com/auth/gmail.modify` | Full read/write access |
| `https://www.googleapis.com/auth/gmail` | Full mailbox access (deprecated, use readonly) |

**For MCP inbox retrieval**: Use `gmail.readonly` or `gmail.metadata` (more restrictive)

3. Click "UPDATE"
4. Click "SAVE AND CONTINUE"

### Step 5: Add Test Users

1. On "Test users" screen, click "ADD USERS"
2. Add your test email addresses
3. Click "SAVE AND CONTINUE"

### Step 6: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "CREATE CREDENTIALS" → "OAuth client ID"
3. Choose Application Type:
   - **Desktop application** (for CLI/desktop apps)
   - **Web application** (for web servers)
4. For Web application, add Authorized redirect URIs:
   - Local: `http://localhost:8080/callback`
   - Production: Your app's callback URL
5. Click "CREATE"
6. Download the JSON file (save as `credentials.json`)

### Step 7: Implement OAuth Flow in Code

#### Python Example

```python
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
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

    from google.oauth2.service_account import Credentials as ServiceAccountCredentials
    from googleapiclient.discovery import build

    service = build('gmail', 'v1', credentials=creds)
    return service
```

#### Node.js Example

```javascript
const {google} = require('googleapis');
const {OAuth2} = google.auth;
const fs = require('fs');

const oauth2Client = new OAuth2(
    CLIENT_ID,
    CLIENT_SECRET,
    REDIRECT_URL
);

// Get token from storage or redirect to auth URL
async function getGmailService() {
    let tokens;

    if (fs.existsSync('tokens.json')) {
        tokens = JSON.parse(fs.readFileSync('tokens.json'));
        oauth2Client.setCredentials(tokens);
    } else {
        const authUrl = oauth2Client.generateAuthUrl({
            access_type: 'offline',
            scope: ['https://www.googleapis.com/auth/gmail.readonly']
        });
        // User needs to visit authUrl and provide authorization code
    }

    const gmail = google.gmail({version: 'v1', auth: oauth2Client});
    return gmail;
}
```

---

## Service Account Setup

### Step 1: Create Service Account

1. In Google Cloud Console, go to "APIs & Services" → "Service Accounts"
2. Click "CREATE SERVICE ACCOUNT"
3. Enter service account name (e.g., "gmail-mcp-server")
4. Enter service account ID (auto-generated)
5. Click "CREATE AND CONTINUE"

### Step 2: Grant Roles (Optional)

1. Skip role assignment for personal Gmail access
2. For Google Workspace domain access, add roles:
   - "Editor" or "Viewer" as appropriate
3. Click "CONTINUE"

### Step 3: Create Service Account Key

1. Click on created service account
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Click "CREATE"
6. Save the JSON file as `service-account-key.json`

**⚠️ IMPORTANT**: Never commit this file to version control. Add to `.gitignore`.

### Step 4: Enable Domain-Wide Delegation (Google Workspace Only)

If accessing Google Workspace mailboxes:

1. On service account page, go to "Details"
2. Under "Domain-wide delegation", click "Enable"
3. Copy the Client ID
4. Go to Google Admin Console → Security → API controls → Domain-wide delegation
5. Click "Add new"
6. Paste Client ID
7. Grant OAuth scopes: `https://www.googleapis.com/auth/gmail.readonly`
8. Click "Authorize"

### Step 5: Use Service Account in Code

#### Python Example

```python
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service_account():
    credentials = service_account.Credentials.from_service_account_file(
        'service-account-key.json',
        scopes=SCOPES
    )

    # For Google Workspace (impersonate user)
    credentials = credentials.with_subject('user@example.com')

    service = build('gmail', 'v1', credentials=credentials)
    return service
```

#### Node.js Example

```javascript
const {google} = require('googleapis');
const key = require('./service-account-key.json');

async function getGmailService() {
    const auth = new google.auth.GoogleAuth({
        keyFile: 'service-account-key.json',
        scopes: ['https://www.googleapis.com/auth/gmail.readonly']
    });

    const gmail = google.gmail({
        version: 'v1',
        auth: auth
    });

    return gmail;
}
```

---

## Scopes & Permissions

### Available Scopes

| Scope | Purpose | Restriction |
|-------|---------|-------------|
| `gmail.readonly` | Read-only full access | No writing |
| `gmail.metadata` | Headers only (lightweight) | Can't read body |
| `gmail.modify` | Read and modify | Can modify labels |
| `gmail.labels` | Manage labels only | No message content |
| `gmail.send` | Send emails only | No reading |
| `mail.google.com` | Full IMAP/POP access | Legacy, not recommended |

### Scope Selection for MCP

For an MCP server focused on **retrieving inbox content**, use:

1. **Best**: `gmail.metadata` - Most restrictive, sufficient for headers
2. **Better**: `gmail.readonly` - Full read access without modification
3. **Avoid**: `gmail.modify` or `gmail` - More permissions than needed

**Principle**: Request minimum permissions needed (least privilege)

---

## Token Management

### Access Token Lifecycle

**Valid for**: 1 hour by default

### Refresh Token Lifecycle

**Valid for**:
- 6 months if used at least once per 6 months
- Revoked if unused for 6 months
- Infinite if the app is not in testing phase

### Token Refresh Strategy

```python
from google.auth.transport.requests import Request

def ensure_valid_token(credentials):
    """Refresh token if expired."""
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    return credentials
```

### Storing Credentials Safely

**DO**:
- Encrypt tokens at rest
- Use environment variables for secret keys
- Store in secure databases
- Rotate keys regularly
- Add to `.gitignore`

**DON'T**:
- Commit tokens to version control
- Log token values
- Share credentials between environments
- Hardcode in source code

---

## Common Issues

### Issue: "OAuth consent screen not configured"

**Cause**: Haven't set up consent screen
**Solution**:
1. Go to "APIs & Services" → "OAuth consent screen"
2. Select User Type: "External"
3. Fill in required fields and save

### Issue: "Invalid redirect_uri"

**Cause**: Redirect URI in code doesn't match configured URI
**Solution**:
1. Check credentials JSON file
2. Ensure redirect_uri matches exactly (including http/https and port)
3. Common valid URIs:
   - `http://localhost:8080/callback` (development)
   - `urn:ietf:wg:oauth:2.0:oob` (out-of-band, desktop apps)

### Issue: "Insufficient Permission"

**Cause**: Scope not granted or token doesn't have required scope
**Solution**:
1. Check requested scopes in code
2. Delete stored token/credentials
3. Force re-authentication with correct scopes

### Issue: "Service account doesn't have access"

**Cause**: Missing domain-wide delegation or wrong user
**Solution**:
1. Verify domain-wide delegation is enabled
2. Check service account has access to domain
3. Verify user email is correct
4. Check scopes are authorized in Admin console

### Issue: "Token expired or revoked"

**Cause**: Refresh token is invalid or user revoked access
**Solution**:
1. Delete stored tokens
2. Require user re-authentication
3. Implement token refresh retry logic

---

## Security Best Practices

1. **Never commit credentials**: Always use `.gitignore`
2. **Use environment variables**: Store sensitive data in environment
3. **Rotate keys regularly**: Especially service account keys
4. **Audit access**: Monitor API usage in Google Cloud Console
5. **Minimal scopes**: Only request needed permissions
6. **Secure storage**: Encrypt credentials at rest
7. **HTTPS only**: Always use HTTPS for redirect URIs
8. **Monitor tokens**: Track token expiration and refresh
