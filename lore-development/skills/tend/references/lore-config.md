# Lore Config Reference

Project-level configuration for tend. Lives at `.lore/lore-config.md`.

## Purpose

Every project's `.lore/` grows differently. Some projects have commissions, meetings, or prototypes alongside the standard brainstorm/specs/plans structure. Lore config tells tend what's intentional so it doesn't flag the same things every run.

Tend reads this file at startup. If it doesn't exist, tend uses defaults from the frontmatter schema and reports everything non-standard as a finding.

## Format

A markdown file with a YAML frontmatter block:

```yaml
---
# Additional directory types beyond the frontmatter schema defaults.
# Each entry: directory name -> list of valid status values.
custom_directories:
  commissions: [pending, active, completed, abandoned]
  meetings: [open, closed, deferred]
  prototypes: [active, archived]

# Override the archive directory name (default: _archive)
archive_directory: _abandoned

# Filename patterns to exempt from convention checks.
# Each entry is a regex pattern. Files matching any pattern skip
# naming convention and "dates in filenames" checks.
filename_exemptions:
  - "^commission-.+-\\d{8}-\\d{6}\\.md$"
  - "^audience-.+-\\d{8}-\\d{6}.*\\.md$"

# Additional frontmatter fields that are valid for custom directory types.
# Tend won't flag these as unexpected when retrofitting frontmatter.
custom_fields:
  commissions: [worker, workerDisplayTitle, prompt, dependencies, linked_artifacts]
  meetings: [worker, workerDisplayTitle, workerPortraitUrl, agenda, deferred_until, meeting_log]
---

# Project Lore Configuration

This file tells `/tend` what's intentional about this project's `.lore/` structure.

Updated by `/tend` at the end of each run when it discovers non-standard patterns
the user confirms as intentional.
```

## How Tend Uses It

### Status mode
- Looks up valid statuses for custom directories in `custom_directories`
- Falls back to frontmatter schema for standard directories
- Documents in unlisted directories get flagged (unless user confirms, which triggers a config suggestion)

### Tags mode
- No config dependency. Tags mode works the same regardless of directory types.

### Filenames mode
- Checks each filename against `filename_exemptions` before applying convention rules
- Exempt files skip case-style, date-in-filename, and tag-alignment checks
- Non-exempt files in custom directories follow the same rules as standard ones

### Directories mode
- Treats `custom_directories` keys as standard (won't flag as orphans)
- Uses `archive_directory` instead of hardcoded `_archive`
- Still reports empty directories and single-file directories regardless of config

## Config Suggestion Step

After completing all requested modes, tend checks whether any findings were dismissed as intentional:

1. **Directories flagged as orphans but confirmed intentional**: Suggest adding to `custom_directories` with observed status values
2. **Filenames flagged but confirmed as machine-generated patterns**: Suggest adding to `filename_exemptions` with a regex matching the pattern
3. **Archive directory differs from default**: Suggest setting `archive_directory`
4. **Custom frontmatter fields found in confirmed directories**: Suggest adding to `custom_fields`

### Suggestion behavior

- Present the proposed config as a diff (or full file if creating new)
- Wait for user confirmation before writing
- If config already exists, merge new entries with existing ones (don't overwrite)
- Only suggest entries for things the user explicitly confirmed as intentional during this run. Don't suggest based on assumptions.

### When to skip

- If no non-standard patterns were found, skip the suggestion step
- If the user ran a single mode that didn't surface config-relevant findings, skip
- If all findings are already covered by existing config, skip
