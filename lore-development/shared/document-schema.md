# Lore Document Schema

Single source of truth for HTML structure and metadata across all `.lore/` document types.

## File Format

All lore documents are HTML files (`.html` extension). Metadata is carried in `<meta>` tags inside `<head>`. Content lives in `<body>`.

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Descriptive document title</title>
  <meta name="date" content="YYYY-MM-DD">
  <meta name="status" content="...">
  <meta name="tags" content="tag-one, tag-two">
  <!-- optional fields below -->
  <meta name="modules" content="module-one, module-two">
  <meta name="related" content=".lore/path/to/other.html, .lore/path/to/another.html">
</head>
<body>
  <h1>Descriptive document title</h1>
  <!-- document content -->
</body>
</html>
```

## The three-directory model

`.lore/` is organized into three top-level directories. Every lore document lives under exactly one of them:

- **`.lore/work/`** — work scaffolding. Session-bound material: brainstorms, specs, designs, plans, tasks, notes, research, retros, issues, ideas, validation, stubs, excavation indices, session diagrams.
- **`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Distilled feature docs, vision, current-state diagrams.
- **`.lore/learned/`** — operational imperatives, mistakes-only, worker-oriented. Written by `/learn`.

Status values are scoped to the directory tree the document lives in (see "Status Values" below).

## Common Fields

All lore documents include these fields:

| Field | HTML Element | Required | Notes |
|-------|-------------|----------|-------|
| title | `<title>` + `<h1>` | Yes | Used for search; repeated in body as `<h1>` |
| date | `<meta name="date">` | Yes | Creation or completion date, `YYYY-MM-DD` |
| status | `<meta name="status">` | Yes | Document-type-specific (see below) |
| tags | `<meta name="tags">` | Yes | Comma-separated kebab-case keywords |
| modules | `<meta name="modules">` | No | Comma-separated kebab-case module names |
| related | `<meta name="related">` | No | Comma-separated paths to related lore documents |

Array fields (tags, modules, related) use comma-separated values within a single `content` attribute.

## Spec-Specific Fields

Specs support one additional optional field:

```html
<meta name="req-prefix" content="AUTH">
```

| Field | Required | Notes |
|-------|----------|-------|
| req-prefix | No | Override auto-generated prefix. Use 3-12 uppercase chars. |

If omitted, prefix is auto-generated from the spec filename (first 2 segments, uppercase, max 12 chars).

Examples:
- `auth-flow.html` → `AUTH-FLOW`
- `user-authentication-oauth2.html` → `USER-AUTH`
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

```html
<meta name="source" content=".lore/work/plans/auth-flow.html">
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the spec, design, or plan being implemented. Enables retro to diff plan vs reality. |

## Task-Specific Fields

Tasks support two additional required fields:

```html
<meta name="source" content=".lore/work/plans/auth-flow.html">
<meta name="sequence" content="1">
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Yes | Path to the plan this task was decomposed from. Enables implement to find the parent plan. |
| sequence | Yes | Integer ordering within the task set. Determines execution order in implement. |

## Vision-Specific Notes

The vision document lives at `.lore/reference/vision.html` (one per project). It uses the common fields only; `modules` is intentionally omitted because the vision applies to the entire project. A vision becomes `current` when the user edits the meta directly or tells the skill to mark it so.

## Examples

### Notes (Implementation)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Implementation notes: auth-flow</title>
  <meta name="date" content="2026-02-05">
  <meta name="status" content="in_progress">
  <meta name="tags" content="implementation, notes">
  <meta name="source" content=".lore/work/plans/auth-flow.html">
  <meta name="modules" content="auth-service">
</head>
<body>
  <h1>Implementation notes: auth-flow</h1>
  ...
</body>
</html>
```

### Task

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Add auth middleware</title>
  <meta name="date" content="2026-02-10">
  <meta name="status" content="pending">
  <meta name="tags" content="task">
  <meta name="source" content=".lore/work/plans/auth-flow.html">
  <meta name="sequence" content="1">
  <meta name="modules" content="auth-service">
</head>
<body>
  <h1>Add auth middleware</h1>
  ...
</body>
</html>
```

