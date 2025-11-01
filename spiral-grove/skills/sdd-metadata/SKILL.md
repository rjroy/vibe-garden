---
name: sdd-metadata
description: Provides metadata detection and management for SDD documents. Use when creating or updating specs, plans, tasks, or progress documents to auto-populate author, dates, and version fields.
---

# SDD Metadata

## Detect Author

```bash
bash spiral-grove/skills/sdd-metadata/scripts/detect-author.sh
```

**Output**: `Name <email>` or `Name` or `Unknown Author`

**Detection priority**: Git → Perforce → ENV ($USER/$USERNAME) → Unknown Author

## Get Current Date

```bash
date +%Y-%m-%d
```

**Output**: `YYYY-MM-DD` (ISO 8601 format)

## Frontmatter Fields

- `created`: Set once at document creation, never changed
- `last_updated`: Update on every document edit
- `authored_by`: YAML list, append new authors if different
- `version`: Only change when user explicitly requests version bump
