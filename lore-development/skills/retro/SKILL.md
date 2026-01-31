---
name: retro
description: This skill reviews completed work and records lessons learned. Use after completing a feature, when capturing insights before they fade, or for periodic reflection on progress. Triggers include "let's do a retro", "what did we learn", "review what happened", "capture lessons from".
---

# Retro

Review artifacts and record lessons learned.

## When to Use

- After completing a feature or significant chunk of work
- When wanting to capture insights before they fade
- Periodic reflection on project progress

## Process

1. Review relevant `.lore/` artifacts:
   - Original spec in `.lore/specs/`
   - Plan in `.lore/plans/`
2. Reflect on what happened vs. what was expected
3. Capture lessons learned
4. Save to `.lore/retros/`

## Output

Save to `.lore/retros/[feature-name].md`

### Document Structure

**Before writing**: Load `../../shared/frontmatter-schema.md` to get frontmatter field definitions and status values for retros.

```markdown
---
[frontmatter per schema]
---

# Retro: [Feature Name]

## Summary
Brief description of what was built.

## What Went Well
- Thing 1
- Thing 2

## What Could Improve
- Thing 1
- Thing 2

## Lessons Learned
Insights to carry forward:
- Lesson 1
- Lesson 2

## Artifacts
Links to related `.lore/` documents.
```

### Frontmatter Tips for Retros

- **title**: Focus on the key lesson, not just the feature name (e.g., "N+1 query fix in brief generation" not just "Brief generation retro")
- **tags**: Include problem types (bug, performance, refactor), technologies, and patterns
- **modules**: Include codebase areas touched; omit if purely process/methodology focused

## Purpose

This builds organizational memory. Future work benefits from past experience - but only if it's written down.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help identify patterns. Reviewers can spot recurring issues or opportunities worth capturing. Invoke relevant agents via Task tool and incorporate their insights.
