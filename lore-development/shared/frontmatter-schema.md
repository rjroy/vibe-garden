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

## The four-zone model

`.lore/` separates disposable local context, shared historical work, maintained reference, and operational learning:

- **`.lore/local/`** — disposable, gitignored plans, implementation notes, and generic task context. New plans and notes go here; task artifacts are not automatic implementation phases.
- **`.lore/work/`** — shared historical conversations and work. Intents, brainstorms, legacy specs, designs, research, retros, issues, ideas, validation, stubs, excavation indices, and session diagrams remain discoverable. Existing tracked content is preserved. Legacy plans, tasks, and notes remain readable historical context, not binding instructions.
- **`.lore/reference/`** — solidified, system-oriented documentation. What the code cannot say. Distilled feature docs, vision, current-state diagrams.
- **`.lore/learned/`** — operational imperatives, mistakes-only, worker-oriented. This zone is reserved for useful operational learning; no lore-development skill currently writes it.

All lore uses the same four lifecycle statuses (see "Status Values" below). Initialize local storage with `python3 <path-to-lore-development>/scripts/ensure_local.py <project-root>` before writing local artifacts. The helper creates the directory, adds a root-anchored ignore rule, and verifies effective ignore behavior in Git worktrees.

## Common Fields

All lore documents include these fields:

| Field | Required | Notes |
|-------|----------|-------|
| title | Yes | Used for search; repeated in body as `# H1` |
| date | Yes | Creation or completion date, `YYYY-MM-DD` |
| status | Yes | Shared four-value lifecycle across all lore zones (see below) |
| tags | Yes | List of kebab-case keywords |
| modules | No | List of kebab-case module names |
| related | No | List of paths to related lore documents |

Array fields (`tags`, `modules`, `related`) use YAML list syntax: `[a, b, c]` inline, or a block list with `-` items.

## Optional Review Annotations

Lore Garden supports optional `comments`, `todos`, and `starred` frontmatter
fields on work documents. These are annotations for review, not lifecycle
statuses, approval signals, or implementation authorization:

```yaml
comments:
  - author: rjroy
    at: "2026-10-06"
    text: Please clarify this point.
todos:
  - text: Check the migration boundary
    done: false
starred: true
```

| Field | Required shape | Notes |
|-------|----------------|-------|
| comments | Optional list of records, each with string `author`, `at`, and `text` | A comment is review context; it does not approve or authorize work. |
| todos | Optional list of records, each with string `text` and boolean `done` | Document-level follow-ups only, not a replacement for Beads task tracking. |
| starred | Optional boolean | A marker for a document; it does not indicate approval or priority authorization. |

Do not add empty annotation fields to new documents. When editing an existing
document, preserve its comments, todos, star, and unrelated frontmatter unless
the user explicitly asks to change them. Do not infer approval, completion, or
permission to implement from comments, checked follow-ups, or a star. Do not
resolve comments or mark follow-ups done automatically just because the agent
believes the work is finished; change annotations only when explicitly asked.
The lifecycle remains `draft`, `approved`, `completed`, or `archived` as defined
in Status Values above; annotations do not add or replace lifecycle states.

## Status Values

Every document in all four zones, including nested reference and learned documents, uses exactly these lifecycle values:

| Status | Meaning |
|--------|---------|
| `draft` | Agent-created work not yet explicitly approved by the user. Default for new documents. |
| `approved` | The user explicitly approved the document, including by editing it to approve it, or asked for its relevant next process step. |
| `completed` | The agent completed the work applicable to the document. This does not imply user approval. |
| `archived` | The document is archived for any reason. |

Status describes document/work lifecycle, not maturity, correctness, currency, or authority. Do not infer approval from arbitrary edits; user editing that signals approval/acceptance is explicit approval. Current user direction can revise an approved artifact; approval is not a veto or a mandatory gate. Do not ask for approval on minor transitions or every document. Approval includes the user asking to proceed to the relevant next process step; do not treat agent guesses or a generic request to do work as approval of a particular artifact. Field-guide freshness uses separate `fg-status` metadata (for example `current`/`stale`) and is not this lifecycle field. Beads issue status is also separate.

