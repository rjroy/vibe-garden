---
title: vision Skill
date: 2026-03-16
status: implemented
tags: [skill, vision, decision-filter, interactive, bootstrapping]
modules: [lore-development]
related:
  - .lore/work/specs/lore-development/vision-document.md
  - .lore/work/research/lore-development/vision-statements-as-ai-decision-filters.md
req-prefix: VSKILL
---

# Spec: vision Skill

## Overview

A skill that helps a user define their project's vision and writes it to `.lore/reference/vision.md`. The vision document serves as a decision filter: other lore-development skills can reference it when evaluating proposals, scoping features, or resolving priority conflicts.

Two creation paths exist. For projects with existing code, the skill reads the codebase and lore artifacts to draft a vision from what the project's decisions already reveal, then refines it with the user. For projects without code (or where the code doesn't tell enough of the story), the skill walks the user through structured questions. Both paths produce the same artifact: a `.lore/reference/vision.md` in the format defined by the [vision document spec](vision-document.md).

The skill is interactive. It synthesizes a draft and presents it for refinement, not approval-and-done. The user shapes the vision through conversation, not by filling in a template.

## Entry Points

- Explicit: User invokes `/lore-development:vision` or `/vision`
- Implicit: User asks to "define the project vision", "what should this project become", "create a vision document"
- Continuation: User invokes the skill when `.lore/reference/vision.md` already exists (draft or approved)

## Requirements

### Path Selection

- REQ-VSKILL-1: On invocation, the skill checks for an existing `.lore/reference/vision.md`. If one exists with `status: approved`, the skill asks whether the user wants to revise it or just review it. If one exists with `status: draft`, the skill loads it and continues refinement. If none exists, the skill proceeds to creation.

- REQ-VSKILL-2: For creation, the skill determines the creation path. If the project has a meaningful codebase, the skill uses the bootstrap path. If the project is empty or too thin for bootstrap, the skill uses the guided path. The skill states which path it chose and why, and the user can override.

  A codebase is "meaningful" for bootstrap purposes when it has enough signal to draft at least two of the four vision sections from evidence. Indicators: multiple source files, git history with deliberate commits, existing lore artifacts, or a CLAUDE.md with project-specific guidance. A project with only boilerplate, config files, or a skeleton README should default to guided. When the signal is ambiguous, the skill should say what it found and let the user pick.

### Bootstrap Path (Existing Code)

- REQ-VSKILL-3: The skill reads broadly before drafting. Sources include: project source code (structure, patterns, naming), `.lore/` artifacts (specs, retros, brainstorms, issues, research), CLAUDE.md files, and README or similar documentation. The skill looks for implicit values: what gets built, what gets rejected, what wins when priorities conflict.

- REQ-VSKILL-4: The skill drafts a vision document based on observable evidence. Where evidence is ambiguous or contradictory, the draft says so rather than inventing coherence. A sparse but honest draft is more useful than a complete but fabricated one.

- REQ-VSKILL-5: After drafting, the skill presents the draft to the user section by section, asking for corrections, additions, and reordering. The skill does not present the draft as a finished product. It frames each section as "here's what I see in the code; tell me what's right, what's wrong, and what's missing." If the bootstrap draft is too sparse to be useful (fewer than two sections have substantive content), the skill should offer to switch to guided questions rather than walking through an empty scaffold.

### Guided Path (New Projects)

- REQ-VSKILL-6: The skill walks the user through structured questions covering these areas (adapt based on responses, ask follow-ups):

  1. **Identity:** What is this project? Who does it serve? What problem does it solve that isn't solved elsewhere?
  2. **Values:** What matters most? If you had to pick three things this project should always be, what are they? What order do they go in when they conflict?
  3. **Rejections:** What should this project never become? What reasonable-sounding ideas would you reject on principle?
  4. **Tensions:** Where do your values pull in opposite directions? When one value conflicts with another, which wins by default?
  5. **Constraints:** What's true now that won't be true forever? What limitations shape current decisions but shouldn't become permanent identity?

- REQ-VSKILL-7: The skill synthesizes user responses into a draft vision, then presents it for refinement in the same conversation. The user should see their own words reflected back, shaped into the document format, not replaced by the skill's vocabulary.

### Document Format

- REQ-VSKILL-8: The output document follows the format defined in the [vision document spec](vision-document.md), specifically REQ-VIS-1 through REQ-VIS-6. The document lives at `.lore/reference/vision.md` and contains four required sections: Vision (prose), Principles (ordered, behavioral, with examples), Anti-Goals (with rationale), and Tension Resolution (table). An optional Current Constraints section may be included.

