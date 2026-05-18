---
title: HTML as the primary lore artifact format
date: 2026-05-18
status: open
tags: [html, markdown, lore-development, artifacts, format]
modules: [lore-development]
---

# Brainstorm: HTML as the Primary Lore Artifact Format

## Context

Prompted by a post from someone on the Claude Code team arguing that HTML is a better output format than Markdown for AI agent artifacts. The core argument: markdown hits a readability wall at ~100 lines, nobody actually reads long markdown files, and HTML enables richer visualizations, interactivity, and shareability. The question explored here: what would it mean to switch lore-development to use HTML instead of markdown?

## Ideas Explored

- **Who is the primary reader?** Two jobs in tension: Claude needs to ingest artifacts (parse structure, extract facts, follow cross-references); the user needs to validate them (does this reflect what I actually meant?). Markdown serves the first job well. HTML serves the second. Currently the second job gets skipped, which means the first job runs on bad input anyway.

- **HTML is the primary artifact, no companion markdown.** Claude reads HTML directly. Having two docs (HTML + markdown) is just asking for them to get out of sync. Single source of truth.

- **Annotation seam is first-class.** Current behavior: user adds `[USER NOTE: ...]` inline. In HTML this becomes a `<section id="user-notes">` always present at the bottom of every artifact, always findable by Claude on next ingest. Richer than inline text but simple enough to hand-edit.

- **Semantic `id` attributes on sections.** Claude navigates by `<section id="requirements">`, `<section id="open-questions">` etc. rather than free-form parsing. Human sees rich HTML; Claude navigates by semantic IDs.

- **Frontmatter becomes `<meta>` tags.** Common frontmatter fields (`title`, `date`, `status`, `tags`, `modules`, `related`) move to `<meta name="lore-*">` tags in `<head>`. Claude can grep these as reliably as YAML. `frontmatter-schema.md` stays as schema source of truth, updated to describe HTML meta syntax instead of YAML.

- **Templates move into each skill.** Skills own their HTML structure. The shared schema doc defines what fields exist and what values are valid; rendering is owned by the skill.

- **Richness scales by artifact type.** A learned entry is a styled card. A plan might be a full interactive artifact with dependency graphs. A brainstorm gets collapsible sections and highlighted open questions. Degree of HTML richness varies; the principle applies universally.

- **`lore-researcher` updated.** Grep patterns change from YAML frontmatter to `<meta name="lore-*"` targets. Whether this is just updated patterns or a "read lore metadata" abstraction is a design question for later.

- **Workflow unchanged.** AI writes, user opens in browser. Currently VS Code markdown preview; this just changes that to opening an HTML file directly.

- **Version control tradeoff accepted.** HTML diffs are noisier than markdown. That's the cost of the benefit.

## Open Questions

- What does the annotation UX actually look like? Inline divs Claude writes, a sidebar, or a fixed bottom section? (Leaning toward fixed `<section id="user-notes">` bottom.)
- Does `lore-researcher` get a "read lore metadata" abstraction, or just updated grep patterns?
- Do existing markdown artifacts get migrated, or do old and new coexist until `/tend` handles it?

## Next Steps

Move to `/design` to work out the HTML template structure, annotation UX, and `lore-researcher` changes before touching any skill implementations.
