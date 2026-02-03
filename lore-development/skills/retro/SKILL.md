---
name: retro
description: This skill reviews completed work and records lessons learned. Use after completing a feature, when capturing insights before they fade, for periodic reflection on progress, or to graduate lessons to higher scopes. Triggers include "let's do a retro", "what did we learn", "review what happened", "capture lessons from", "graduate lessons".
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
5. Graduate lessons (see Lessons Graduation below)

## Output

Save to `.lore/retros/[feature-name].md`

### Document Structure

**Before writing**: Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` to get frontmatter field definitions and status values for retros.

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

## Lessons Graduation

After saving the retro, graduate lessons to higher scopes.

### Detection

If `/retro` is invoked on an existing retro document (path to `.lore/retros/*.md`), skip the normal retro flow and run graduation only.

### Flow

1. Extract lessons from the "Lessons Learned" section
2. If no lessons, skip graduation
3. For each lesson, use AskUserQuestion:
   - Prompt: `Review lesson: "[lesson text]"`
   - Options:
     - **Invalid** - Remove from retro
     - **Valid (Recommended)** - Keep in retro only
     - **Critical** - Add to project CLAUDE.md
     - **Universal** - Add to ~/.claude/rules/lessons-learned.md
4. Process classifications:
   - Invalid: Remove lesson from retro document
   - Valid: No action (already in retro)
   - Critical: Append to project CLAUDE.md under "## Critical Lessons"
   - Universal: Append to `~/.claude/rules/lessons-learned.md` under inferred category

### File Operations

**For Critical lessons** (project CLAUDE.md):
- If "## Critical Lessons" section doesn't exist, create it at file bottom
- Append lesson as bullet: `- [lesson text]`
- Don't duplicate existing lessons

**For Universal lessons** (`~/.claude/rules/lessons-learned.md`):
- Create file if missing with header: `# Lessons Learned\n\nHard-won lessons that apply across all projects.`
- Infer category from retro tags (see Category Inference)
- Create category section if missing
- Append lesson as bullet under category
- Don't duplicate existing lessons

### Category Inference

Infer category from retro tags, not exact match:

| Tags like | Category |
|-----------|----------|
| plugin, extension | Plugin Development |
| git, commit, branch | Git Workflow |
| test, testing, coverage | Testing |
| process, methodology, workflow | Process |
| performance, optimization | Performance |
| (no clear match) | General |

**Category hygiene**:
- Review existing categories before creating new ones
- Don't let any category sprawl (10+ items suggests splitting)
- Err on fitting into existing categories over creating new ones

## Purpose

This builds organizational memory. Future work benefits from past experience - but only if it's written down.

## Specialized Agents

If `.lore/lore-agents.md` exists, consult it for specialized agents that can help identify patterns. Reviewers can spot recurring issues or opportunities worth capturing. Invoke relevant agents via Task tool and incorporate their insights.
