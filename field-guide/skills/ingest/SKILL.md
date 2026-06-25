---
name: ingest
description: Use when extracting knowledge from .lore/ artifacts into the reference wiki. Converts work artifacts (retros, specs, plans, research, notes) into structured wiki pages grouped by knowledge type. Reads Markdown or HTML sources and writes Markdown by default. Triggers include "ingest this", "extract knowledge from", "add this to the wiki", "update the reference from", and "populate the field guide".
---

# Ingest

Read source artifacts, extract what they know, and write it into `.lore/reference/` as searchable wiki pages.

## Sources

Accept one or more paths from the user. Each may be a file or a directory. For directories, walk them and read every `.md` and `.html` file found. If a directory walk finds zero supported files, report this clearly to the user ("No .md or .html files found in [path] — nothing ingested") and move on to the next source path. Sources should live under `.lore/` — warn and skip anything that doesn't.

Treat Markdown and HTML sources as equivalent knowledge inputs:

- Markdown files use YAML frontmatter when present, followed by Markdown body content.
- HTML files use `<meta name="...">` fields when present, `<title>` as the title, and visible document body content as the source text. Ignore scripts, styles, and generated chrome that does not carry project knowledge.

## Extraction

Read each source file in full. Use judgment to identify distinct knowledge units within it. A knowledge unit is a claim that stands on its own and would be useful without the source document's context. One source typically yields one to several units; a retro might yield three, a plan might yield one, a research document might yield ten.

Assign each unit an `fg-type`:

- `decision` — a resolved choice and its rationale ("we chose X over Y because Z")
- `lesson` — a generalized rule derived from experience, usually surfaced in retros or learned entries
- `architecture` — how a system, component, or data flow is structured
- `concept` — a recurring term, pattern, or abstraction used across the project
- `entity` — a named person, system, component, or external dependency

Do not assign `synthesis` — that type is reserved for query output.

When a unit is borderline between types, pick the type that best describes how someone would search for it. A lesson about an architectural decision is a `lesson`. A description of an architectural decision that is still the current approach is an `architecture`.

## Writing pages

For each extracted knowledge unit, write or update a page in `.lore/reference/`. New pages should be Markdown files with kebab-case names and `.md` extensions. No subdirectories beyond `.lore/reference/` unless they already exist.

Compatibility rule: before creating a new page, check for an existing page for the same knowledge unit in either `.md` or `.html` form. Prefer updating an existing Markdown page. If only an HTML page exists for that unit, update that HTML page in place unless the user has asked to migrate it to Markdown. Do not create duplicate `.md` and `.html` pages for the same unit.

New Markdown pages use YAML frontmatter:

```markdown
---
title: Precise noun-first description of the knowledge unit
date: YYYY-MM-DD
status: current
tags: [kebab-case, terms, subject, domain, problem-type]
fg-type: decision|lesson|architecture|concept|entity
fg-sources: [relative/path/to/source.md]
fg-status: current
---

# Precise noun-first description of the knowledge unit

<!-- body in Markdown -->
```

`fg-sources` is a YAML list of relative paths. Include all source files that contributed to this page; paths may end in `.md` or `.html`.

The body must be self-contained. Write it in Markdown. Reach for embedded inline HTML only when a visual carries meaning Markdown cannot — a color-coded status badge, an inline `<svg>` diagram, a side-by-side comparison. When you do, write it raw and inline; never in a fenced code block.

## Re-ingest (same source)

If a source path was previously ingested, some pages already exist. Before writing, read existing `.md` and `.html` pages whose source metadata includes the current source path. For Markdown, read the `fg-sources` frontmatter list. For HTML, read the `fg-sources` meta tag as a comma-separated or YAML-like list. Compare content against what the source now says.

Three outcomes per existing page:

- **No change**: source still supports the page content. Leave the page alone.
- **Stale content**: source has changed or superseded the claim. Update the page body and reset `date` to today.
- **Contradiction**: source now asserts something that directly conflicts with the page. Note it during processing but do not surface it immediately and do not overwrite the page. Leave the page unchanged. At the end of the run, report all contradictions together, each with the page path, the existing claim, and what the source now says. Let the user decide.

Reconciliation is content comparison only. No activity log, no change history in the page.

## Index update

After all pages are written, update the field-guide index. Prefer `.lore/reference/index.md`. If only `.lore/reference/index.html` exists, update it in place unless the user asked to migrate the index to Markdown. If neither exists, create `.lore/reference/index.md`.

The index groups pages by `fg-type`. Within each group, each entry links to the page using the page's `title` as both the link text and a one-line description. Markdown indexes use Markdown links. HTML indexes use normal anchor links.

Add new pages to their group. Update link text and descriptions for modified pages. Do not remove entries for pages that weren't touched in this run. Preserve existing entries and groups that aren't affected.

If the index exists but has no group structure yet, build it from scratch using all supported pages currently in `.lore/reference/`, including both `.md` and `.html` pages.

Example index structure:

```markdown
---
title: Field Guide Index
date: YYYY-MM-DD
status: current
tags: [index, field-guide]
---

# Field Guide Index

## decision

- [Auth token storage decision](auth-token-storage-decision.md) — we chose httpOnly cookies over localStorage because of XSS exposure

## lesson

- [Database migration lesson](db-migration-lesson.md) — always run migrations against a prod-schema clone before applying to prod
```

## Summary

After all writes complete, tell the user:

- How many sources were processed
- How many pages were created, updated, or unchanged
- Any contradictions that need resolution, with enough context to act on each one
