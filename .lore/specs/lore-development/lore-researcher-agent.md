---
title: lore-researcher Agent
date: 2026-01-30
status: implemented
tags: [agent-design, compound-loop, knowledge-retrieval, search]
modules: [lore-development]
related: [.lore/brainstorm/lore-development/compound-loop-lore-development.md]
---

# Spec: lore-researcher Agent

## Overview

An agent that searches `.lore/` for related prior work before new specifications or plans begin. Closes the compound loop by surfacing lessons learned, existing specs, and relevant brainstorms so past knowledge informs new work.

## Entry Points

- Automatic invocation by `/specify` (early in process, before gathering requirements)
- Automatic invocation by `/prep-plan` (before entering plan mode)
- Manual invocation via Task tool with a topic/description

## Requirements

- REQ-1: Agent searches `.lore/retros/` first, then `.lore/specs/`, then `.lore/brainstorm/` (priority order)
- REQ-2: Agent uses fuzzy keyword extraction: synonyms, related terms, not just exact matches
- REQ-3: Agent returns findings inline (not to temp file) for immediate integration
- REQ-4: Agent distills findings to actionable summaries, not full document dumps
- REQ-5: Agent indicates when no related work is found (explicit "nothing found" is useful)
- REQ-6: Agent uses grep-first strategy: filter by frontmatter/headers before reading full files
- REQ-7: Agent runs with `model: haiku` for speed (search task, not deep analysis)
- REQ-8: Agent references `../../shared/frontmatter-schema.md` for field definitions

## Search Strategy

**Keyword extraction from input**:
- Module/component names mentioned
- Technical terms (performance, auth, database, etc.)
- Problem indicators (slow, error, bug, etc.)
- Domain terms (user, payment, email, etc.)

**Fuzzy expansion** (LLM-driven):
The agent uses its own judgment to expand keywords where appropriate. "slow" naturally expands to include "performance", "latency". Domain-specific terms like "EOS SDK" don't expand. Trust the model; don't overcomplicate with lookup tables.

**Grep targets** (frontmatter fields):
- `title:` field
- `tags:` arrays
- `modules:` arrays

**Frontmatter required**: Documents without frontmatter won't be matched. Use `/tend` to retrofit old documents with frontmatter.

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Return findings | Search complete, matches found | Inline markdown with summaries |
| Return "no matches" | Search complete, nothing found | Explicit message that no related work exists |
| Return partial | Some directories missing | Findings from what exists, note what's missing |

## Output Format

```markdown
## Related Learnings

### From Retros

**[Title]** (.lore/retros/filename.md)
Key insight: [1-2 sentence actionable takeaway]

### From Specs

**[Title]** (.lore/specs/filename.md)
Relevance: [Why this existing spec matters for the new work]

### From Brainstorms

**[Title]** (.lore/brainstorm/filename.md)
Explored: [What was considered that might inform this]

---
*No matches in [section]* (when a section has no hits)
```

## Success Criteria

- [ ] Agent finds relevant retros when keywords match
- [ ] Agent finds related specs when topic overlaps
- [ ] Agent returns "no matches" explicitly when nothing found
- [ ] Fuzzy matching catches related terms (not just exact)
- [ ] Output is concise enough to scan in <30 seconds
- [ ] `/specify` invokes agent automatically before requirements gathering
- [ ] `/prep-plan` invokes agent automatically before entering plan mode

## AI Validation

**Defaults** (apply unless overridden):
- Code review by fresh-context sub-agent

**Custom**:
- Integration test: create test retro with known tags, invoke agent with matching topic, verify retro surfaces
- Integration test: invoke agent with unrelated topic, verify "no matches" response

## Interface

**Input**: Plain text description of the topic/feature being specified or planned. Passed via Task tool prompt.

**Output**: Markdown text returned in agent response. Invoking skill includes this in the document's Context section.

## Constraints

- Must be fast (haiku model, grep-first, no full-file reads unless matched)
- No modification of any files (read-only search)
- No conversation history access (operates on input topic only)
- Findings are advisory, not blocking (invoking skill decides what to do with them)

---

## Shared Frontmatter Schema

**Location**: `shared/frontmatter-schema.md` (plugin root)

**Purpose**: Single source of truth for frontmatter fields across all lore document types.

### Schema Definition

```yaml
# Common fields (all document types)
title: string        # Descriptive title, used for search
date: YYYY-MM-DD     # Creation or completion date
status: string       # Document-type-specific status values
tags: [string]       # Searchable keywords (kebab-case)
modules: [string]    # Affected modules/components (kebab-case)

# Optional fields
related: [string]    # Paths to related lore documents
```

### Status Values by Document Type

| Type | Valid Status Values |
|------|---------------------|
| brainstorm | `open`, `resolved`, `parked` |
| spec | `draft`, `approved`, `implemented`, `superseded` |
| retro | `complete` |
| research | `active`, `archived` |
| diagram | `current`, `outdated` |
| plan | `draft`, `approved`, `executed` |

### Example Frontmatter

**Retro**:
```yaml
---
title: N+1 query in brief generation
date: 2026-01-30
status: complete
tags: [performance, database, eager-loading]
modules: [brief-system, email-processing]
---
```

**Spec**:
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

**Brainstorm**:
```yaml
---
title: Compound loop for lore-development
date: 2026-01-30
status: open
tags: [methodology, feedback-loop, knowledge-management]
modules: [lore-development]
---
```

---

## Skill Modifications

### Skills That Write Lore Documents

Each skill that creates `.lore/` files must:
1. Reference `../../shared/frontmatter-schema.md` for field definitions
2. Generate frontmatter with at minimum: `title`, `date`, `status`, `tags`
3. Include `modules` when the document relates to specific codebase areas

**Skills requiring update**:
- `/retro` - already writes to `.lore/retros/`, needs frontmatter
- `/specify` - writes to `.lore/specs/`, needs frontmatter
- `/brainstorm` - writes to `.lore/brainstorm/`, needs frontmatter
- `/research` - writes to `.lore/research/`, needs frontmatter
- `/ddp` - writes to `.lore/diagrams/`, needs frontmatter
- `/prep-plan` - writes to `.lore/plans/`, needs frontmatter

### Retrofitting Old Documents

`/tend` already handles status field hygiene. Extend it to detect documents missing frontmatter and offer to add it. This handles the transition for existing `.lore/` content.

### Skills That Invoke lore-researcher

- `/specify` - invoke agent early, before gathering requirements
- `/prep-plan` - invoke agent before entering plan mode

---

## Context

- Brainstorm: `.lore/brainstorm/lore-development/compound-loop-lore-development.md`
- Related: `.lore/specs/lore-development/fresh-lore-agent.md` (another lore agent, different purpose)
- Inspiration: compound-engineering's `learnings-researcher` agent (grep-first pattern)
