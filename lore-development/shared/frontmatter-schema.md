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

## Status Values by Document Type

| Type | Directory | Valid Status Values |
|------|-----------|---------------------|
| brainstorm | `.lore/brainstorm/` | `open`, `resolved`, `parked` |
| spec | `.lore/specs/` | `draft`, `approved`, `implemented`, `superseded` |
| retro | `.lore/retros/` | `complete` |
| research | `.lore/research/` | `active`, `archived` |
| diagram | `.lore/diagrams/` | `current`, `outdated` |
| plan | `.lore/plans/` | `draft`, `approved`, `executed` |
| reference | `.lore/reference/` | `current`, `outdated` |

## Examples

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
