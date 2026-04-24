# Lore Document Frontmatter Schema

Single source of truth for frontmatter fields across all `.lore/` document types.

## The three-directory model

`.lore/` is organized into three top-level directories. Every lore document lives under exactly one of them:

- **`.lore/build/`** — work scaffolding. Session-bound material: brainstorms, specs, designs, plans, tasks, notes, research, retros, issues, ideas, validation, stubs, excavation indices, session diagrams.
- **`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Excavated feature docs, vision, current-state diagrams.
- **`.lore/learned/`** — operational imperatives, mistakes-only, worker-oriented. Written by `/learn`.

Status values are scoped to the directory tree the document lives in (see "Status Values" below).

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

## Status Values

Status values are organized into three sets, one per top-level directory.

### Build documents

Build artifacts retain meaningful per-type lifecycles. The directory key is `build/<type>`.

| Type | Directory | Valid Status Values |
|------|-----------|---------------------|
| brainstorm | `.lore/build/brainstorm/` | `open`, `parked`, `resolved`, `archived` |
| spec | `.lore/build/specs/` | `draft`, `approved`, `implemented`, `superseded`, `archived` |
| design | `.lore/build/design/` | `draft`, `approved`, `implemented`, `superseded`, `archived` |
| plan | `.lore/build/plans/` | `draft`, `approved`, `executed`, `archived` |
| task | `.lore/build/tasks/` | `pending`, `complete`, `skipped` |
| notes | `.lore/build/notes/` | `in_progress`, `complete`, `archived` |
| research | `.lore/build/research/` | `active`, `archived` |
| retro | `.lore/build/retros/` | `open`, `archived` |
| issue | `.lore/build/issues/` | `open`, `resolved`, `wontfix`, `archived` |
| diagram (build) | `.lore/build/diagrams/` | `current`, `outdated`, `archived` |

`/retro`'s reshape collapses the old `complete` status: retros are free-form notes, not analyzed artifacts, so "complete" has no distinct meaning. A retro is `open` while it can still be amended and `archived` once the work it tracks is fully past.

### Reference documents

All reference documents share one status set:

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/reference/` (and any subdirectory, including `.lore/reference/diagrams/`) | `current`, `outdated`, `archived` |

### Learned documents

Learned entries share one minimal status set. Lifecycle beyond this is owned by `.lore/build/issues/design-learned-structure.md`.

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/learned/` | `active`, `superseded` |

## Notes-Specific Fields

Notes support an additional required field:

```yaml
---
source: .lore/build/plans/auth-flow.md    # Path to the source artifact (required)
---
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the spec, design, or plan being implemented. Enables retro to diff plan vs reality. |

## Task-Specific Fields

Tasks support additional required fields:

```yaml
---
source: .lore/build/plans/auth-flow.md    # Path to the plan this task was decomposed from (required)
sequence: 1                                # Integer ordering within the task set (required)
---
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the plan this task was decomposed from. Enables implement to find the parent plan. |
| sequence | Yes | Integer ordering within the task set. Determines execution order in implement. |

## Vision-Specific Notes

The vision document lives at `.lore/reference/vision.md` (one per project, under `reference/`). It uses the common fields only; `modules` is intentionally omitted because the vision applies to the entire project, not specific modules. As a reference document, its status is one of `current`, `outdated`, or `archived`. A vision becomes `current` when the user edits the frontmatter directly or tells the skill to mark it so. The skill does not approve on the user's behalf.

## Examples

### Notes (Implementation)

```yaml
---
title: "Implementation notes: auth-flow"
date: 2026-02-05
status: in_progress
tags: [implementation, notes]
source: .lore/build/plans/auth-flow.md
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
source: .lore/build/plans/auth-flow.md
sequence: 1
modules: [auth-service]
---
```

### Retro

```yaml
---
title: N+1 query in brief generation
date: 2026-01-30
status: open
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
related: [.lore/build/research/oauth-patterns.md]
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
related: [.lore/build/specs/history-sync.md]
---
```

### Plan

```yaml
---
title: "Implementation plan: auth-flow"
date: 2026-02-05
status: draft
tags: [plan, auth]
modules: [auth-service]
related: [.lore/build/specs/auth-flow.md]
---
```

New plans should always start as `draft`. They move to `approved` when the user accepts them, and `executed` after implementation completes.

### Research

```yaml
---
title: OAuth 2.0 patterns for CLI tools
date: 2026-01-25
status: active
tags: [oauth, authentication, cli, security]
---
```

### Diagram (build, session-bound)

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
status: current
tags: [vision]
---
```

### Learned entry

```yaml
---
title: Don't ship the same path string in two places
date: 2026-04-24
status: active
tags: [refactor, hardcoded-paths]
modules: [lore-development]
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
