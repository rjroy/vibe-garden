# Field Guide

<img src="logo.webp" align="right" width="128" height="128" alt="Field Guide Logo">

A Claude Code plugin that compiles `.lore/` artifacts into a persistent, query-able project wiki.

## What It Does

Most knowledge work produces scattered artifacts: specs, retros, design decisions, lessons learned. Field Guide reads those artifacts and synthesizes the durable knowledge they contain into a wiki stored in `.lore/reference/`. The wiki compounds over time and preserves context the source code cannot recover on its own: intent, rationale, constraints, rejected alternatives, operating lessons, and domain vocabulary.

Field Guide is a sibling to lore-development. lore-development generates artifacts in `.lore/work/`; field guide synthesizes them into reference material in `.lore/reference/`.

## Skills

| Skill | Purpose |
|-------|---------|
| `/field-guide:init` | Bootstrap the wiki directory and register a scheduled daily lint job |
| `/field-guide:ingest` | Compile one or more `.lore/` artifacts into wiki pages |
| `/field-guide:update-evidence` | Attach living code/test anchors to reference pages |
| `/field-guide:resolve-drift` | Compare reference pages against evidence and reconcile semantic drift |
| `/field-guide:query` | Answer natural language questions against the wiki |
| `/field-guide:stratify` | Reorganize an overgrown wiki into category directories and repair every referrer |
| `/field-guide:lint` | Health-check the wiki for contradictions, orphans, stale pages, missing concept pages, and overgrown directories |

## Workflow

**Start with init.** Run `/field-guide:init` once per project to create `.lore/reference/` and register a daily lint job. Re-run it after 7 days to refresh the scheduled job (CronCreate recurring jobs auto-expire after 7 days).

**Ingest as you go.** After completing work in lore-development (finishing a retro, approving a spec, closing out a design), run `/field-guide:ingest` pointing at the new artifact or a whole directory. Ingest reads Markdown and HTML sources, extracts distinct durable knowledge units, skips implementation details that can be reconstructed from code, and writes the surviving guidance as typed wiki pages. Re-ingesting an existing source reconciles the wiki against the updated content and flags contradictions for your review.

**Wire evidence after ingestion.** Run `/field-guide:update-evidence` to connect reference pages to living code, tests, data files, and symbols. Treat `fg-sources` as ingestion provenance; source artifacts can be deleted after durable knowledge is captured. Evidence anchors are what future checks use to notice likely drift.

**Resolve semantic drift when evidence changes.** Run `/field-guide:resolve-drift` when code or tests have moved under an evidence-backed page, or when you want an audit of reference accuracy. This pass reads the page plus its evidence, then updates stale prose, refreshes evidence, or reports implementation drift from intended design.

**Query the accumulated knowledge.** Run `/field-guide:query` with a natural language question. The skill reads the wiki index, pulls relevant pages, searches `.lore/work/` for additional context, and synthesizes a cited answer. You can file the answer back into the wiki as a synthesis page.

**Stratify when the wiki outgrows a flat directory.** Once a directory accumulates more than ~12 pages, run `/field-guide:stratify` to group pages into topical category directories (3-4 groups per split, adjusting toward 6-7 top-level categories as the wiki grows). Stratify moves pages, rewrites the index by category, and repairs every link that referenced the old paths — inside the wiki and across the repository. After the first run, later runs split only the directories that have outgrown the threshold. Ingest and query place new pages into the category layout automatically.

**Let lint run, or trigger it manually.** The scheduled lint job fires daily and checks for stale pages, orphans, contradictions, concepts that deserve their own page, and directories due for stratification. Run `/field-guide:lint` directly any time you want a health check.

## Output Structure

Wiki pages live in `.lore/reference/`. New pages are Markdown by default, and existing HTML pages remain supported during migration. HTML pages should be self-contained with no external stylesheets or scripts.

```
.lore/reference/
├── index.md                # Catalog of all wiki pages, grouped by type
├── .field-guide.json       # Scheduled lint job ID and schedule config
└── <wiki-pages>.md         # Generated pages
```

After stratification, pages live in topical category directories and the index is grouped by category instead of type. The index still lists every page — lint discovers pages only through index links:

```
.lore/reference/
├── index.md                        # Catalog of all wiki pages, grouped by category
├── .field-guide.json
├── <category>/<page>.md
└── <category>/<subcategory>/<page>.md
```

Mixed-format projects are valid:

```
.lore/reference/
├── index.md or index.html
├── existing-page.html
└── new-page.md
```

### Page Types

Each wiki page carries an `fg-type` field that describes what kind of knowledge it holds:

| Type | What it captures |
|------|-----------------|
| `decision` | A resolved choice and its rationale |
| `lesson` | A generalized rule derived from experience |
| `architecture` | How a system or component is structured |
| `concept` | A recurring term, pattern, or abstraction |
| `entity` | A named person, system, or component |
| `synthesis` | A query answer filed back into the wiki |

### Page Metadata

Markdown pages carry YAML frontmatter. HTML pages carry equivalent `<meta name="...">` tags. Each page includes standard lore fields (`date`, `status`, `tags`) plus field-guide-specific fields:

- `fg-type` — the page type (see above)
- `fg-sources` — paths to the `.lore/` artifacts this page was derived from; YAML list in Markdown, comma-separated or YAML-like value in HTML
- `fg-status` — `current`, `stale` (set by lint when sources have changed), or `archived`
- `fg-evidence` — optional living code/test/symbol anchors for Markdown pages
- `fg-evidence-code`, `fg-evidence-tests`, `fg-evidence-symbols` — optional living anchors for HTML pages

## Dependencies

The `init` skill requires `CronCreate` and `CronList` from the Claude Code harness to register the scheduled lint job. If those tools are unavailable, the wiki directory and `index.md` are still created, but scheduling will not be set up.
