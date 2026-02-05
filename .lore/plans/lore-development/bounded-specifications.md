---
title: Bounded Specification Model
date: 2026-01-29
status: executed
tags: [specification, layers, stubs, update-stubs]
modules: [lore-development]
related: [.lore/specs/lore-development/bounded-specification.md, .lore/brainstorm/lore-development/bounded-specification.md]
---

# Plan: Bounded Specification Model

**Spec**: `.lore/specs/lore-development/bounded-specification.md`

## Overview

Implement the bounded specification model for `/specify` and create `/update-stubs` skill. This enables layer-based specification where each spec defines one functional layer with explicit connections to undefined areas (stubs).

## Changes

### 1. Update `/specify` Skill

**File**: `lore-development/skills/specify/SKILL.md`

**Template additions** (between Requirements and Success Criteria):

```markdown
## Entry Points
How users arrive at this feature:
- [Entry description] (from [source])

## Exit Points
| Exit | Triggers When | Target |
|------|---------------|--------|
| [Exit name] | [User action or condition] | [STUB: target-name] or [Spec: existing-spec] |
```

**Process additions**:
- After drafting requirements, add step to probe for stubs: "For each major action identified, ask: 'Are we stubbing [action], or defining it now?'"
- User can choose to define inline or mark as stub
- Document stub format in skill: `[STUB: stub-name]` where stub-name uses kebab-case matching spec filename conventions

**Preserve existing**:
- Overview, Requirements, Success Criteria, Constraints, Context sections
- Fresh-eyes review hand-off to `lore-docs-reviewer`
- Research phase, clarification, user confirmation workflow

### 2. Create `/update-stubs` Skill

**File**: `lore-development/skills/update-stubs/SKILL.md`

**Structure** (following existing skill pattern):
```yaml
---
name: update-stubs
description: Scans specs for stubs and generates outstanding stub index. Use when reviewing spec coverage, before starting new specification work, or after completing a specification. Triggers include "update stubs", "check stubs", "stub index", "outstanding stubs".
artifact_path: .lore/stubs
---
```

**Process**:
1. Scan all `.md` files in `.lore/specs/` recursively
2. Extract `[STUB: name]` patterns using regex
3. For each stub, check if `.lore/specs/[stub-name].md` exists (exact match, case-sensitive)
4. Validate stub names are valid kebab-case filenames
5. Flag self-referential stubs (spec references itself) as warnings
6. Generate/update `.lore/stubs/index.md`

**Output format** for `.lore/stubs/index.md`:
```markdown
# Outstanding Stubs

Last updated: [timestamp]

## Unresolved Stubs

| Stub | Referenced From | Notes |
|------|-----------------|-------|
| [STUB: auth-flow] | `.lore/specs/login.md` | |
| [STUB: payment-processing] | `.lore/specs/checkout.md`, `.lore/specs/subscription.md` | |

## Warnings

- Self-referential stub in `checkout.md`: [STUB: checkout]
- Invalid stub name in `login.md`: [STUB: Auth Flow] (contains spaces)
```

**Key behaviors**:
- Resolved stubs simply absent from index (not listed as "resolved")
- Duplicate stubs across specs: list all source specs
- Self-referential stubs: report as warning, include in index
- Invalid names: report as error, include in warnings section

## File Changes Summary

| File | Action |
|------|--------|
| `lore-development/skills/specify/SKILL.md` | Edit - add Entry/Exit Points, stub probing |
| `lore-development/skills/update-stubs/SKILL.md` | Create - new skill |

## Verification

1. Run `/specify` on a test feature, verify:
   - Template includes Entry Points and Exit Points sections
   - Process prompts for stub decisions on major actions
   - Stubs use correct `[STUB: kebab-case]` format

2. Create test specs with stubs, run `/update-stubs`, verify:
   - Scans `.lore/specs/` recursively
   - Generates `.lore/stubs/index.md`
   - Resolved stubs (matching existing spec files) are absent
   - Duplicate stubs show all sources
   - Self-referential and invalid stubs appear in warnings