- REQ-VSKILL-9: The frontmatter uses the lore-development frontmatter schema, not the Guild Hall-specific schema from the vision document spec. The minimum fields are:

  ```yaml
  ---
  title: "<Project Name> Vision"
  date: YYYY-MM-DD
  status: draft
  tags: [vision]
  ---
  ```

  The `status` field uses `draft` and `approved`. A vision becomes `approved` when the user edits the frontmatter directly or tells the skill to mark it approved. The skill does not approve the vision on the user's behalf.

  The vision document spec (REQ-VIS-2) defines additional frontmatter fields for the Guild Hall lifecycle: `version`, `last_reviewed`, `approved_by`, `approved_date`, `review_trigger`, and `changelog`. This skill omits those fields because they serve Guild Hall's multi-agent consumption patterns, not the general-purpose creation workflow. If a project also uses Guild Hall, those fields can be added to the document after creation without conflicting with the base schema here.

### Refinement

- REQ-VSKILL-10: The skill treats refinement as the core of the interaction, not a cleanup step. The first draft is a conversation starter. The skill should probe: "Does this principle actually describe how you make decisions, or is it aspirational?" "Are these anti-goals things you'd genuinely reject, or things you just haven't prioritized yet?"

- REQ-VSKILL-11: Principles must be written as behavioral guidelines, not trait aspirations. If the user says "it should be simple," the skill helps reframe: "What does simplicity mean in practice for this project? What would you reject as too complex?" The output is something like "Every new feature must justify itself against the cost it adds to the mental model" rather than "The system should be simple."

- REQ-VSKILL-13: After refining each section, the skill checks whether the user wants to continue refining or save. When the full document has been reviewed at least once, the skill offers to write it. The user can always ask to keep refining or defer. If the user defers, the skill summarizes what was discussed so the conversation can be resumed later.

### Revision

- REQ-VSKILL-14: When the user revises an existing approved vision (per REQ-VSKILL-1), the skill loads the current document and enters the refinement loop (REQ-VSKILL-10), not the creation paths. The revision updates `status` to `draft` and the `date` field. The user approves the revision the same way as an initial vision: by telling the skill to mark it approved or editing the frontmatter directly.

### Downstream Integration

- REQ-VSKILL-12: Once `.lore/reference/vision.md` exists, other lore-development skills may reference it as context. The vision is available, not mandatory. Skills like `/specify`, `/brainstorm`, and `/prep-plan` can check for a vision and use it to inform scope decisions and priority calls, but they function normally without one.

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Vision saved | User is satisfied with the draft | `.lore/reference/vision.md` written |
| Deferred | User wants to think more before committing | No file written; skill summarizes what was discussed |
| Revision saved | User revises an existing vision | `.lore/reference/vision.md` updated, status returns to `draft` |

## Success Criteria

- [ ] Skill produces a `.lore/reference/vision.md` that follows the document format
- [ ] Bootstrap path cites specific observable patterns from the codebase (not generic language like "this project values quality")
- [ ] Guided path covers all five question areas in the output, regardless of conversation structure
- [ ] Principles are behavioral, not aspirational (each describes what to do, not what to be)
- [ ] User confirms the output during refinement rather than discarding the draft entirely

## AI Validation

**Custom** (this is a skill definition, not application code):
- Manual test: invoke on a project with existing code, verify bootstrap draft reflects the codebase
- Manual test: invoke on an empty project, verify guided questions cover all five areas
- Manual test: verify refinement loop catches trait-framing and helps convert to behavioral
- Review: skill content matches spec requirements
- Skill reviewer: run `/plugin-dev:skill-reviewer` on the skill after implementation

## Constraints

- Does not modify source code. Reads code to inform the vision; does not change it.
- Produces exactly one artifact: `.lore/reference/vision.md`. No intermediate files.
- Does not require Guild Hall. Works in any project that uses lore-development.

## Context

- Format defined by: [Spec: Vision Document](vision-document.md), REQ-VIS-1 through REQ-VIS-6
- Research basis: [Vision Statements as AI Decision Filters](../../research/lore-development/vision-statements-as-ai-decision-filters.md)
- Skill conventions: follows patterns from `/specify`, `/brainstorm`, `/excavate`

## Design Notes

The vision document spec (vision-document.md) defines this format in the context of Guild Hall's multi-agent system, with commissions, meetings, and brainstorming workers as the creation and consumption mechanisms. This skill extracts the document format and creates a simpler, general-purpose creation workflow that works in any project using lore-development.

The spec intentionally omits the Guild Hall-specific lifecycle (approval via frontmatter edit, brainstorming worker consumption, scheduled review triggers). Those belong to the Guild Hall implementation. If a project uses Guild Hall, the vision document this skill produces is compatible with the Guild Hall lifecycle. If not, the document still works as a decision filter that humans and AI can reference.

The skill is lighter on prescriptive process than most lore-development skills. Vision creation is inherently personal. The skill provides structure (the five question areas, the four-section format) without scripting the conversation. The AI should adapt its questions based on what the user says, not march through a checklist.
