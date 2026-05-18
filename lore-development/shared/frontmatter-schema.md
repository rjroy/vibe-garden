# Lore Document Frontmatter Schema

> **Note:** This file is a reference for Claude, not a user-facing artifact. It stays markdown.

Single source of truth for frontmatter fields across all `.lore/` document types.

## The three-directory model

`.lore/` is organized into three top-level directories. Every lore document lives under exactly one of them:

- **`.lore/work/`** — work scaffolding. Session-bound material: brainstorms, specs, designs, plans, tasks, notes, research, retros, issues, ideas, validation, stubs, excavation indices, session diagrams.
- **`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Distilled feature docs, vision, current-state diagrams.
- **`.lore/learned/`** — operational imperatives, mistakes-only, worker-oriented. Written by `/learn`.

Status values are scoped to the directory tree the document lives in (see "Status Values" below).

## Common Fields

All lore documents should include these fields:

```html
<meta name="lore-title" content="Descriptive title, used for search">
<meta name="lore-date" content="YYYY-MM-DD">
<meta name="lore-status" content="string">
<meta name="lore-tags" content="tag-one, tag-two, tag-three">
<meta name="lore-modules" content="module-one, module-two">
<meta name="lore-related" content=".lore/path/to/doc.html, .lore/path/to/other.html">
```

## Required vs Optional

| Field | Required | Notes |
|-------|----------|-------|
| lore-title | Yes | Used by lore-researcher for search |
| lore-date | Yes | When document was created/completed |
| lore-status | Yes | Enables `/tend` hygiene checks |
| lore-tags | Yes | Primary search mechanism |
| lore-modules | No | Include when document relates to specific codebase areas |
| lore-related | No | Cross-references to other lore documents |

## Spec-Specific Fields

Specs support an additional optional field:

```html
<meta name="lore-req-prefix" content="AUTH">
```

| Field | Required | Notes |
|-------|----------|-------|
| lore-req-prefix | No | Override auto-generated prefix. Use 3-12 uppercase chars. |

If omitted, prefix is auto-generated from the spec filename (first 2 segments, uppercase, max 12 chars).

Examples:
- `auth-flow.html` → `AUTH-FLOW`
- `user-authentication-oauth2.html` → `USER-AUTH`
- With `<meta name="lore-req-prefix" content="AUTH">` → `AUTH`

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

`/retro`'s reshape collapses the old `complete` status: retros are free-form notes, not analyzed artifacts, so "complete" has no distinct meaning. A retro is `open` while it can still be amended and `archived` once the work it tracks is fully past.

Diagrams are the one work type whose lifecycle is visual currency rather than a work-cycle state. REQ-REDESIGN-9 does not enumerate diagram statuses, and REQ-REDESIGN-5 splits diagrams by purpose (session-bound vs current-state) rather than by lifecycle. Both `work/diagrams/` and `reference/diagrams/` therefore share the same `current / outdated / archived` set: a diagram is `current` while it accurately depicts what it claims to depict, `outdated` once it does not, and `archived` once it is no longer worth maintaining. The split happens at the directory level (which subtree a diagram belongs to), not at the status level.

### Reference documents

All reference documents share one status set:

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/reference/` (and any subdirectory, including `.lore/reference/diagrams/`) | `current`, `outdated`, `archived` |

### Learned documents

Learned entries share one minimal status set. Lifecycle beyond this is owned by `.lore/work/issues/design-learned-structure.md`.

| Directory | Valid Status Values |
|-----------|---------------------|
| `.lore/learned/` | `active`, `superseded` |

## Notes-Specific Fields

Notes support an additional required field:

```html
<meta name="lore-source" content=".lore/work/plans/auth-flow.html">
```

| Field | Required | Notes |
|-------|----------|-------|
| lore-source | Yes | Path to the spec, design, or plan being implemented. Enables retro to diff plan vs reality. |

## Task-Specific Fields

Tasks support additional required fields:

```html
<meta name="lore-source" content=".lore/work/plans/auth-flow.html">
<meta name="lore-sequence" content="1">
```

| Field | Required | Notes |
|-------|----------|-------|
| lore-source | Yes | Path to the plan this task was decomposed from. Enables implement to find the parent plan. |
| lore-sequence | Yes | Integer ordering within the task set. Determines execution order in implement. |

## Vision-Specific Notes

The vision document lives at `.lore/reference/vision.html` (one per project, under `reference/`). It uses the common fields only; `lore-modules` is intentionally omitted because the vision applies to the entire project, not specific modules. As a reference document, its status is one of `current`, `outdated`, or `archived`. A vision becomes `current` when the user edits the meta tag directly or tells the skill to mark it so. The skill does not approve on the user's behalf.

