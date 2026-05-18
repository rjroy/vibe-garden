---
title: "Implementation plan: HTML artifact format for lore-development"
date: 2026-05-18
status: draft
tags: [html, markdown, lore-development, artifacts, format, plan]
modules: [lore-development]
related:
  - .lore/work/brainstorm/html-artifacts.md
  - .lore/work/design/html-artifact-annotations.md
---

# Plan: HTML Artifact Format for lore-development

## Goal

Switch lore-development from markdown to HTML as the primary artifact format across all skills. HTML artifacts are richer, more readable, and more shareable. Claude reads HTML directly -- no companion markdown. The common frontmatter schema moves from YAML to `<meta name="lore-*">` tags. A lightweight annotation mechanism (`<div class="user-note">`) allows users to flag notes for Claude to act on and remove.

This plan covers: updating the shared frontmatter schema, updating all skill templates, updating the lore-researcher agent, and defining the shared HTML base template that skills reference.

## Codebase Context

- Skills live in `lore-development/skills/[name]/SKILL.md`
- Each skill references `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for frontmatter definitions
- The `lore-researcher` agent lives in `lore-development/agents/lore-researcher.md` and greps YAML frontmatter fields (`title:`, `tags:`, `modules:`)
- Other agents (`spec-reviewer`, `plan-reviewer`, `design-reviewer`) read lore artifacts -- they will need updated ingest instructions
- No existing HTML templates or shared CSS -- all new

## Implementation Steps

### Step 1: Create shared HTML base template

**Files**: `lore-development/shared/html-base-template.md`

Define the canonical HTML shell that all skills copy as their starting point. "Extending the base" means: copy the full shell verbatim, then fill in the `<main>` content area with artifact-specific sections. No build step, no includes, no inheritance mechanism -- just a literal copy-and-fill pattern.

The base template includes:
- `<head>` with `<meta name="lore-*">` tags for all common frontmatter fields
- **CSS delivered inline** in a `<style>` block in `<head>`. No external stylesheet, no relative path dependency. Every artifact is fully self-contained. CSS covers: clean readable typography, muted color palette, `user-note` div styling (visually distinct, amber/yellow tint), `copy-prompt-btn` button styling (small, muted, recedes visually)
- `<body>` structure with a `<header>` block (title, metadata bar showing status/date/tags) and a `<main>` content area
- The `[Copy as Prompt]` button: a single `<button class="copy-prompt-btn">` in the `<header>` that copies `Add a user note to "[document title]": ` to clipboard. Button is in the header only -- not per-section.
- No `<section id="user-notes">` -- user-note divs are ephemeral and placed inline wherever relevant, not a permanent section

**Canonical section IDs** -- define these cross-skill standard IDs so reviewers and `/tend` can navigate reliably:
- `context` -- background and framing
- `summary` -- key findings or decisions (one-paragraph overview)
- `open-questions` -- unresolved questions (visually highlighted)
- `next-steps` -- optional, where this leads

Type-specific sections use their own IDs (e.g., `requirements`, `approaches`, `decision`, `steps`) defined in each skill's template.

**Annotation re-embed rule** (document here so all skills inherit it by reference): When regenerating an artifact that already exists on disk, Claude must read the existing file, extract all `<div class="user-note">` elements, and re-embed them in the regenerated artifact. User notes must never be lost on regeneration. Notes are removed only after Claude has explicitly acted on their content.

Document the `<meta>` tag convention for all common fields plus type-specific fields (e.g., `lore-req-prefix` for specs, `lore-source` for notes, `lore-sequence` for tasks).

### Step 2: Update frontmatter-schema.md

**Files**: `lore-development/shared/frontmatter-schema.md`

Replace YAML examples with HTML `<meta>` tag equivalents throughout. Preserve all field definitions, status values, and guidelines -- only the syntax changes.

Key changes:
- All `---\nyaml\n---` blocks become `<meta name="lore-[field]" content="...">` examples
- Multi-value fields (`tags`, `modules`, `related`) use comma-separated `content` values
- The "Search Behavior" section updates grep targets from YAML keys to `<meta name="lore-*"`
- Add a note: the schema file itself stays markdown (it is a reference for Claude, not a user-facing artifact)

### Step 3: Update lore-researcher agent

**Files**: `lore-development/agents/lore-researcher.md`

Update grep strategy from YAML frontmatter to HTML meta tags:
- `grep 'name="lore-title"'` instead of `grep 'title:'`
- `grep 'name="lore-tags"'` instead of `grep 'tags:'`
- `grep 'name="lore-modules"'` instead of `grep 'modules:'`

Update file glob patterns: target **both** `.html` and `.md` files. Old markdown artifacts coexist with new HTML artifacts during the transition period. The researcher must find both.

Add ingest instruction: when reading a matched `.html` file, extract metadata from `<meta name="lore-*">` tags and body content from `<main>` element. For `.md` files, use existing YAML frontmatter parsing.

### Step 4: Update reviewer agents

**Files**:
- `lore-development/agents/spec-reviewer.md`
- `lore-development/agents/plan-reviewer.md`
- `lore-development/agents/design-reviewer.md`
- `lore-development/agents/fresh-lore.md`

**Dependency: must run after Steps 5-7.** Reviewer agents navigate sections by `<section id="...">` -- those IDs are defined by the skill templates. Writing reviewers before templates are done means referencing IDs that don't exist yet.

Each reviewer reads lore artifacts. Update their ingest instructions:
- Read metadata from `<meta name="lore-*">` tags
- Navigate document sections by `<section id="...">` using the canonical IDs defined in Step 1 plus type-specific IDs from the relevant skill template
- Check for `<div class="user-note">` elements and include them in the review summary

### Step 5: Update skill templates -- work artifacts

**Files** (one per skill, update the Output / Document Structure section):
- `skills/brainstorm/SKILL.md`
- `skills/specify/SKILL.md`
- `skills/design/SKILL.md`
- `skills/prep-plan/SKILL.md`
- `skills/research/SKILL.md`
- `skills/retro/SKILL.md`
- `skills/file-issue/SKILL.md`
- `skills/ddp/SKILL.md`
- `skills/define-validation/SKILL.md`
- `skills/review-ideas/SKILL.md`

For each skill:
- Change output file extension from `.md` to `.html`. Output is exclusively `.html` -- do not retain or produce a companion `.md` file.
- Replace the markdown template with an HTML template. The base shell is copied verbatim from `html-base-template.md`; the `<main>` content area is filled with artifact-specific `<section id="...">` elements.
- Map existing markdown sections to `<section id="[section-name]">` elements. Use canonical cross-skill IDs from Step 1 where they apply; define type-specific IDs for everything else.
- Update "Before writing" instruction: load `html-base-template.md` and `frontmatter-schema.md`
- Richness guidance: work artifacts (brainstorm, spec, plan) get collapsible sections and highlighted open questions; simpler artifacts (retro, research) get clean structured layout

Spec-specific: requirement IDs (`REQ-XX-N`) render as `<span class="req-id">` for visual callout.

Plan-specific: implementation steps render as a numbered list with dependency indicators.

### Step 6: Update skill templates -- reference and learned artifacts

**Files**:
- `skills/distill/SKILL.md`
- `skills/learn/SKILL.md`
- `skills/vision/SKILL.md`
- `skills/stratify/SKILL.md`

Same rules as Step 5: output is exclusively `.html`, base shell copied from Step 1, sections use canonical IDs.

Learned entries are minimal -- styled card layout, no interactivity. Reference docs get clean structured layout. Vision gets a slightly richer treatment (this is a document people read).

### Step 7: Update skill templates -- utility skills

**Files**:
- `skills/plan-breakdown/SKILL.md` (writes task files)
- `skills/implement/SKILL.md` (writes notes files)
- `skills/back-propagate/SKILL.md`
- `skills/tend/SKILL.md` (reads lore files for hygiene -- update file glob and meta parsing)
- `skills/ask/SKILL.md`
- `skills/update-stubs/SKILL.md`

`/tend` requires the most attention of any utility skill. All four modes touch lore file reading:
- **Status mode**: update to read `<meta name="lore-status">` instead of YAML `status:`
- **Tags mode**: update to read `<meta name="lore-tags">` instead of YAML `tags:`
- **Filenames mode**: update convention check to accept `.html` as valid. During transition, both `.md` and `.html` are valid; flag neither as non-conforming.
- **Directories mode**: no change expected, but verify it doesn't assume `.md` extensions when listing files

Also update `/tend`'s four tend reference files in `skills/tend/references/` if they contain frontmatter examples.

### Step 8: Verify annotation re-embed rule coverage

**Dependency: runs after Steps 5-7.**

The annotation re-embed rule is defined in the base template (Step 1). This step verifies every skill updated in Steps 5-7 references `html-base-template.md` in its "Before writing" instruction, which is the mechanism by which the rule is inherited. No skill should duplicate the rule inline -- if found, remove the duplication and confirm the base template reference is present.

### Step 9: Validate

Launch a sub-agent that reads the Goal section above plus the brainstorm and design artifacts, reviews the updated skills and shared files, and flags:
- Any skill that still references `.md` output or YAML frontmatter
- Any agent that still greps YAML fields
- Any skill missing the annotation re-embed rule
- Any template missing the `[Copy as Prompt]` button

## Delegation Guide

- **Steps 1-2**: Sequential, no parallelism. Step 1 is a dependency for everything else.
- **Step 3**: After Steps 1-2. Grep pattern precision matters -- after updating, run a controlled test: create one `.html` artifact with known meta tags and verify lore-researcher finds it.
- **Steps 5-7**: Parallel after Steps 1-2. Each skill is independent. Good target for sub-agent swarming (5-8 skills per agent).
- **Step 4**: After Steps 5-7. Reviewers need the section IDs that skills define.
- **Step 8**: After Steps 5-7. Verification pass, not authoring.
- **Step 9**: Final validation. Use `plan-reviewer` agent.

## Open Questions

- Migration: existing `.md` artifacts in `.lore/` are not converted by this plan. Old and new coexist until `/tend migrate` handles it (future work).
- Skill files themselves (SKILL.md) stay markdown -- they are instructions for Claude, not user-facing artifacts. This is intentional.
