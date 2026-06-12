# Lore Document Schema

Single source of truth for document structure, metadata, and body format across all `.lore/` document types.

## File Format

All lore documents are Markdown files (`.md` extension). Metadata is carried in a YAML frontmatter block at the top of the file. Content follows as Markdown.

```markdown
---
title: Descriptive document title
date: YYYY-MM-DD
status: ...
tags: [tag-one, tag-two]
# optional fields below
modules: [module-one, module-two]
related: [.lore/path/to/other.md, .lore/path/to/another.md]
---

# Descriptive document title

<!-- document content in Markdown -->
```

The `title` appears twice: once in frontmatter (`title:`) and once as the body `# H1`. Search relies on both.

## Body Format

Write the body in **Markdown**. Prose, lists, requirement tables, and decisions are Markdown. This is the default for roughly 90% of every document.

Reach for **embedded HTML** only when a visual carries meaning that Markdown cannot:

- color-coding (status badges, risk levels)
- charts or diagrams as inline `<svg>`
- side-by-side visual comparison

When you do, write the HTML **raw and inline** so it renders. Never put it in a ```` ``` ```` fence — a fence shows it as source. No `<script>`, no external resources, no whole-document CSS scaffolding. Keep the HTML local to the section that needs it.

Render target is local editors (Obsidian, VS Code preview, pandoc, browser), where inline `style=` and `<svg>` render fully.

## The three-directory model

`.lore/` is organized into three top-level directories. Every lore document lives under exactly one of them:

- **`.lore/work/`** — work scaffolding. Session-bound material: brainstorms, specs, designs, plans, tasks, notes, research, retros, issues, ideas, validation, stubs, excavation indices, session diagrams.
- **`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Distilled feature docs, vision, current-state diagrams.
- **`.lore/learned/`** — operational imperatives, mistakes-only, worker-oriented. Written by `/learn`.

Status values are scoped to the directory tree the document lives in (see "Status Values" below).

## Common Fields

All lore documents include these fields:

| Field | Required | Notes |
|-------|----------|-------|
| title | Yes | Used for search; repeated in body as `# H1` |
| date | Yes | Creation or completion date, `YYYY-MM-DD` |
| status | Yes | Document-type-specific (see below) |
| tags | Yes | List of kebab-case keywords |
| modules | No | List of kebab-case module names |
| related | No | List of paths to related lore documents |

Array fields (`tags`, `modules`, `related`) use YAML list syntax: `[a, b, c]` inline, or a block list with `-` items.

## Spec-Specific Fields

Specs support one additional optional field:

```yaml
req-prefix: AUTH
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

### Work documents

Work artifacts retain meaningful per-type lifecycles. The directory key is `work/<type>`.

| Type | Directory | Valid Status Values |
|------|-----------|---------------------|
| brainstorm | `.lore/work/brainstorm/` | `open`, `parked`, `resolved`, `archived` |
| spec | `.lore/work/specs/` | `draft`, `approved`, `implemented`, `superseded`, `archived` |
| design | `.lore/work/design/` | `draft`, `approved`, `implemented`, `superseded`, `archived` |
| plan | `.lore/work/plans/` | `draft`, `approved`, `executed`, `archived` |
| task | `.lore/work/tasks/` | `pending`, `complete`, `skipped` |
| notes | `.lore/work/notes/` | `in_progress`, `complete`, `archived` |
| research | `.lore/work/research/` | `active`, `archived` |
| retro | `.lore/work/retros/` | `open`, `archived` |
| issue | `.lore/work/issues/` | `open`, `resolved`, `wontfix`, `archived` |
| diagram (work) | `.lore/work/diagrams/` | `current`, `outdated`, `archived` |

Diagrams in both `work/diagrams/` and `reference/diagrams/` share the same status set: `current` while accurate, `outdated` once not, `archived` once no longer worth maintaining. The split is at the directory level, not the status level.

### Reference documents

All reference documents share one status set:

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/reference/` (and any subdirectory) | `current`, `outdated`, `archived` |

