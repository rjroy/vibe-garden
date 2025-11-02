---
name: sdd-metadata
description: Provides metadata detection and management for SDD documents. This skill should be used when creating or updating specs, plans, tasks, or progress documents to auto-populate author, dates, and version fields.
---

# SDD Metadata

This skill provides utilities to auto-populate metadata fields in SDD frontmatter.

## Author Detection

To populate the `authored_by` field:

1. Execute the author detection script via the Bash tool:
   ```bash
   bash scripts/detect-author.sh
   ```

2. Capture the output in one of these formats:
   - `Name <email>` (if both name and email detected)
   - `Name` (if only name detected)
   - `Unknown Author` (if nothing detected)

3. Populate the `authored_by` field in the document frontmatter with the script output

**Detection priority**: Git config → Perforce user info → Environment variables ($USER/$USERNAME) → "Unknown Author"

## Date Generation

To populate date fields (`created`, `last_updated`):

1. Execute the date command via the Bash tool:
   ```bash
   date +%Y-%m-%d
   ```

2. Capture the output in `YYYY-MM-DD` format (ISO 8601)

3. Apply the date to the appropriate fields:
   - `created`: Set once at document creation, never change afterwards
   - `last_updated`: Update on every document edit

## Frontmatter Field Management

To manage SDD document frontmatter fields:

- **`created`**: Set once at document creation using current date, never change afterwards
- **`last_updated`**: Update to current date on every document edit
- **`authored_by`**: YAML list format. To manage this field:
  - Compare detected author with existing list
  - Append new author if different from all existing authors
  - Preserve existing authors
- **`version`**: Only increment when user explicitly requests a version bump (do not auto-increment)
