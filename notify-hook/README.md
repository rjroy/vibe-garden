# claude-hook-scripts

A collection of utility scripts for Claude Code hooks to enhance your development workflow.

## Overview

This repository contains various scripts that can be triggered by Claude Code hooks to provide notifications, automation, and other utilities during your development process.

## Scripts

### notify.py
Located at `scripts/notify.py` - A notification script that sends real-time alerts via ntfy.sh when Claude Code performs operations.

**Documentation**: See [docs/notify.md](docs/notify.md) for detailed usage instructions.

**Quick usage**:
```bash
echo '{"message": "Task completed", "title": "Claude Code"}' | python3 scripts/notify.py
```

## Repository Structure

```
claude-hook-scripts/
├── scripts/           # Hook scripts
│   └── notify.py     # Notification script
├── docs/             # Documentation
│   └── notify.md     # notify.py documentation
└── README.md         # This file
```

## Getting Started

1. Clone this repository
2. Make scripts executable: `chmod +x scripts/*.py`
3. Configure Claude Code hooks to use the scripts
4. See individual script documentation for specific setup instructions