## Examples

### Notes (Implementation)

```html
<meta name="lore-title" content="Implementation notes: auth-flow">
<meta name="lore-date" content="2026-02-05">
<meta name="lore-status" content="in_progress">
<meta name="lore-tags" content="implementation, notes">
<meta name="lore-source" content=".lore/work/plans/auth-flow.html">
<meta name="lore-modules" content="auth-service">
```

### Task

```html
<meta name="lore-title" content="Add auth middleware">
<meta name="lore-date" content="2026-02-10">
<meta name="lore-status" content="pending">
<meta name="lore-tags" content="task">
<meta name="lore-source" content=".lore/work/plans/auth-flow.html">
<meta name="lore-sequence" content="1">
<meta name="lore-modules" content="auth-service">
```

### Retro

```html
<meta name="lore-title" content="N+1 query in brief generation">
<meta name="lore-date" content="2026-01-30">
<meta name="lore-status" content="open">
<meta name="lore-tags" content="performance, database, eager-loading">
<meta name="lore-modules" content="brief-system, email-processing">
```

### Spec

```html
<meta name="lore-title" content="User authentication flow">
<meta name="lore-date" content="2026-01-28">
<meta name="lore-status" content="draft">
<meta name="lore-tags" content="auth, security, login">
<meta name="lore-modules" content="auth-service, user-model">
<meta name="lore-related" content=".lore/work/research/oauth-patterns.html">
<meta name="lore-req-prefix" content="AUTH">
```

### Brainstorm

```html
<meta name="lore-title" content="Compound loop for lore-development">
<meta name="lore-date" content="2026-01-30">
<meta name="lore-status" content="open">
<meta name="lore-tags" content="methodology, feedback-loop, knowledge-management">
<meta name="lore-modules" content="lore-development">
```

### Design

```html
<meta name="lore-title" content="Deduplication algorithm for history sync">
<meta name="lore-date" content="2026-02-03">
<meta name="lore-status" content="draft">
<meta name="lore-tags" content="algorithm, deduplication, sync, data-structures">
<meta name="lore-modules" content="history-service, stream-processor">
<meta name="lore-related" content=".lore/work/specs/history-sync.html">
```

### Plan

```html
<meta name="lore-title" content="Implementation plan: auth-flow">
<meta name="lore-date" content="2026-02-05">
<meta name="lore-status" content="draft">
<meta name="lore-tags" content="plan, auth">
<meta name="lore-modules" content="auth-service">
<meta name="lore-related" content=".lore/work/specs/auth-flow.html">
```

New plans should always start as `draft`. They move to `approved` when the user accepts them, and `executed` after implementation completes.

### Research

```html
<meta name="lore-title" content="OAuth 2.0 patterns for CLI tools">
<meta name="lore-date" content="2026-01-25">
<meta name="lore-status" content="active">
<meta name="lore-tags" content="oauth, authentication, cli, security">
```

### Diagram (work, session-bound)

```html
<meta name="lore-title" content="Message flow between user and AI">
<meta name="lore-date" content="2026-01-29">
<meta name="lore-status" content="current">
<meta name="lore-tags" content="architecture, messaging, websocket">
<meta name="lore-modules" content="chat-service, ai-client">
```

### Reference (Distilled Feature)

```html
<meta name="lore-title" content="User authentication feature">
<meta name="lore-date" content="2026-01-30">
<meta name="lore-status" content="current">
<meta name="lore-tags" content="auth, login, session">
<meta name="lore-modules" content="auth-service, user-model">
```

### Issue

```html
<meta name="lore-title" content="Session dialog overflow on narrow viewports">
<meta name="lore-date" content="2026-02-18">
<meta name="lore-status" content="open">
<meta name="lore-tags" content="ui, layout, responsive">
<meta name="lore-modules" content="session-dialog">
```

### Vision

```html
<meta name="lore-title" content="Vibe Garden Vision">
<meta name="lore-date" content="2026-03-16">
<meta name="lore-status" content="current">
<meta name="lore-tags" content="vision">
```

### Learned entry

```html
<meta name="lore-title" content="Don't ship the same path string in two places">
<meta name="lore-date" content="2026-04-24">
<meta name="lore-status" content="active">
<meta name="lore-tags" content="refactor, hardcoded-paths">
<meta name="lore-modules" content="lore-development">
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
- `name="lore-title"` for topic matches
- `name="lore-tags"` for keyword matches
- `name="lore-modules"` for codebase area matches

Documents without meta tags won't be found by search. Use `/tend` to retrofit old documents.
