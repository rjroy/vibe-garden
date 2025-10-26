# Notification Script Documentation

## Overview

The `notify.py` script is a utility designed to send desktop notifications when Claude Code performs various operations. It integrates with the ntfy.sh service to deliver real-time alerts about Claude Code activities in your projects.

## Purpose

This script allows you to stay informed about Claude Code's progress without constantly monitoring the terminal. You'll receive notifications for:

- Task completions
- Error conditions
- Build status updates
- Other Claude Code events (configurable)

## How It Works

1. **Input**: The script reads JSON data from standard input containing a message and optional title
2. **Repository Detection**: Automatically detects your Git repository information
3. **Topic Generation**: Creates a unique notification topic based on your GitHub repository (`claude-{owner}-{repo}`)
4. **Notification Delivery**: Sends the notification via ntfy.sh with timestamp and formatting

## Features

- **Automatic Repository Detection**: Works with both HTTPS and SSH GitHub remotes
- **Timestamped Messages**: All notifications include the time they were sent
- **Unique Topics**: Each repository gets its own notification channel
- **Error Handling**: Gracefully handles network issues and malformed input
- **Zero Dependencies**: Uses only Python standard library (requires `git` and `curl` commands)

## Usage Examples

### Manual Testing

Test the script directly from the command line:

```bash
# Basic notification
echo '{"message": "Claude finished the task"}' | python3 notify.py

# Notification with custom title
echo '{"message": "Build completed successfully", "title": "Build Status"}' | python3 notify.py
```

### Expected Output

When successful, you'll see:
```
Notification sent: [14:30:25] Claude finished the task
```

The notification will be delivered to the ntfy.sh topic for your repository, which you can subscribe to on your mobile device or desktop.

## Notification Topic Format

Your notifications will be sent to: `https://ntfy.sh/claude-{owner}-{repo}`

For example:
- Repository: `https://github.com/johndoe/my-project`
- Topic: `claude-johndoe-my-project`

## Subscribing to Notifications

To receive the notifications:

1. **Mobile**: Install the ntfy app and subscribe to your topic
2. **Desktop**: Visit `https://ntfy.sh/claude-{owner}-{repo}` in your browser
3. **Command Line**: Use `curl -s ntfy.sh/claude-{owner}-{repo}/json` to monitor

## Error Handling

The script handles common issues:

- **Invalid JSON**: Returns error message and exits with code 1
- **Git command failure**: Returns error message if repository info can't be retrieved
- **Network issues**: Returns error message if notification can't be sent
- **Non-GitHub repositories**: Uses "unknown-unknown" as fallback topic

## Integration with Claude Code

- Open **Claude Code**
- Run `/hooks`
- Select `Notification`
- Decide if you want this to be global or local
- Add the new hook `python3 /full_path/notify.py`

## Troubleshooting

### Common Issues

1. **No notifications received**:
   - Verify you're subscribed to the correct topic
   - Check that `curl` and `git` commands are available
   - Test manually with the examples above

2. **Permission errors**:
   - Ensure the script is executable: `chmod +x notify.py`
   - Verify Python 3 is available: `python3 --version`

3. **Network connectivity**:
   - Test ntfy.sh access: `curl -d "test" https://ntfy.sh/test-topic`
   - Check firewall settings if in corporate environment

### Debug Mode

Add error output to see what's happening:

```bash
echo '{"message": "test"}' | python3 notify.py 2>&1
```

## Security Notes

- The script only sends the message content you provide
- Repository information is extracted from your local git configuration
- No sensitive data (like file contents or credentials) is transmitted
- All communication is over HTTPS to ntfy.sh