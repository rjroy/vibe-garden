---
name: courier-setup-helper
description: Assist users when Gmail OAuth setup or authentication fails for Courier MCP. Use when authentication errors occur, credentials are missing, GMAIL_CREDENTIALS_PATH is invalid, OAuth token issues arise, or permission errors prevent Gmail API access. Guides through Google Cloud Console setup, OAuth 2.0 credential creation, environment configuration, and troubleshooting common authentication problems.
---

# Courier MCP Setup Helper

You are assisting a user who encountered an authentication or setup error with Courier MCP. Your role is to diagnose the issue and provide clear, actionable steps to resolve it.

## Error Detection & Diagnosis

When you see error messages containing these patterns, this Skill should be active:
- "GMAIL_CREDENTIALS_PATH"
- "credentials not found" or "credential"
- "OAuth" or "authentication"
- "token" (expired, invalid, missing)
- "Permission denied" or "403"
- "Invalid client" or "401"
- "InstalledAppFlow"
- Gmail API initialization failures

## Common Error Scenarios

### Error: "GMAIL_CREDENTIALS_PATH not set" or "Environment variable not found"

**Cause:** Environment variable missing or not loaded in current shell session.

**Solution:**
1. Check if environment variable exists:
   ```bash
   echo $GMAIL_CREDENTIALS_PATH
   ```

2. If empty, set it temporarily:
   ```bash
   export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
   ```

3. Make it permanent by adding to shell profile:
   ```bash
   # For bash
   echo 'export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json' >> ~/.bashrc
   source ~/.bashrc

   # For zsh
   echo 'export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json' >> ~/.zshrc
   source ~/.zshrc
   ```

4. Restart Claude Code to pick up the new environment variable.

---

### Error: "Credentials file not found" or "No such file or directory"

**Cause:** File path in `GMAIL_CREDENTIALS_PATH` is incorrect or file doesn't exist.

**Solution:**
1. Verify the file exists:
   ```bash
   ls -la $GMAIL_CREDENTIALS_PATH
   ```

2. If file is missing, you need to create OAuth credentials:
   - See **First-Time OAuth Setup** section below
   - Or refer to the complete guide: `courier-mcp/docs/SETUP.md`

3. If file exists but path is wrong, update the environment variable:
   ```bash
   export GMAIL_CREDENTIALS_PATH=/correct/path/to/credentials.json
   ```

---

### Error: "invalid_grant", "Token has expired", or "Token refresh failed"

**Cause:** OAuth refresh token is stale, revoked, or corrupted.

**Solution:**
1. Delete the token cache file:
   ```bash
   # Token is usually stored next to credentials.json
   rm ~/.courier/token.pickle
   ```

2. Next run will trigger re-authentication:
   - A browser window will open
   - Sign in to your Gmail account
   - Click "Allow" to grant access
   - New token will be automatically saved

3. If re-authentication fails, credentials may be invalid:
   - Download fresh `credentials.json` from Google Cloud Console
   - Follow **First-Time OAuth Setup** steps below

---

### Error: "Permission denied", "403 Forbidden", or "Insufficient permissions"

**Cause:** OAuth scope not granted, or Gmail API not enabled.

**Solution:**
1. **Delete token and re-authenticate:**
   ```bash
   rm ~/.courier/token.pickle
   # Run Courier MCP again - grant ALL permissions when prompted
   ```

2. **Verify Gmail API is enabled:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to **APIs & Services** → **Library**
   - Search for "Gmail API"
   - Ensure it shows "API enabled" (if not, click ENABLE)

3. **Check OAuth consent screen:**
   - Go to **APIs & Services** → **OAuth consent screen**
   - Verify your email is listed as a test user (for External apps)
   - If missing, add yourself as a test user

---

### Error: "Invalid client", "Client ID not found", or "Malformed credentials"

**Cause:** `credentials.json` file is corrupted, wrong type, or from a deleted OAuth client.

**Solution:**
1. Verify it's valid JSON:
   ```bash
   cat $GMAIL_CREDENTIALS_PATH | python3 -m json.tool
   ```
   (Should show formatted JSON. If error, file is corrupted)

2. Check it's the right credential type:
   - Must be "OAuth 2.0 Client ID" type: "Desktop application"
   - **NOT** Service Account or API Key

3. Download fresh credentials:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to **APIs & Services** → **Credentials**
   - Find your OAuth 2.0 Client ID (or create new one)
   - Download as JSON
   - Save as `credentials.json`
   - Update `GMAIL_CREDENTIALS_PATH` to point to new file

---

### Error: "InstalledAppFlow not found", "ImportError", or "Module not found"

