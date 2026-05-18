---
title: "Implementation notes: HTML artifact format for lore-development"
date: 2026-05-18
status: complete
tags: [implementation, notes, html, markdown, lore-development, artifacts]
source: .lore/work/plans/html-artifact-format.md
modules: [lore-development]
---

# Implementation Notes: HTML Artifact Format

9 phases. All complete. No divergences from the plan.

## Progress
- [x] Phase 1: Create shared HTML base template
- [x] Phase 2: Update frontmatter-schema.md
- [x] Phase 3: Update lore-researcher agent
- [x] Phase 4: Update reviewer agents (spec-reviewer, plan-reviewer, design-reviewer, fresh-lore)
- [x] Phase 5: Update skill templates -- work artifacts (10 skills)
- [x] Phase 6: Update skill templates -- reference and learned artifacts (4 skills)
- [x] Phase 7: Update skill templates -- utility skills (6 skills + validate_frontmatter.py)
- [x] Phase 8: Verify annotation re-embed rule coverage
- [x] Phase 9: Validate

## Log

### Phase 1: Create shared HTML base template
- Created `lore-development/shared/html-base-template.md` with full HTML shell, inline CSS, copy-as-prompt button, canonical section IDs, and the annotation re-embed rule as a prominent comment.

### Phase 2: Update frontmatter-schema.md
- Replaced all YAML `---` block examples with `<meta name="lore-*" content="...">` equivalents throughout. Updated Search Behavior grep targets. Added note that the schema file itself stays markdown.

### Phase 3: Update lore-researcher agent
- Updated grep patterns from `title:` / `tags:` / `modules:` to `name="lore-title"` / `name="lore-tags"` / `name="lore-modules"`.
- Added `.html` to file glob patterns alongside `.md`.
- Added ingest instruction: for `.html` files, extract from `<meta name="lore-*">` tags and `<main>` element.

### Phase 4: Update reviewer agents
- Added "Artifact Ingest" section to spec-reviewer, plan-reviewer, design-reviewer, and fresh-lore agents.
- Each section covers: reading `<meta name="lore-*">` for metadata, navigating by `<section id="...">`, checking for `<div class="user-note">` elements.

### Phase 5: Update work artifact skill templates (10 skills)
- Dispatched to a worktree agent (ran in parallel with Phase 6). All 10 skills updated: brainstorm, specify, design, prep-plan, research, retro, file-issue, ddp, define-validation, review-ideas.
- Output extension changed to `.html`. "Before writing" updated to load both base template and schema. Markdown templates replaced with HTML `<section id="...">` structure.

### Phase 6: Update reference/learned skill templates (4 skills)
- Dispatched to a worktree agent in parallel with Phase 5. All 4 skills updated: distill, learn, vision, stratify.
- Same pattern as Phase 5. Richness scaled: learned entries get card layout, vision gets richer treatment.

### Phase 7: Update utility skill templates + validate_frontmatter.py
- `plan-breakdown`: task files now `.html`, template updated to HTML, storage path updated.
- `implement`: input table accepts `.html` or `.md`, notes file is `.html`, template updated to HTML, task file status read from `lore-status` meta tag, `lore-source` meta tag replaces YAML `source:` field.
- `update-stubs`: scans both `.html` and `.md` specs, index written to `.html`.
- `tend/references/filenames.md`: accepts `.html` as valid extension during transition.
- `tend/references/status.md`: frontmatter validation section updated to mention HTML handling; retrofitting section covers both formats.
- `validate_frontmatter.py`: added `_parse_html_meta()` HTML parser using stdlib `html.parser`, updated `scan_directory()` to include `.html` files, updated `validate_file()` to route by extension. 11 new tests added; all 74 tests pass.
- `back-propagate`, `ask`: no changes needed (read/modify existing artifacts, don't create new ones).

### Phase 8: Verify annotation re-embed rule coverage
- All 20 skills that produce new artifacts reference `html-base-template.md` (which contains the rule).
- 3 skills that don't (back-propagate, tend, ask) correctly don't need it -- they read or modify, not create.
- No inline duplication of the rule found anywhere.

### Phase 9: Validate
- No skills still output `.md` (within plan scope).
- No agents still grep YAML frontmatter fields.
- lore-researcher confirmed updated.
- All 74 tests pass.

## Divergence

None.
