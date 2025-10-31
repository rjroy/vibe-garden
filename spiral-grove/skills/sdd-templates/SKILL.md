---
name: sdd-templates
description: Provides SDD document templates (spec, plan, tasks, progress) for Spiral Grove commands. Use when creating or updating SDD documents to ensure consistent structure and frontmatter.
---

# SDD Templates

## Available Templates

**`templates/spec-template.md`**
- Feature specifications (WHAT to build)
- Used by: `/spec-writing`, `module-spec-synthesizer` agent

**`templates/plan-template.md`**
- Technical plans (HOW to build)
- Used by: `/plan-generation`

**`templates/tasks-template.md`**
- Task breakdowns (STEPS to implement)
- Used by: `/task-breakdown`

**`templates/progress-template.md`**
- Progress tracking (STATUS of implementation)
- Used by: `/implementation`

## Frontmatter Structure

All templates use consistent YAML frontmatter:
- `version`: Document version (semver)
- `status`: Draft | Under Review | Approved
- `created`: YYYY-MM-DD (set once, never changed)
- `last_updated`: YYYY-MM-DD (updated on every edit)
- `authored_by`: List of authors (Name <email> format)

Populate metadata using the `sdd-metadata` skill.
