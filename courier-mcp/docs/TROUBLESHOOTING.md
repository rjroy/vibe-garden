# Courier MCP - Troubleshooting Guide

Common issues and solutions for Courier MCP.

---

## Quick Diagnostic Checklist

Before troubleshooting, verify:

- [ ] Python 3.10+ installed: `python --version`
- [ ] Virtual environment activated
- [ ] Gmail API enabled in Google Cloud Console
- [ ] `GMAIL_CREDENTIALS_PATH` environment variable set
- [ ] `credentials.json` file exists and is valid
- [ ] `courier.config` file exists in plugin directory
- [ ] MCP server running (visible in Claude Code)

---

## Common Issues

### 1. "Configuration not yet loaded" Error

**Symptom**:
```json
{
  "error": "INTERNAL_ERROR",
  "message": "Configuration not yet loaded. Call load_config() first."
}
```

**Cause**: MCP server didn't initialize configuration properly (pre-v1.1.0 bug).

**Solution**:
1. Ensure you're running v1.1.0 or later
2. Restart MCP server
3. Verify `courier.config` exists in plugin directory

**Prevention**: Keep plugin updated.

---

### 2. "GMAIL_CREDENTIALS_PATH not set" Error

**Symptom**:
```json
{
  "error": "AUTH_ERROR",
  "message": "GMAIL_CREDENTIALS_PATH environment variable not set"
}
```

**Cause**: Environment variable missing or not exported correctly.

**Solution**:
```bash
# Set environment variable
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

# Verify it's set
echo $GMAIL_CREDENTIALS_PATH

# Restart MCP server
```

**For persistent setup**, add to shell profile:
```bash
# Add to ~/.bashrc or ~/.zshrc
export GMAIL_CREDENTIALS_PATH="$HOME/gmail-credentials/credentials.json"

# Reload profile
source ~/.bashrc
```

---

### 3. "Credentials file not found" Error

**Symptom**:
```json
{
  "error": "AUTH_ERROR",
  "message": "Credentials file not found: /path/to/credentials.json"
}
```

**Cause**: Path is incorrect or file doesn't exist.

**Solution**:
1. Verify file exists:
   ```bash
   ls -la /path/to/credentials.json
   ```

2. Check path is absolute (not relative):
   ```bash
   # Good
   export GMAIL_CREDENTIALS_PATH=/home/user/credentials.json

   # Bad (relative path may not work)
   export GMAIL_CREDENTIALS_PATH=./credentials.json
   ```

3. Download credentials from Google Cloud Console (see [SETUP.md](SETUP.md))

---

### 4. "Token expired" or "invalid_grant" Error

**Symptom**:
```json
{
  "error": "AUTH_ERROR",
  "message": "Token expired or invalid",
  "details": {
    "type": "google.auth.exceptions.RefreshError"
  }
}
```

**Cause**: OAuth refresh token has expired or been revoked.

**Solution**:
1. Delete token cache:
   ```bash
   rm token.pickle
   ```

2. Re-authenticate (MCP server will trigger OAuth flow):
   ```bash
   # Server will open browser for authentication
   # Follow OAuth prompts
   ```

3. Verify new token created:
   ```bash
   ls -la token.pickle
   ```

**Note**: Token expiration is rare. Usually caused by:
- Revoking app access in Google Account settings
- Changing OAuth credentials
- Security policy changes

---

### 5. "Permission denied" (Export Directory)

**Symptom**:
```json
{
  "error": "EXPORT_ERROR",
  "message": "Cannot write to directory /root/emails (permission denied)"
}
```

**Cause**: Directory is not writable by MCP server process.

**Solution**:
1. Choose a directory you have write access to:
   ```
   You: Export to ~/emails instead
   ```

2. Or fix permissions:
   ```bash
   # Create directory with correct permissions
   mkdir -p /tmp/emails
   chmod 755 /tmp/emails
   ```

3. Verify write access:
   ```bash
   touch /tmp/emails/test.txt && rm /tmp/emails/test.txt
   ```

---

### 6. "Gmail API not enabled" Error

**Symptom**:
```json
{
  "error": "AUTH_ERROR",
  "message": "Gmail API has not been used in project XXX..."
}
```

**Cause**: Gmail API not enabled in Google Cloud Console.

**Solution**:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" → "Library"
4. Search for "Gmail API"
5. Click "Enable"
6. Wait 1-2 minutes for propagation
7. Restart MCP server

---

### 7. Rate Limit / Quota Exhaustion

**Symptom** (rare):
```json
{
  "error": "RATE_LIMITED",
  "message": "Gmail API quota exhausted after 3 retry attempts"
}
```

**Cause**: Too many API requests in short time (unusual with free tier).

**Solution**:
1. Wait 1-2 minutes before retrying
2. Reduce `max_results` in request
3. Increase `COURIER_TIMEOUT_SECONDS` to allow more backoff time

