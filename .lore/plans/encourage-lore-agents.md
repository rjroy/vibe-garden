---
title: Encourage lore agents in implement and update-lore-agents
date: 2026-02-06
status: executed
tags: [agents, implement, update-lore-agents, fallback, registry]
modules: [lore-development]
related:
  - .lore/specs/lore-development/implementation-skill.md
---

# Plan: Encourage Lore Agents

## Goal

The `/implement` skill references three agent roles (implementation, testing, review) but provides no concrete fallback when `.lore/lore-agents.md` is missing or doesn't map to those roles. The `/update-lore-agents` skill doesn't know about `/implement`'s needs, so the registry it generates has no "Implementation" category and no role mapping guidance.

Fix both so `/implement` always dispatches to agents (not nothing), and the registry has slots for the roles `/implement` needs.

## Codebase Context

- `/implement` SKILL.md lines 90-96: Agent selection section. Says "use reasonable defaults" but doesn't name them.
- `/update-lore-agents` SKILL.md lines 144-149: Consumer list omits `/implement`. Template categories (lines 36-44) have Testing and Code Quality but no Implementation.
- Spec constraint (REQ-IMPL-5, line 147): "Agent selection is not hardcoded." Fallbacks should be defaults, not mandates.
- Retro lesson: Keep skill specs light. Don't over-constrain.

## Implementation Steps

### Step 1: Add explicit fallback defaults to `/implement` SKILL.md

**Files**: `lore-development/skills/implement/SKILL.md`
**Delegation**: inline

Replace lines 90-96 (the "Select agents" block) with concrete fallback `subagent_type` values:

- **Implementation**: registry lookup first, fallback `general-purpose`
- **Testing**: registry lookup first, fallback `general-purpose` (with instruction to run tests)
- **Review**: registry lookup first, fallback `pr-review-toolkit:code-reviewer` if available, else `general-purpose`

Keep the existing structure (consult registry, then fall back). Add a small table or list that names the fallback types. Don't prescribe behavior beyond "use this type if registry is silent."

### Step 2: Add Implementation category and `/implement` consumer reference to `/update-lore-agents` SKILL.md

**Files**: `lore-development/skills/update-lore-agents/SKILL.md`
**Delegation**: inline

Three edits:

a. **Consumer list** (line 144-149): Add `/implement` with note about its three roles:
   ```
   - `implement` - implementation, testing, and review agents for phase execution
   ```

b. **Category list** (lines 36-44): Add "Implementation" category for code-writing agents:
   ```
   - **Implementation**: Code writing, phase execution, general-purpose task completion
   ```

c. **Template** (lines 85-138): Add an "Implementation" section to the registry template. Include a note (guidance for humans, not enforcement) showing how `/implement` maps its roles to registry categories:
   - Implementation role → Implementation category
   - Testing role → Testing category
   - Review role → Code Quality category

### Step 3: Validate against spec and retro lessons

**Delegation**: fresh-context sub-agent (required)

Launch a sub-agent that reads the spec at `.lore/specs/lore-development/implementation-skill.md`, the two modified SKILL.md files, and the retro at `.lore/retros/lore-development/implementation-skill.md`. Verify:
- Fallback defaults don't violate "agent selection is not hardcoded" (REQ-IMPL-5)
- Changes don't over-constrain the skill (retro lesson)
- `/implement` can always dispatch to an agent (the original problem)

## Delegation Guide

Steps safe to run inline:
- Step 1: Small edit, clear target
- Step 2: Small edit, clear target

Steps needing fresh context:
- Step 3: Validation against spec constraints benefits from fresh eyes

## Open Questions

None. Scope is clear and small.