The schema validator enforces only these four values uniformly in `.lore/work/`, `.lore/local/`, `.lore/reference/` (including subdirectories), and `.lore/learned/`.

## Notes-Specific Fields

Notes may include a source field when a particular artifact informed the work:

```yaml
source: .lore/work/plans/auth-flow.md
```

| Field | Required | Notes |
|-------|----------|-------|
| source | No | Path to a relevant intent, spec, design, plan, or other context. Useful for navigation, but notes do not require a source artifact. |

## Task-Specific Fields

Historical tasks under `.lore/work/tasks/` support two additional required
fields. Generic task context under `.lore/local/tasks/` uses common fields only
and is not an execution sequence.

```yaml
source: .lore/work/plans/auth-flow.md
sequence: 1
```

| Field | Required | Notes |
|-------|----------|-------|
| source | Required for historical `.lore/work/tasks/`; optional for local tasks | Path to relevant context. |
| sequence | Required for historical `.lore/work/tasks/`; optional for local tasks | Historical ordering only; it does not determine `/implement` execution order. |

## Vision-Specific Notes

The vision document lives at `.lore/reference/vision.md` (one per project). It uses the common fields only; `modules` is intentionally omitted because the vision applies to the entire project. Use the shared lifecycle: explicit user approval or a request for its relevant next process step may mark it `approved`; agent completion is `completed`. Freshness is not represented by lifecycle status.

## Examples

### Notes (Implementation)

```markdown
---
title: "Implementation notes: auth-flow"
date: 2026-02-05
status: draft
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
status: draft
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
status: draft
tags: [performance, database, eager-loading]
modules: [brief-system, email-processing]
---

# N+1 query in brief generation

...
```

### Intent

```markdown
---
title: Why users need a simpler sign-in flow
date: 2026-01-28
status: draft
tags: [auth, security, sign-in]
modules: [auth-service, user-model]
related: [.lore/work/research/oauth-patterns.md]
---

# Why users need a simpler sign-in flow

The current sign-in flow is confusing for returning users. We want to make it
easier to get back into an account without weakening account security. We have
not chosen an implementation; discuss options and useful validation in the plan.
```

Older `.lore/work/specs/` documents remain discoverable historical context. Their
requirement IDs and validation sections do not make them authoritative for
current work. Explicit migration normalizes old lifecycle status to the four
values and records a changed original value in optional `legacy_status`. This
does not make a document newly authored or confer authority. Do not rewrite
project histories merely to normalize status.

On explicitly migrated artifacts, old `draft`/`open`/`pending`/`in_progress`
become `draft`; `approved` stays `approved`; `completed`/`complete`/
`implemented`/`executed`/`resolved` become `completed`; `archived`/
`superseded`/`parked`/`outdated`/`wontfix`/`skipped` become `archived`.
Old `current` and `active` become `completed`: those labels describe maintained
or agent-produced content, not explicit user approval or guaranteed currency.
An unrecognized value blocks preview rather than guessing. This migration is
limited to mapped legacy-layout artifacts; it does not normalize project
histories, wikis, or current-zone files en masse.

### Brainstorm

```markdown
---
title: Compound loop for lore-development
date: 2026-01-30
status: draft
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

New plans start as `draft`. Mark them `approved` only on explicit user approval or when the user asks for the relevant next process step; mark applicable work `completed` when it is done. Implementing a plan does not imply that the plan itself was user-approved.

### Research

```markdown
---
title: OAuth 2.0 patterns for CLI tools
date: 2026-01-25
status: draft
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
status: completed
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
status: approved
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
status: draft
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
status: approved
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
status: completed
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

The `lore-researcher` agent uses these fields to rank related prior work:
- `title:` for topic matches
- `tags:` for keyword matches
- `modules:` for codebase area matches

It also searches document bodies. A document without frontmatter can therefore
be found by body text, but it is lower-confidence legacy material because its
type, lifecycle status, and module scope cannot be established from metadata.
