# Compass Rose

A Claude Code plugin for project management using GitHub Projects.

## Overview

Compass Rose provides skills, commands, and agents to help users and Claude manage a project together. It uses GitHub's project functionality (`gh project ...`) to track work items.

## Purpose

Compass Rose complements [Spiral Grove](../spiral-grove/) (the Spec-Driven Development plugin) by providing a place for:

- **Tasks/Bugs**: Small, actionable items like "the input box is too big" or "when refresh is hit during a refresh the server crashes"
- **Feature Ideas**: Larger questions that may eventually need a full spec, like "add functionality for different rule-based RPG systems into the engine"

While Spiral Grove handles the structured development workflow (Spec → Plan → Tasks → Implementation), Compass Rose manages the backlog of work items that feed into that process.

## Requirements

- GitHub CLI (`gh`) installed and authenticated
- A GitHub Project linked to your repository

## Configuration

Each repository using Compass Rose must define which GitHub Project it uses. Configuration is stored in `.compass-rose/config.json` at the repository root.

### Setup

Create `.compass-rose/config.json` with your project details:

```json
{
  "project": {
    "owner": "my-org",
    "number": 123
  }
}
```

**Finding your project number:**

The project number appears in the GitHub Projects URL:
```
https://github.com/orgs/<owner>/projects/<number>
```

For example, if your project URL is:
```
https://github.com/orgs/my-org/projects/42
```

Your configuration would be:
```json
{
  "project": {
    "owner": "my-org",
    "number": 42
  }
}
```

### Required Fields

- `project.owner` - GitHub organization or username that owns the project
- `project.number` - Project number (visible in project URL)

### Optional Fields

You can customize behavior with optional preferences:

```json
{
  "project": {
    "owner": "my-org",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"]
  }
}
```

**Preferences:**

- `promptForLargeItems` (default: `true`) - Whether to prompt before starting L-sized items, suggesting spec-writing via Spiral Grove
- `largeSizeThreshold` (default: `["L", "XL"]`) - Array of size values that trigger spec-writing prompts

### Example Configurations

**Minimal configuration** (just the required fields):
```json
{
  "project": {
    "owner": "my-username",
    "number": 7
  }
}
```

**Full configuration** (with preferences):
```json
{
  "project": {
    "owner": "my-org",
    "number": 123
  },
  "preferences": {
    "promptForLargeItems": true,
    "largeSizeThreshold": ["L", "XL"]
  }
}
```

### Error Messages

If configuration is missing or invalid, Compass Rose will provide clear instructions:

**Missing configuration file:**
```
Error: Configuration file not found.

Please create .compass-rose/config.json with your project details:

{
  "project": {
    "owner": "<org-or-username>",
    "number": <project-number>
  }
}

Find your project number in the project URL:
https://github.com/orgs/<owner>/projects/<number>
```

**Invalid configuration:**
```
Error: Invalid configuration.

Both 'project.owner' and 'project.number' are required.

Example:
{
  "project": {
    "owner": "my-org",
    "number": 123
  }
}
```

**Project not found:**
```
Error: Project not found.

Verify that:
1. Project owner is correct: <owner>
2. Project number is correct: <number>
3. You have access to the project
4. You are authenticated: gh auth status
```

## Installation

```bash
/plugin install compass-rose@vibe-garden
```

## Status

**v0.1.0** - Initial project setup. Spec phase next.