### Learned documents

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/learned/` | `active`, `superseded` |

## Notes-Specific Fields

Notes support one additional required field:

```yaml
source: .lore/work/plans/auth-flow.md
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the spec, design, or plan being implemented. Enables retro to diff plan vs reality. |

## Task-Specific Fields

Tasks support two additional required fields:

```yaml
source: .lore/work/plans/auth-flow.md
sequence: 1
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the plan this task was decomposed from. Enables implement to find the parent plan. |
| sequence | Yes | Integer ordering within the task set. Determines execution order in implement. |

## Vision-Specific Notes

The vision document lives at `.lore/reference/vision.md` (one per project). It uses the common fields only; `modules` is intentionally omitted because the vision applies to the entire project. A vision becomes `current` when the user edits the meta directly or tells the skill to mark it so.

## Examples

### Notes (Implementation)

```markdown
---
title: "Implementation notes: auth-flow"
date: 2026-02-05
status: in_progress
tags: [implementation, notes]
source: .lore/work/plans/auth-flow.md
modules: [auth-service]
---

# Implementation notes: auth-flow

...
```

### Task

```markdown
---
title: Add auth middleware
date: 2026-02-10
status: pending
tags: [task]
source: .lore/work/plans/auth-flow.md
sequence: 1
modules: [auth-service]
---

# Add auth middleware

...
```

### Retro

```markdown
---
title: N+1 query in brief generation
date: 2026-01-30
status: open
tags: [performance, database, eager-loading]
modules: [brief-system, email-processing]
---

# N+1 query in brief generation

...
```

### Spec

```markdown
---
title: User authentication flow
date: 2026-01-28
status: draft
tags: [auth, security, login]
modules: [auth-service, user-model]
related: [.lore/work/research/oauth-patterns.md]
req-prefix: AUTH
---

# User authentication flow

...
```

### Brainstorm

```markdown
---
title: Compound loop for lore-development
date: 2026-01-30
status: open
tags: [methodology, feedback-loop, knowledge-management]
modules: [lore-development]
---

# Compound loop for lore-development

...
```

### Design

```markdown
---
title: Deduplication algorithm for history sync
date: 2026-02-03
status: draft
tags: [algorithm, deduplication, sync, data-structures]
modules: [history-service, stream-processor]
related: [.lore/work/specs/history-sync.md]
---

# Deduplication algorithm for history sync

...
```

### Plan

```markdown
---
title: "Implementation plan: auth-flow"
date: 2026-02-05
status: draft
tags: [plan, auth]
modules: [auth-service]
related: [.lore/work/specs/auth-flow.md]
---

# Implementation plan: auth-flow

...
```

New plans always start as `draft`. They move to `approved` when the user accepts them, and `executed` after implementation completes.

### Research

```markdown
---
title: OAuth 2.0 patterns for CLI tools
date: 2026-01-25
status: active
tags: [oauth, authentication, cli, security]
---

# OAuth 2.0 patterns for CLI tools

...
```

### Diagram (work, session-bound)

```markdown
---
title: Message flow between user and AI
date: 2026-01-29
status: current
tags: [architecture, messaging, websocket]
modules: [chat-service, ai-client]
---

# Message flow between user and AI

...
```

A diagram is a strong case for embedded HTML: an inline `<svg>` of the topology beats a prose description. Write it raw and inline per the Body Format rule.

### Reference (Distilled Feature)

```markdown
---
title: User authentication feature
date: 2026-01-30
status: current
tags: [auth, login, session]
modules: [auth-service, user-model]
---

# User authentication feature

...
```

### Issue

```markdown
---
title: Session dialog overflow on narrow viewports
date: 2026-02-18
status: open
tags: [ui, layout, responsive]
modules: [session-dialog]
---

# Session dialog overflow on narrow viewports

...
```

### Vision

```markdown
---
title: Vibe Garden Vision
date: 2026-03-16
status: current
tags: [vision]
---

# Vibe Garden Vision

...
```

### Learned entry

```markdown
---
title: Don't ship the same path string in two places
date: 2026-04-24
status: active
tags: [refactor, hardcoded-paths]
modules: [lore-development]
---

# Don't ship the same path string in two places

...
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

Documents without frontmatter won't be found by search.
