# Courier MCP Setup Guide

This guide walks you through setting up Courier MCP to access your Gmail inbox.

## Quick Start (5 minutes)

### 1. Get Gmail Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Gmail API:
   - Click "APIs & Services"
   - Click "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth credentials:
   - Go back to "APIs & Services"
   - Click "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop application"
   - Download as JSON (saves as `credentials.json`)

### 2. Set Environment Variable

```bash
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
```

Add to your shell profile (`.bashrc`, `.zshrc`, etc.) to make it permanent:

```bash
echo 'export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json' >> ~/.bashrc
```

### 3. Run Courier MCP

First time, you'll be prompted to authenticate:

```bash
courier-mcp
```

A browser window will open asking you to grant access. After granting, a `token.pickle` file is automatically saved.

✅ Done! You're ready to use Courier MCP.

---

## Detailed Setup Steps

### Step 1: Create Google Cloud Project

1. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top
3. Click "NEW PROJECT"
4. Enter project name (e.g., "Courier MCP")
5. Click "CREATE"

### Step 2: Enable Gmail API

1. In the Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click on the "Gmail API" result
4. Click the **ENABLE** button

### Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** at the top
3. Select **OAuth client ID**
4. If prompted to configure OAuth consent screen first:
   - Click **Configure Consent Screen**
   - Choose **External** user type
   - Click **CREATE**
   - Fill in:
     - **App name**: "Courier MCP"
     - **User support email**: your email
     - **Developer contact**: your email
   - Click **SAVE AND CONTINUE**
   - Skip optional scopes (click **SAVE AND CONTINUE**)
   - Review and click **BACK TO DASHBOARD**
5. Go back to **Credentials**
6. Click **Create Credentials** → **OAuth client ID** again
7. Choose **Desktop application** (for local use)
8. Click **CREATE**
9. Click the download icon next to your new credentials
10. Save as `credentials.json`

### Step 4: Store Credentials Securely

⚠️ **IMPORTANT SECURITY NOTE:**

- **Never commit** `credentials.json` or `token.pickle` to version control
- Store in a secure location (e.g., `~/.courier/`)
- Add to `.gitignore`:

```bash
credentials.json
token.pickle
.env
```

### Step 5: Configure Environment Variable

Copy `credentials.json` to a safe location:

```bash
mkdir -p ~/.courier
cp credentials.json ~/.courier/
```

Set environment variable:

```bash
export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json
```

Make permanent by adding to your shell profile:

```bash
# For bash
echo 'export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json' >> ~/.bashrc

# For zsh
echo 'export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json' >> ~/.zshrc

# For fish
echo 'set -gx GMAIL_CREDENTIALS_PATH ~/.courier/credentials.json' >> ~/.config/fish/config.fish
```

### Step 6: First-Time Authentication

When you first run Courier MCP:

```bash
courier-mcp
```

You'll see:

```
Please visit this URL to authorize this application: https://accounts.google.com/o/oauth2/auth?...
```

1. Open the URL in your browser
2. Select your Gmail account
3. Click "Allow" to grant Courier MCP access to read emails
4. You'll see "The authentication flow has completed"
5. Return to terminal - Courier MCP is ready!

A `token.pickle` file is automatically created in the same directory as `credentials.json`. This allows future runs to authenticate without user interaction.

---

## Verify Setup

To verify your setup works:

```bash
./venv/bin/python3 -c "
from courier_mcp.auth import GmailAuthenticator
auth = GmailAuthenticator()
service = auth.build_gmail_service()
print('✓ Gmail API connection successful!')
"
```

---

## Troubleshooting

### "Credentials file not found"

**Issue**: `GMAIL_CREDENTIALS_PATH` not set or file doesn't exist

**Solution**:
1. Verify file exists: `ls -la ~/.courier/credentials.json`
2. Check env var is set: `echo $GMAIL_CREDENTIALS_PATH`
3. Make sure it's in your shell profile for persistent setup

### "OAuth token expired"

**Issue**: `token.pickle` is stale

**Solution**:
```bash
rm ~/.courier/token.pickle
# Run again to re-authenticate
courier-mcp
```

### "Permission denied" or "403 error"

**Issue**: OAuth scope not granted

**Solution**:
1. Delete `token.pickle`: `rm ~/.courier/token.pickle`
2. Check your Google Cloud project has Gmail API enabled
3. Run again and grant all permissions when prompted

### "Invalid client" error

**Issue**: `credentials.json` is corrupted or wrong file

**Solution**:
1. Verify it's a valid JSON file: `cat ~/.courier/credentials.json`
2. Delete old credentials in Google Cloud Console
3. Download fresh `credentials.json` following steps in "Create OAuth 2.0 Credentials"

### "InstalledAppFlow not found" or import errors

**Issue**: Dependencies not installed

**Solution**:
```bash
cd courier-mcp
pip install -e .
```

---

## For Teams / Shared Credentials

If using shared test Gmail account:

1. Have one person complete setup steps 1-3
2. Share the `credentials.json` file securely (e.g., 1Password, LastPass)
3. Everyone sets `GMAIL_CREDENTIALS_PATH` to their copy
4. First person to run will authenticate
5. Others can use the same `token.pickle` (share securely)

⚠️ Security Note: Each `credentials.json` represents app registration with Google. Don't distribute widely.

---

## Revoking Access

If you want to revoke Courier MCP's access to your Gmail:

1. Go to [Google Account Security Settings](https://myaccount.google.com/security)
2. Scroll to "Your apps with access to your Google Account"
3. Find "Courier MCP" (or your OAuth app name)
4. Click and remove

---

## Advanced Configuration

See `courier.config` for additional configuration options:

```yaml
COURIER_TIMEOUT_SECONDS: 20          # Max operation time
COURIER_MAX_RESULTS_DEFAULT: 10      # Default email limit per query
COURIER_LOG_LEVEL: DEBUG              # Logging verbosity
```

Override via environment variables:

```bash
export COURIER_TIMEOUT_SECONDS=30
export COURIER_MAX_RESULTS_DEFAULT=50
```

---

## Support

For issues, check:
- `courier-mcp.log` for detailed error logs
- [Gmail API Documentation](https://developers.google.com/gmail/api/)
- [Google Cloud Console](https://console.cloud.google.com/)
