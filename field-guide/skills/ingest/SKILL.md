---
name: ingest
description: Use when distilling useful project understanding from eligible .lore/ artifacts into the reference wiki. Historical artifacts suggest candidates; current claims are checked against implementation and tests. Triggers include "ingest this", "distill reference knowledge", "update the reference", and "populate the field guide".
---

# Ingest

Distill useful project understanding into `.lore/reference/`. The reference is an aid to future work, not a contract or archive of project pages.

Keep only knowledge that code and tests do not adequately communicate and that materially helps a future change: rationale, real external constraints, relevant failed approaches, domain context, or useful current seams/coupling/refactoring guidance. Do not make a page just to summarize a feature, implementation, or source artifact. No useful candidate is a valid result; report that nothing was added.

## Sources

Accept one or more paths from the user. Sources should live under `.lore/`; warn and skip anything else. For directories, walk supported `.md` and `.html` files. Historical brainstorms, designs, intents, research, and retros can suggest candidates. Plans, notes, and tasks (including under `.lore/local/`) are never reference sources: they may point to where to investigate, but do not lift their execution choices or claims into reference knowledge. If a directory contains no eligible sources, report that and continue.

Treat Markdown and HTML sources as equivalent knowledge inputs:

- Markdown files use YAML frontmatter when present, followed by Markdown body content.
- HTML files use `<meta name="...">` fields when present, `<title>` as the title, and visible document body content as the source text. Ignore scripts, styles, and generated chrome that does not carry project knowledge.

## Extraction

Read each eligible source in full. Treat it only as a lead, not proof of current behavior or authority over current user direction. For every candidate about current behavior, architecture, constraints, or extension seams, inspect relevant implementation and tests; correct, qualify, or discard claims they do not support. Historical rationale may be retained when useful even if code cannot prove it, but label it as historical rationale rather than current behavior or a mandate. The user's current direction prevails over any old artifact; call out a concrete safety or compatibility consequence when one matters, not documentary noncompliance.

Before writing a unit, apply this reference-worthiness gate:

- Keep rationale, tradeoffs, real external constraints, domain rules, failed approaches, or lessons when they remain useful and code/tests do not communicate them.
- Keep current architecture, extension seams, ownership, lifecycle, or coupling only when it is not adequately apparent from code/tests and helps a likely future change; verify current claims against those sources.
- Skip ordinary implementation details that can be rebuilt from the source code: file lists, function inventories, endpoint names, schema fields, control flow summaries, library usage that is already visible in manifests, and transient task checklists.
- Skip plans, notes, and tasks as sources. Other historical documents are not requirements that future work must honor; their rationale is context, and current direction/evidence can supersede their choices.
- Do not add speculative future architecture, unused abstractions, feature catalogs, implementation summaries, or a page per artifact. Do not invent a “futures” score or promote an extension seam just because it might someday be useful.
- Before creating a page, compare the candidate with the existing wiki. Merge it into the best-fitting page, update/supersede an obsolete page, or retire redundant material rather than accumulating parallel summaries. Preserve valuable rationale proportionately; no mandatory history, template, or revisit checklist.
- If a source contains no reference-worthy units, do not create a page for it. Count the source as processed and report that no durable knowledge was found.

When in doubt, ask whether this knowledge is both missing from code/tests and materially useful to a future change. If either answer is no, skip it. A historical source alone is not enough to promote a claim.

Assign each unit an `fg-type`:

- `decision` — a resolved choice and its rationale ("we chose X over Y because Z")
- `lesson` — a generalized rule derived from experience, usually surfaced in retros or learned entries
- `architecture` — how a system, component, or data flow is structured
- `concept` — a recurring term, pattern, or abstraction used across the project
- `entity` — a named person, system, component, or external dependency

Do not assign `synthesis` — that type is reserved for query output.

When a unit is borderline between types, pick the type that best describes how someone would search for it. A lesson about an architectural decision is a `lesson`. A description of an architectural decision that is still the current approach is an `architecture`.

