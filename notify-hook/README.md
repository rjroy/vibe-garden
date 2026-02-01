# Notify Hook

<img src="logo.webp" align="right" width="128" height="128" alt="Notify Hook Logo">

A Claude Code plugin for desktop and mobile notifications when Claude needs your attention.

## Overview

Get notified when Claude Code asks a question or completes a long-running task. Supports desktop notifications (Linux/macOS) and mobile push via ntfy.sh.

## Features

- **Desktop notifications**: Native system notifications on Linux and macOS
- **Mobile push**: Push notifications via ntfy.sh to your phone
- **Smart triggers**: Notifies on questions and task completion
- **Configurable**: Control which events trigger notifications

## Installation

```bash
/plugin install notify-hook@vibe-garden
```

## Configuration

### ntfy.sh Setup (Mobile Notifications)

1. Install the ntfy app on your phone ([Android](https://play.google.com/store/apps/details?id=io.heckel.ntfy), [iOS](https://apps.apple.com/app/ntfy/id1625396347))
2. Subscribe to a unique topic (e.g., `my-claude-notifications`)
3. Set the `NTFY_TOPIC` environment variable:

```bash
export NTFY_TOPIC="my-claude-notifications"
```

### Desktop Notifications

Desktop notifications work out of the box on:
- **Linux**: Uses `notify-send` (install `libnotify-bin` if missing)
- **macOS**: Uses native notification center

## Structure

```
notify-hook/
├── .claude-plugin/
│   └── plugin.json       # Plugin metadata
├── hooks/
│   └── hooks.json        # Hook registrations
├── scripts/
│   └── notify.py         # Notification script
└── docs/
    └── notify.md         # Detailed documentation
```

## How It Works

The plugin registers hooks that trigger on:
- `AskUserQuestion` tool calls (Claude is asking you something)
- Task completion events

When triggered, the notification script sends alerts through configured channels.

## Troubleshooting

**No desktop notifications on Linux:**
```bash
sudo apt install libnotify-bin  # Debian/Ubuntu
sudo pacman -S libnotify        # Arch
```

**No mobile notifications:**
- Verify `NTFY_TOPIC` is set: `echo $NTFY_TOPIC`
- Check ntfy app is subscribed to the same topic
- Test manually: `curl -d "Test" ntfy.sh/your-topic`

## Dependencies

- Python 3.12+
- `notify-send` (Linux) or native notifications (macOS)
- ntfy.sh account (optional, for mobile)
