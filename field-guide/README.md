# Field Guide

<img src="logo.webp" align="right" width="128" height="128" alt="Field Guide Logo">

A Claude Code plugin for distilling useful project understanding into a searchable `.lore/reference/` wiki.

## What It Does

Project knowledge appears in scattered artifacts. Field Guide can use eligible historical artifacts as leads to preserve useful rationale, real constraints, failed approaches, and context that code/tests do not adequately communicate. Current behavior claims are checked against implementation and tests. The wiki is explanatory context, not legal authority, a contract, or an archive; current user direction prevails. Keep it selective: merge, update, supersede, or retire pages rather than accumulating a page per artifact. Adding nothing is a valid outcome.

Field Guide is a sibling to lore-development. lore-development generates artifacts in `.lore/work/`; field guide synthesizes them into reference material in `.lore/reference/`.

For an optional preview-first move of legacy `.lore/work/specs/`, `plans/`, `tasks/`, and `notes/`, use `/lore-development:migrate`. Migration preserves these artifacts as historical context; it does not promote them into field-guide reference pages.

## Skills

| Skill | Purpose |
|-------|---------|
| `/field-guide:init` | Bootstrap the wiki directory and register a scheduled daily lint job when Claude Cron tools are available |
| `/field-guide:ingest` | Compile one or more `.lore/` artifacts into wiki pages |
| `/field-guide:update-evidence` | Attach living code/test anchors to reference pages |
| `/field-guide:resolve-drift` | Compare reference pages against evidence and reconcile semantic drift |
| `/field-guide:query` | Answer natural language questions against the wiki |
| `/field-guide:stratify` | Reorganize an overgrown wiki into category directories and repair every referrer |
| `/field-guide:lint` | Health-check the wiki for contradictions, orphans, stale pages, missing concept pages, and overgrown directories |

## Workflow

Run `/field-guide:init` to create `.lore/reference/` and register a daily lint job when the Claude Code harness provides `CronCreate` and `CronList`. Without those tools, wiki setup still succeeds but scheduling is skipped. Re-run init after 7 days to refresh the scheduled job (CronCreate recurring jobs auto-expire after 7 days).

**Distill when useful.** `/field-guide:ingest` can take historical brainstorms, designs, intents, research, and retros as candidate leads. It independently checks current claims against code/tests, skips knowledge already apparent there, and retains only material that can help a future change. Plans, notes, and tasks (including local plans) are not reference sources; at most they can suggest where to investigate. No candidate need produce a page.

**Evidence is optional and scoped.** `/field-guide:update-evidence` connects current behavior claims to code/tests. `fg-sources` is provenance only; it does not establish authority or currency, and source artifacts can be deleted.

**Review accuracy when useful.** `/field-guide:resolve-drift` compares current behavior claims with evidence and user direction. It can update, merge, supersede, or retire pages; historical design differences are reported as context, not automatic implementation failures.

**Query the reference.** `/field-guide:query` answers with citations, separating code/test-backed behavior from historical rationale. Work artifacts may offer context or investigation leads, not authority; plans, notes, and tasks are not reference sources, and current user direction prevails. Save a synthesis only if it adds useful understanding not already present.

**Stratify when the wiki outgrows a flat directory.** Once a directory accumulates more than ~12 pages, run `/field-guide:stratify` to group pages into topical category directories (3-4 groups per split, adjusting toward 6-7 top-level categories as the wiki grows). Stratify moves pages, rewrites the index by category, and repairs every link that referenced the old paths — inside the wiki and across the repository. After the first run, later runs split only the directories that have outgrown the threshold. Ingest and query place new pages into the category layout automatically.

**Lint when useful.** `/field-guide:lint` checks wiki structure and surfaces review leads. Changed source timestamps do not prove a page stale or make a historical source binding; use resolve-drift for semantic validation.

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
- `fg-status` — `current`, `stale` (semantic review found outdated content; provenance timestamps alone do not establish staleness), or `archived`
- `fg-evidence` — optional living code/test/symbol anchors for Markdown pages
- `fg-evidence-code`, `fg-evidence-tests`, `fg-evidence-symbols` — optional living anchors for HTML pages

## Dependencies

The `init` skill requires `CronCreate` and `CronList` from the Claude Code harness to register the scheduled lint job. If those tools are unavailable, the wiki directory and `index.md` are still created, but scheduling will not be set up.