**Cause:** Python dependencies not installed.

**Solution:**
```bash
cd courier-mcp
pip install -e .              # Install courier-mcp and dependencies
# Or if using virtual environment:
source venv/bin/activate
pip install -e .
```

If still failing, check Python version:
```bash
python --version   # Must be Python 3.10+
```

---

## First-Time OAuth Setup

If you don't have `credentials.json` yet, follow these steps:

### Quick Setup (5 minutes)

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Click project dropdown → **NEW PROJECT**
   - Enter name: "Courier MCP"
   - Click **CREATE**

2. **Enable Gmail API:**
   - Go to **APIs & Services** → **Library**
   - Search "Gmail API"
   - Click **ENABLE**

3. **Create OAuth Credentials:**
   - Go to **APIs & Services** → **Credentials**
   - Click **Create Credentials** → **OAuth client ID**
   - If prompted, configure OAuth consent screen:
     - Choose **External** user type
     - App name: "Courier MCP"
     - Enter your email for support and developer contact
     - Click **SAVE AND CONTINUE** (skip optional scopes)
   - Back at credentials, click **Create Credentials** → **OAuth client ID**
   - Choose **Desktop application**
   - Click **CREATE**
   - Download JSON file (saves as `credentials.json`)

4. **Store credentials securely:**
   ```bash
   mkdir -p ~/.courier
   cp ~/Downloads/credentials.json ~/.courier/
   chmod 600 ~/.courier/credentials.json  # Restrict permissions
   ```

5. **Set environment variable:**
   ```bash
   export GMAIL_CREDENTIALS_PATH=~/.courier/credentials.json
   # Add to shell profile to make permanent (see solutions above)
   ```

6. **First authentication:**
   - Run Courier MCP
   - Browser window will open
   - Grant access to Gmail
   - Done! Token saved automatically

### Detailed Setup

For complete step-by-step instructions with screenshots, see:
- **`courier-mcp/docs/SETUP.md`** (comprehensive guide)

---

## Troubleshooting Checklist

Run through this checklist to diagnose issues:

1. **Is `GMAIL_CREDENTIALS_PATH` set?**
   ```bash
   echo $GMAIL_CREDENTIALS_PATH
   # Should show: /path/to/credentials.json
   ```

2. **Does credentials file exist?**
   ```bash
   ls -la $GMAIL_CREDENTIALS_PATH
   # Should show file size and permissions
   ```

3. **Is it valid JSON?**
   ```bash
   cat $GMAIL_CREDENTIALS_PATH | python3 -m json.tool
   # Should show formatted JSON (no errors)
   ```

4. **Is Gmail API enabled?**
   - Check [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Library → Gmail API

5. **Is token stale?**
   ```bash
   rm ~/.courier/token.pickle  # Delete and re-authenticate
   ```

6. **Are dependencies installed?**
   ```bash
   pip list | grep google  # Should see google-auth, google-api-python-client
   ```

---

## Reference Documentation

For more details, consult these resources:

- **Complete Setup Guide:** `courier-mcp/docs/SETUP.md`
- **Gmail API Scopes:** [Google Developers - Gmail Scopes](https://developers.google.com/gmail/api/auth/scopes)
- **OAuth 2.0 Troubleshooting:** [Google Identity - OAuth Troubleshooting](https://developers.google.com/identity/protocols/oauth2/native-app#troubleshooting)
- **Google Cloud Console:** [console.cloud.google.com](https://console.cloud.google.com/)

---

## After Fixing the Issue

Once you've resolved the authentication error:

1. **Verify setup works:**
   ```bash
   cd courier-mcp
   ./venv/bin/python3 -c "
   from courier_mcp.auth import GmailAuthenticator
   auth = GmailAuthenticator()
   service = auth.build_gmail_service()
   print('✓ Gmail API connection successful!')
   "
   ```

2. **Try the original command again** (the one that triggered the error)

3. **If still failing:**
   - Check `courier-mcp.log` for detailed error messages
   - Verify all steps in the troubleshooting checklist
   - Consult `docs/SETUP.md` for advanced configuration

---

## Security Best Practices

⚠️ **Important:**

- **Never commit** `credentials.json` or `token.pickle` to version control
- Store credentials in secure location (e.g., `~/.courier/`)
- Add to `.gitignore`:
  ```
  credentials.json
  token.pickle
  .env
  ```
- Use restrictive file permissions:
  ```bash
  chmod 600 ~/.courier/credentials.json
  chmod 600 ~/.courier/token.pickle
  ```

---

**Next Step:** Once authentication is working, you can use Courier MCP tools like `get-messages` and `get-folders` to access your Gmail inbox!