## Writing pages

For each surviving knowledge unit, update/merge the most relevant page or create a Markdown page in `.lore/reference/`. Retire or supersede obsolete redundant pages when appropriate, repairing the index and links. New pages should be kebab-case `.md` files. No page is required for every artifact or candidate.

If the wiki has been stratified into category directories (see the `stratify` skill — the index will have a "Layout" section), place a new page in the best-fitting existing category. Never invent new category directories during ingest. In an unstratified wiki, write pages directly in `.lore/reference/` — no subdirectories unless they already exist.

Compatibility rule: before creating a new page, check for an existing page for the same knowledge unit in either `.md` or `.html` form. Prefer updating an existing Markdown page. If only an HTML page exists for that unit, update that HTML page in place unless the user has asked to migrate it to Markdown. Do not create duplicate `.md` and `.html` pages for the same unit.

New Markdown pages use YAML frontmatter:

```markdown
---
title: Precise noun-first description of the knowledge unit
date: YYYY-MM-DD
status: draft
tags: [kebab-case, terms, subject, domain, problem-type]
fg-type: decision|lesson|architecture|concept|entity
fg-sources: [relative/path/to/source.md]
fg-status: current
---

# Precise noun-first description of the knowledge unit

<!-- body in Markdown -->
```

`fg-sources` is a YAML list of relative paths. Include all source files that contributed to this page; paths may end in `.md` or `.html`.

`status` is the shared lore lifecycle (`draft`, `approved`, `completed`, or `archived`), not freshness; `fg-status` separately records field-guide freshness. New agent-created pages start `draft`. Use `approved` only for explicit user approval (including editing to approve) or when the user asks for the relevant next process step; arbitrary edits are not approval. Mark applicable agent work `completed` when done, independently of approval. Current user direction may revise approved pages; approval is not a veto or mandatory gate. Do not ask approval for minor transitions or every page.

The body must be self-contained. Write it in Markdown. Reach for embedded inline HTML only when a visual carries meaning Markdown cannot — a color-coded status badge, an inline `<svg>` diagram, a side-by-side comparison. When you do, write it raw and inline; never in a fenced code block.

## Re-ingest (same source)

`fg-sources` records provenance only; it does not grant authority, establish currency, or make an old choice binding. When a source changes, reassess affected claims against current implementation/tests and user direction. Do not preserve a claim merely because the older source supported it.

Three outcomes per existing page:

- **Still useful/current**: independently grounded behavior remains accurate and knowledge still earns reference space; update only as needed.
- **Superseded/redundant**: merge or retire the page and repair the index/references.
- **Historical rationale**: preserve only if useful, clearly framed as history rather than instruction.

Do not treat a conflict between historical sources as a blocker or require the user to arbitrate old documents. Ask only when current intent itself is unclear or a material consequence requires a decision. No activity log or change history in the page.

## Index update

After all pages are written, update the field-guide index. Prefer `.lore/reference/index.md`. If only `.lore/reference/index.html` exists, update it in place unless the user asked to migrate the index to Markdown. If neither exists, create `.lore/reference/index.md`.

The index groups pages by `fg-type`. If the wiki is stratified and the index is organized by category instead, keep that structure: add each entry under its page's category (and subcategory) heading, with the link path relative to `.lore/reference/`. Within each group, each entry links to the page using the page's `title` as both the link text and a one-line description. Markdown indexes use Markdown links. HTML indexes use normal anchor links.

Add surviving pages, update changed entries, and remove entries for pages retired in this run. Preserve unrelated entries and groups.

If the index exists but has no group structure yet, build it from scratch using all supported pages currently in `.lore/reference/`, including both `.md` and `.html` pages.

Example index structure:

```markdown
---
title: Field Guide Index
date: YYYY-MM-DD
status: completed
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

- Sources considered and whether any candidates were independently grounded
- Pages created, merged/updated, or retired (if any)
- Any concrete unresolved uncertainty; do not report mere disagreement with an old artifact as a blocker