**Prevention**:
- Use date filters to reduce result sets
- Export in smaller batches
- Avoid concurrent exports

**Check quota usage**:
```
# Review logs for quota tracking
tail -f courier-mcp.log | grep -i quota
```

---

### 8. Timeout Exceeded

**Symptom**:
```json
{
  "error": "TIMEOUT",
  "message": "Operation exceeded 20s timeout",
  "files_saved": [/* partial results */]
}
```

**Cause**: Export took longer than timeout limit.

**Solution**:
1. **Increase timeout** (temporary):
   ```bash
   export COURIER_TIMEOUT_SECONDS=60
   # Restart MCP server
   ```

2. **Reduce result count**:
   ```
   You: Export 50 messages instead of 100
   ```

3. **Use partial results**:
   - Timeout returns files saved before timeout
   - Continue with remaining messages in next request

4. **Optimize queries**:
   - Use date filters to reduce search space
   - Filter by specific folder/label

---

### 9. Server Won't Start

**Symptom**: MCP server doesn't appear in Claude Code tools.

**Diagnosis**:
1. Check server logs:
   ```bash
   tail -f courier-mcp.log
   ```

2. Test server manually:
   ```bash
   cd courier-mcp
   source servers/venv/bin/activate
   python -m courier_mcp
   ```

3. Look for error messages:
   - Import errors → Missing dependencies
   - Auth errors → Credential issues
   - Config errors → `courier.config` missing

**Common fixes**:
```bash
# Reinstall dependencies
pip install -e servers/

# Verify Python version
python --version  # Should be 3.10+

# Check plugin manifest
cat .claude-plugin/plugin.json
```

---

### 10. "Tool not found" Error

**Symptom**: Claude doesn't recognize `get-folders` or `get-messages`.

**Cause**: Plugin not installed or server not running.

**Solution**:
1. Install plugin:
   ```
   /plugin install courier-mcp@vibe-garden
   ```

2. Verify installation:
   ```
   /plugin list
   ```

3. Restart Claude Code if needed

4. Check MCP server status:
   ```bash
   ps aux | grep courier_mcp
   ```

---

## Logging and Diagnostics

### Enable Debug Logging

Edit `courier.config`:
```yaml
COURIER_LOG_LEVEL: "DEBUG"
```

Or override with environment variable:
```bash
export COURIER_LOG_LEVEL=DEBUG
```

Restart MCP server to apply changes.

### View Logs

```bash
# Real-time log monitoring
tail -f courier-mcp.log

# Search for errors
grep -i error courier-mcp.log

# Search for specific message ID
grep "msg_xyz" courier-mcp.log

# View last 100 lines
tail -100 courier-mcp.log
```

### Log Levels

| Level | When to Use |
|-------|-------------|
| `DEBUG` | Development, troubleshooting |
| `INFO` | Normal operation (default) |
| `WARNING` | Potential issues |
| `ERROR` | Errors that need attention |
| `CRITICAL` | Server-breaking errors |

---

## Network Issues

### Connection Timeout

**Symptom**: `Connection timed out` errors in logs.

**Cause**: Network connectivity issues or Gmail API downtime.

**Solution**:
1. Check internet connection:
   ```bash
   ping -c 4 gmail.googleapis.com
   ```

