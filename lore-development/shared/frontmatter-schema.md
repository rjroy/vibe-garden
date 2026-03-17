# Lore Document Frontmatter Schema

Single source of truth for frontmatter fields across all `.lore/` document types.

## Common Fields

All lore documents should include these fields:

```yaml
---
title: string        # Descriptive title, used for search
date: YYYY-MM-DD     # Creation or completion date
status: string       # Document-type-specific (see below)
tags: [string]       # Searchable keywords (kebab-case)
modules: [string]    # Affected modules/components (kebab-case, optional)
related: [string]    # Paths to related lore documents (optional)
---
```

## Required vs Optional

| Field | Required | Notes |
|-------|----------|-------|
| title | Yes | Used by lore-researcher for search |
| date | Yes | When document was created/completed |
| status | Yes | Enables `/tend` hygiene checks |
| tags | Yes | Primary search mechanism |
| modules | No | Include when document relates to specific codebase areas |
| related | No | Cross-references to other lore documents |

## Spec-Specific Fields

Specs support an additional optional field:

```yaml
---
req-prefix: AUTH    # Short prefix for requirement IDs (optional)
---
```

| Field | Required | Notes |
|-------|----------|-------|
| req-prefix | No | Override auto-generated prefix. Use 3-12 uppercase chars. |

If omitted, prefix is auto-generated from the spec filename (first 2 segments, uppercase, max 12 chars).

Examples:
- `auth-flow.md` → `AUTH-FLOW`
- `user-authentication-oauth2.md` → `USER-AUTH`
- With `req-prefix: AUTH` → `AUTH`

Requirements then use format: `REQ-{prefix}-N` (e.g., `REQ-AUTH-FLOW-1`)

## Status Values by Document Type

| Type | Directory | Valid Status Values |
|------|-----------|---------------------|
| brainstorm | `.lore/brainstorm/` | `open`, `resolved`, `parked` |
| spec | `.lore/specs/` | `draft`, `approved`, `implemented`, `superseded` |
| design | `.lore/design/` | `draft`, `approved`, `implemented`, `superseded` |
| retro | `.lore/retros/` | `complete` |
| research | `.lore/research/` | `active`, `archived` |
| diagram | `.lore/diagrams/` | `current`, `outdated` |
| plan | `.lore/plans/` | `draft`, `approved`, `executed` |
| notes | `.lore/notes/` | `active`, `complete` |
| task | `.lore/tasks/` | `pending`, `complete`, `skipped` |
| reference | `.lore/reference/` | `current`, `outdated` |
| issue | `.lore/issues/` | `open`, `resolved`, `wontfix` |
| vision | `.lore/vision.md` | `draft`, `approved` |

## Notes-Specific Fields

Notes support an additional required field:

```yaml
---
source: .lore/plans/auth-flow.md    # Path to the source artifact (required)
---
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the spec, design, or plan being implemented. Enables retro to diff plan vs reality. |

## Task-Specific Fields

Tasks support additional required fields:

```yaml
---
source: .lore/plans/auth-flow.md    # Path to the plan this task was decomposed from (required)
sequence: 1                          # Integer ordering within the task set (required)
---
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the plan this task was decomposed from. Enables implement to find the parent plan. |
| sequence | Yes | Integer ordering within the task set. Determines execution order in implement. |

## Vision-Specific Notes

The vision document lives at `.lore/vision.md` (one per project, at the `.lore/` root). It uses the common fields only. The `modules` field is intentionally omitted because the vision applies to the entire project, not to specific modules. The `status` field uses `draft` and `approved`. A vision becomes `approved` when the user edits the frontmatter directly or tells the skill to mark it approved. The skill does not approve on the user's behalf.

## Examples

### Notes (Implementation)

```yaml
---
title: "Implementation notes: auth-flow"
date: 2026-02-05
status: active
tags: [implementation, notes]
source: .lore/plans/auth-flow.md
modules: [auth-service]
---
```

### Task

```yaml
---
title: Add auth middleware
date: 2026-02-10
status: pending
tags: [task]
source: .lore/plans/auth-flow.md
sequence: 1
modules: [auth-service]
---
```

### Retro

```yaml
---
title: N+1 query in brief generation
date: 2026-01-30
status: complete
tags: [performance, database, eager-loading]
modules: [brief-system, email-processing]
---
```

### Spec

```yaml
---
title: User authentication flow
date: 2026-01-28
status: draft
tags: [auth, security, login]
modules: [auth-service, user-model]
related: [.lore/research/oauth-patterns.md]
req-prefix: AUTH           # Optional: overrides auto-generated prefix
---
```

### Brainstorm

```yaml
---
title: Compound loop for lore-development
date: 2026-01-30
status: open
tags: [methodology, feedback-loop, knowledge-management]
modules: [lore-development]
---
```

### Design

```yaml
---
title: Deduplication algorithm for history sync
date: 2026-02-03
status: draft
tags: [algorithm, deduplication, sync, data-structures]
modules: [history-service, stream-processor]
related: [.lore/specs/history-sync.md]
---
```

### Research

```yaml
---
title: OAuth 2.0 patterns for CLI tools
date: 2026-01-25
status: active
tags: [oauth, authentication, cli, security]
---
```

### Diagram

```yaml
---
title: Message flow between user and AI
date: 2026-01-29
status: current
tags: [architecture, messaging, websocket]
modules: [chat-service, ai-client]
---
```

### Reference (Excavated Feature)

```yaml
---
title: User authentication feature
date: 2026-01-30
status: current
tags: [auth, login, session]
modules: [auth-service, user-model]
---
```

### Issue

```yaml
---
title: Session dialog overflow on narrow viewports
date: 2026-02-18
status: open
tags: [ui, layout, responsive]
modules: [session-dialog]
---
```

### Vision

```yaml
---
title: Vibe Garden Vision
date: 2026-03-16
status: draft
tags: [vision]
---
```

## Tag Guidelines

- Use kebab-case: `eager-loading` not `eagerLoading`
- Be specific: `n-plus-one` not just `performance`
- Include domain terms: `auth`, `payment`, `email`
- Include problem types: `bug`, `optimization`, `refactor`

## Module Guidelines

- Match codebase structure where possible
- Use kebab-case: `brief-system` not `BriefSystem`
- Be consistent across documents
- Omit if document is methodology/process focused (not code-related)

## Search Behavior

The `lore-researcher` agent greps these fields to find related prior work:
- `title:` for topic matches
- `tags:` for keyword matches
- `modules:` for codebase area matches

Documents without frontmatter won't be found by search. Use `/tend` to retrofit old documents.
