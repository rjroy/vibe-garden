---
name: specify
description: This skill defines requirements and success criteria for features. Use when capturing requirements, defining what "done" looks like, or documenting constraints. Triggers include "write a spec for", "define the requirements", "what should this do", "capture the requirements".
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

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help with domain-specific concerns. Security, compliance, or architecture experts can identify requirements you might miss. Invoke relevant agents via Task tool and incorporate their insights.
