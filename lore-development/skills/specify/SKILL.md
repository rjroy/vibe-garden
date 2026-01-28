---
name: specify
description: Use when the user wants to define requirements, capture what needs to be built, or document success criteria. Invoked via /lore-development:specify.
---

# Specify

Define what to build and how to know it's done.

## When to Use

- Capturing requirements for a feature or change
- Defining success criteria
- Documenting constraints or boundaries

## Process

1. Review any relevant `.lore/research/` or `.lore/brainstorm/` context
2. Ask clarifying questions about scope and success
3. Draft the specification
4. Confirm with user before saving
5. Save to `.lore/specs/`

## Output

Save to `.lore/specs/[feature-name].md`

### Document Structure

```markdown
# Spec: [Feature Name]

## Overview
One paragraph describing what this is.

## Requirements
- REQ-1: [requirement]
- REQ-2: [requirement]

## Success Criteria
How we know this is done:
- [ ] Criterion 1
- [ ] Criterion 2

## Constraints
Any boundaries or limitations.

## Context
Links to related `.lore/` documents if relevant.
```

## Keep It Light

Don't over-specify. Capture the essence. Trust that implementation will fill gaps appropriately.
