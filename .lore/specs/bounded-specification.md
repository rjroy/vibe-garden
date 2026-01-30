# Spec: Bounded Specification Model for /specify

**Status**: complete

## Overview

Update the `/specify` skill to support bounded specification with explicit stubs, and add an `/update-stubs` skill for tracking outstanding stubs across specs. This model allows users to define what's "in scope" for a given specification layer while documenting connections to undefined areas. The user draws the boundary; the AI records it. Stubs become a managed backlog of known unknowns.

This supports layer-based specification where each spec defines one functional layer with explicit connections to undefined layers. Implementation becomes the gate between layers rather than the end of specification.

## Requirements

### /specify Updates

- REQ-1: Add Entry Points section to spec template (where users arrive at this feature)
- REQ-2: Add Exit Points section with stub notation (where users leave to undefined areas)
- REQ-3: Update process to probe for stubs: after drafting requirements, ask "Are we stubbing [action]?" for each major action, allowing user to define now or mark as stub
- REQ-4: Document stub format and naming: `[STUB: stub-name]` where stub-name uses kebab-case matching spec filename conventions
- REQ-5: Preserve existing functionality (overview, requirements, success criteria, constraints, context, status, fresh-eyes review)

### /update-stubs Skill (New)

- REQ-6: Create skill at `lore-development/skills/update-stubs/SKILL.md`
- REQ-7: Scan all `.md` files in `.lore/specs/` recursively for `[STUB: name]` patterns
- REQ-8: Check each stub against existing specs: stub is resolved if `.lore/specs/[stub-name].md` exists (exact match, case-sensitive)
- REQ-9: Generate/update `.lore/stubs/index.md` with outstanding stubs only (resolved stubs are simply absent)
- REQ-10: Show stub source (which spec contains each stub reference)

### Error Handling

- REQ-11: Validate stub names are valid filenames (no special characters beyond kebab-case)
- REQ-12: Handle duplicate stubs (same stub in multiple specs): list all source specs in index
- REQ-13: Report self-referential stubs as warnings (spec references itself as stub)

## Updated Spec Template

The updated template adds Entry Points and Exit Points while preserving existing sections:

```markdown
# Spec: [Feature Name]

**Status**: draft

## Overview
One paragraph describing what this is.

## Entry Points
How users arrive at this feature:
- [Entry description] (from [source])

## Requirements
- REQ-1: [requirement]
- REQ-2: [requirement]

## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| [Exit name] | [User action or condition] | [STUB: target-name] or [Spec: existing-spec] |

## Success Criteria
How we know this is done:
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
Any boundaries or limitations.

## Context
Links to related `.lore/` documents if relevant.
```

## Success Criteria

How we know this is done:
- [ ] `lore-development/skills/specify/SKILL.md` includes updated template with Entry Points and Exit Points sections
- [ ] Process section includes step for probing major actions ("Are we stubbing X?")
- [ ] Stub notation and naming convention documented in skill
- [ ] `lore-development/skills/update-stubs/SKILL.md` exists with When to Use, Process, and Output sections
- [ ] Running `/update-stubs` produces index of unresolved stubs with source specs
- [ ] Stubs matching existing spec filenames are absent from index (resolved)
- [ ] Invalid stub names reported as errors, self-referential stubs as warnings
- [ ] Existing fresh-eyes review hand-off preserved

## Constraints

- Bounded specification is guidance, not enforcement. The skill suggests structure; users decide depth.
- Stub index is generated on-demand via `/update-stubs` (not auto-updated)
- Stub resolution uses exact filename matching (simple, predictable)

## Context

- Brainstorm: `.lore/brainstorm/bounded-specification-2026-01-29.md`
- Current skill: `lore-development/skills/specify/SKILL.md`
