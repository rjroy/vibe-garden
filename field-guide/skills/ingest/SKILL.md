---
name: ingest
description: Use when extracting knowledge from .lore/ artifacts into the reference wiki. Converts work artifacts (retros, specs, plans, research, notes) into structured Markdown wiki pages grouped by knowledge type. Triggers include "ingest this", "extract knowledge from", "add this to the wiki", "update the reference from", and "populate the field guide".
---

# Ingest

Read source artifacts, extract what they know, and write it into `.lore/reference/` as searchable wiki pages.

## Sources

Accept one or more paths from the user. Each may be a file or a directory. For directories, walk them and read every `.md` file found. If a directory walk finds zero `.md` files, report this clearly to the user ("No .md files found in [path] — nothing ingested") and move on to the next source path. Sources should live under `.lore/` — warn and skip anything that doesn't.

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

For each extracted knowledge unit, write or update a Markdown page in `.lore/reference/`. Filename should be kebab-case, descriptive of the unit's content, with `.md` extension. No subdirectories beyond `.lore/reference/` unless they already exist.

Each page is a Markdown file with YAML frontmatter:

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

`fg-sources` is a YAML list of relative paths. Include all source files that contributed to this page.

The body must be self-contained. Write it in Markdown. Reach for embedded inline HTML only when a visual carries meaning Markdown cannot — a color-coded status badge, an inline `<svg>` diagram, a side-by-side comparison. When you do, write it raw and inline; never in a fenced code block.

## Re-ingest (same source)

If a source path was previously ingested, some pages already exist. Before writing, read existing pages whose `fg-sources` frontmatter list includes the current source path. Compare content against what the source now says.

Three outcomes per existing page:

- **No change**: source still supports the page content. Leave the page alone.
- **Stale content**: source has changed or superseded the claim. Update the page body and reset `date` to today.
- **Contradiction**: source now asserts something that directly conflicts with the page. Note it during processing but do not surface it immediately and do not overwrite the page. Leave the page unchanged. At the end of the run, report all contradictions together, each with the page path, the existing claim, and what the source now says. Let the user decide.

Reconciliation is content comparison only. No activity log, no change history in the page.

## Index update

After all pages are written, update `.lore/reference/index.md`.

The index groups pages by `fg-type`. Within each group, each entry is a Markdown link to the page using the page's `title` as both the link text and a one-line description.

Add new pages to their group. Update link text and descriptions for modified pages. Do not remove entries for pages that weren't touched in this run. Preserve existing entries and groups that aren't affected.

If `index.md` does not exist, create it. If it exists but has no group structure yet, build it from scratch using all pages currently in `.lore/reference/`.

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