### Retro

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>N+1 query in brief generation</title>
  <meta name="date" content="2026-01-30">
  <meta name="status" content="open">
  <meta name="tags" content="performance, database, eager-loading">
  <meta name="modules" content="brief-system, email-processing">
</head>
<body>
  <h1>N+1 query in brief generation</h1>
  ...
</body>
</html>
```

### Spec

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>User authentication flow</title>
  <meta name="date" content="2026-01-28">
  <meta name="status" content="draft">
  <meta name="tags" content="auth, security, login">
  <meta name="modules" content="auth-service, user-model">
  <meta name="related" content=".lore/work/research/oauth-patterns.html">
  <meta name="req-prefix" content="AUTH">
</head>
<body>
  <h1>User authentication flow</h1>
  ...
</body>
</html>
```

### Brainstorm

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Compound loop for lore-development</title>
  <meta name="date" content="2026-01-30">
  <meta name="status" content="open">
  <meta name="tags" content="methodology, feedback-loop, knowledge-management">
  <meta name="modules" content="lore-development">
</head>
<body>
  <h1>Compound loop for lore-development</h1>
  ...
</body>
</html>
```

### Design

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Deduplication algorithm for history sync</title>
  <meta name="date" content="2026-02-03">
  <meta name="status" content="draft">
  <meta name="tags" content="algorithm, deduplication, sync, data-structures">
  <meta name="modules" content="history-service, stream-processor">
  <meta name="related" content=".lore/work/specs/history-sync.html">
</head>
<body>
  <h1>Deduplication algorithm for history sync</h1>
  ...
</body>
</html>
```

### Plan

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Implementation plan: auth-flow</title>
  <meta name="date" content="2026-02-05">
  <meta name="status" content="draft">
  <meta name="tags" content="plan, auth">
  <meta name="modules" content="auth-service">
  <meta name="related" content=".lore/work/specs/auth-flow.html">
</head>
<body>
  <h1>Implementation plan: auth-flow</h1>
  ...
</body>
</html>
```

New plans always start as `draft`. They move to `approved` when the user accepts them, and `executed` after implementation completes.

### Research

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OAuth 2.0 patterns for CLI tools</title>
  <meta name="date" content="2026-01-25">
  <meta name="status" content="active">
  <meta name="tags" content="oauth, authentication, cli, security">
</head>
<body>
  <h1>OAuth 2.0 patterns for CLI tools</h1>
  ...
</body>
</html>
```

### Diagram (work, session-bound)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Message flow between user and AI</title>
  <meta name="date" content="2026-01-29">
  <meta name="status" content="current">
  <meta name="tags" content="architecture, messaging, websocket">
  <meta name="modules" content="chat-service, ai-client">
</head>
<body>
  <h1>Message flow between user and AI</h1>
  ...
</body>
</html>
```

### Reference (Distilled Feature)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>User authentication feature</title>
  <meta name="date" content="2026-01-30">
  <meta name="status" content="current">
  <meta name="tags" content="auth, login, session">
  <meta name="modules" content="auth-service, user-model">
</head>
<body>
  <h1>User authentication feature</h1>
  ...
</body>
</html>
```

### Issue

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Session dialog overflow on narrow viewports</title>
  <meta name="date" content="2026-02-18">
  <meta name="status" content="open">
  <meta name="tags" content="ui, layout, responsive">
  <meta name="modules" content="session-dialog">
</head>
<body>
  <h1>Session dialog overflow on narrow viewports</h1>
  ...
</body>
</html>
```

### Vision

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Vibe Garden Vision</title>
  <meta name="date" content="2026-03-16">
  <meta name="status" content="current">
  <meta name="tags" content="vision">
</head>
<body>
  <h1>Vibe Garden Vision</h1>
  ...
</body>
</html>
```

### Learned entry

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Don't ship the same path string in two places</title>
  <meta name="date" content="2026-04-24">
  <meta name="status" content="active">
  <meta name="tags" content="refactor, hardcoded-paths">
  <meta name="modules" content="lore-development">
</head>
<body>
  <h1>Don't ship the same path string in two places</h1>
  ...
</body>
</html>
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
- `<title>` for topic matches
- `<meta name="tags">` for keyword matches
- `<meta name="modules">` for codebase area matches

Documents without this structure won't be found by search.