2. Verify Gmail API status:
   - Visit [Google API Status Dashboard](https://status.cloud.google.com/)

3. Check firewall/proxy settings:
   ```bash
   # Test API endpoint
   curl -I https://gmail.googleapis.com
   ```

4. Retry after network stabilizes

### SSL Certificate Errors

**Symptom**: `SSL certificate verification failed` errors.

**Cause**: System CA certificates outdated or missing.

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates

# Arch Linux
sudo pacman -S ca-certificates

# macOS (Homebrew)
brew install ca-certificates

# Verify Python can access certificates
python -c "import ssl; print(ssl.get_default_verify_paths())"
```

---

## Performance Issues

### Slow Exports

**Symptom**: Exports take longer than expected.

**Diagnosis**:
1. Check logs for bottlenecks:
   ```bash
   grep -E "(duration|seconds)" courier-mcp.log
   ```

2. Review quota usage:
   ```bash
   grep -i "quota" courier-mcp.log
   ```

**Solutions**:
1. **Increase concurrency** (edit `gmail_service.py`):
   ```python
   # Default: 5 concurrent tasks
   # Increase to 10 (more quota consumption)
   semaphore = asyncio.Semaphore(10)
   ```

2. **Reduce message size processing**:
   ```bash
   export COURIER_MAX_FILE_SIZE_KB=5  # Truncate larger messages
   ```

3. **Use specific searches**:
   ```
   You: Export only unread emails from last week
   # vs.
   You: Export all emails  # Much slower
   ```

---

## Data Quality Issues

### Garbled Text in Markdown

**Symptom**: Non-ASCII characters appear as `�` or weird symbols.

**Cause**: Encoding issues in email body.

**Solution**: Usually handled automatically by `html2text`. If issues persist:

1. Check Python locale:
   ```bash
   python -c "import locale; print(locale.getpreferredencoding())"
   # Should be UTF-8
   ```

2. Set UTF-8 locale:
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

### Missing Attachment Metadata

**Symptom**: Attachments not listed in frontmatter.

**Cause**: Email structure doesn't follow standard MIME format.

**Diagnosis**: Check raw message in Gmail web UI.

**Solution**: File a bug report with example message ID.

---

## OAuth Troubleshooting

### "Redirect URI mismatch" Error

**Symptom**:
```
Error 400: redirect_uri_mismatch
```

**Cause**: OAuth redirect URI not configured in Google Cloud Console.

**Solution**:
1. Go to Google Cloud Console → Credentials
2. Edit OAuth 2.0 Client ID
3. Add authorized redirect URIs:
   - `http://localhost:8080/`
   - `urn:ietf:wg:oauth:2.0:oob`
4. Save and retry authentication

### "Access blocked" Error

**Symptom**:
```
This app hasn't been verified by Google
```

**Cause**: OAuth consent screen not configured or app not verified.

**Solution** (for personal use):
1. Click "Advanced" → "Go to [App Name] (unsafe)"
2. Grant permissions

**For production**: Submit app for Google verification (not needed for personal use).

### "Insufficient permission" Error

**Symptom**:
```json
{
  "error": "AUTH_ERROR",
  "message": "Insufficient permission (scope: gmail.readonly)"
}
```

**Cause**: OAuth consent didn't grant Gmail read access.

**Solution**:
1. Delete `token.pickle`
2. Re-authenticate and grant all requested permissions
3. Ensure scope includes `gmail.readonly`

---

## Getting Help

### Before Reporting Issues

1. **Check logs**: `tail -100 courier-mcp.log`
2. **Try basic diagnostics** above
3. **Update to latest version**
4. **Review documentation**:
   - [Setup Guide](SETUP.md)
   - [Usage Examples](USAGE.md)
   - [API Reference](API.md)

### Reporting Bugs

Include in your report:
1. **Error message** (full JSON if available)
2. **Log excerpt** (last 50 lines): `tail -50 courier-mcp.log`
3. **Environment**:
   - OS and version
   - Python version
   - Courier MCP version
4. **Steps to reproduce**
5. **Expected vs. actual behavior**

**GitHub Issues**: [github.com/rjroy/vibe-garden/issues](https://github.com/rjroy/vibe-garden/issues)

### Setup Assistance Skill

Courier MCP includes an auto-activation Skill for common setup issues:

**Triggers automatically when**:
- Authentication errors occur
- Credential path issues detected
- Token expiration errors

**Manual invocation**:
```
You: Help me set up Courier MCP
```

The Skill will guide you through OAuth setup and troubleshooting.

---

## Advanced Troubleshooting

### Force Server Restart

```bash
# Find MCP server process
ps aux | grep courier_mcp

# Kill process
kill <PID>

# Or use killall
killall -9 python

# Restart via Claude Code (server auto-starts)
```

### Reset All State

```bash
# Delete all cached data
rm token.pickle
rm courier-mcp.log

# Clear Python cache
find . -name "*.pyc" -delete
find . -name "__pycache__" -delete

# Reinstall dependencies
pip install --force-reinstall -e servers/

# Restart MCP server
```

### Debug Mode

Run server manually with debug output:
```bash
cd courier-mcp
source servers/venv/bin/activate
export COURIER_LOG_LEVEL=DEBUG
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
python -m courier_mcp 2>&1 | tee debug.log
```

---

## FAQ

**Q: Why do I keep getting "Configuration not loaded" errors?**
A: Update to v1.1.0 or later. This was a bug in earlier versions (fixed in commit `399080f`).

**Q: Can I use multiple Gmail accounts?**
A: Not in a single server instance. Run separate instances with different credentials.

**Q: Why are my exports slow?**
A: Network speed, Gmail API latency, and rate limiting affect speed. Use targeted searches and date filters to reduce result sets.

**Q: Does this work with G Suite/Workspace accounts?**
A: Yes, as long as you have Gmail API access. May require admin approval for OAuth scope.

**Q: Can I download attachment binaries?**
A: Not currently (by design). Only metadata is included. Future feature request.

**Q: Why does re-authentication keep asking for permissions?**
A: OAuth token may be expired or revoked. This is normal after long periods of inactivity or security changes.

---

**Still stuck? Open a [GitHub issue](https://github.com/rjroy/vibe-garden/issues) or check the [Setup Guide](SETUP.md).**
