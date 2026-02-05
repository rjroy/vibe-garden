---
title: Docs Review Capability
date: 2026-01-29
status: executed
tags: [fresh-context, review, documentation, agents]
modules: [lore-development]
related: [.lore/brainstorm/docs-review-capability.md]
---

# Plan: Docs Review Capability

## Context

- **Brainstorm**: `.lore/brainstorm/docs-review-capability.md`
- **Existing agent pattern**: `lore-development/agents/surface-surveyor.md`
- **Registry skill**: `lore-development/skills/update-lore-agents/SKILL.md`
- **Consumer skills**: `specify` and `plan` (both have "Specialized Agents" sections)

## Approach

Create a `lore-docs-reviewer` agent that provides fresh-context review of specs and plans. The agent's value is that it reads documentation without the accumulated assumptions of the main conversation thread.

Key decisions:
- **Agent, not skill**: Sub-agents inherently provide fresh context
- **Prose feedback, not checklists**: Goal is "make this clearer" not "pass/fail"
- **Four review lenses**: Clarity, completeness, consistency, actionability
- **Minimal changes**: Only add agent + update registry guidance

## Steps

### 1. Create `lore-docs-reviewer` agent

File: `lore-development/agents/lore-docs-reviewer.md`

Structure:
- Frontmatter (description, tools: Read/Glob/Grep, model: sonnet)
- Role section: fresh-context reviewer for specs and plans
- Invocation context: from skills or direct user request
- Review strategy: four lenses with specific questions each
- Output format: structured prose organized by lens
- Behavior guidelines: focus on reader experience, not authorial intent

### 2. Update `update-lore-agents` skill

File: `lore-development/skills/update-lore-agents/SKILL.md`

Changes:
- Add "Documentation Review" to category list in Step 1
- Add consistent registry entry guidance for `lore-docs-reviewer`
- Include recommended purpose/usage text to ensure cross-project consistency

### 3. Verify integration

No code changes needed. Confirm that:
- `specify` skill's "Specialized Agents" section will find and suggest the reviewer
- `plan` skill's "Specialized Agents" section will find and suggest the reviewer
- Users can invoke directly: "use the lore-docs-reviewer agent"

## Considerations

### Why prose over checklists

Spiral-grove validators use pass/fail because they enforce process compliance. Documentation review is different: the goal is "can a fresh reader understand this?" That's inherently qualitative. Prose feedback organized by concern type (clarity, completeness, etc.) is more actionable for improving documentation.

### Agent description wording

The description must communicate:
1. Fresh context is the value (reads without conversation history)
2. Targets specs and plans (not all `.lore/` artifacts)
3. Available for direct invocation or skill suggestion

Proposed description: "Reviews specs and plans with fresh context to identify clarity issues, gaps, and ambiguities that the author may have missed. Invoke after completing a spec or plan, or when documentation feels unclear."

### No skill needed

Skills that produce reviewable artifacts (`specify`, `plan`) already have generic "Specialized Agents" integration. Adding a skill wrapper would be redundant orchestration. Users who want explicit review can invoke the agent directly.

## Artifacts

| Step | File | Action |
|------|------|--------|
| 1 | `lore-development/agents/lore-docs-reviewer.md` | Create |
| 2 | `lore-development/skills/update-lore-agents/SKILL.md` | Edit |
