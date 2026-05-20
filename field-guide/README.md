# Field Guide

<img src="logo.webp" align="right" width="128" height="128" alt="Field Guide Logo">

A Claude Code plugin that compiles `.lore/` artifacts into a persistent, query-able HTML wiki.

## What It Does

Most knowledge work produces scattered artifacts: specs, retros, design decisions, lessons learned. Field Guide reads those artifacts and synthesizes them into a wiki stored in `.lore/reference/`. The wiki compounds over time. Each ingest adds to an evolving knowledge base rather than re-deriving knowledge from scratch on every question.

Field Guide is a sibling to lore-development. lore-development generates artifacts in `.lore/work/`; field guide synthesizes them into reference material in `.lore/reference/`.

## Skills

| Skill | Purpose |
|-------|---------|
| `/field-guide:init` | Bootstrap the wiki directory and register a scheduled daily lint job |
| `/field-guide:ingest` | Compile one or more `.lore/` artifacts into wiki pages |
| `/field-guide:query` | Answer natural language questions against the wiki |
| `/field-guide:lint` | Health-check the wiki for contradictions, orphans, stale pages, and missing concept pages |

## Workflow

**Start with init.** Run `/field-guide:init` once per project to create `.lore/reference/` and register a daily lint job. Re-run it after 7 days to refresh the scheduled job (CronCreate recurring jobs auto-expire after 7 days).

**Ingest as you go.** After completing work in lore-development (finishing a retro, approving a spec, closing out a design), run `/field-guide:ingest` pointing at the new artifact or a whole directory. Ingest reads the source, extracts distinct knowledge units, and writes them as typed wiki pages. Re-ingesting an existing source reconciles the wiki against the updated content and flags contradictions for your review.

**Query the accumulated knowledge.** Run `/field-guide:query` with a natural language question. The skill reads the wiki index, pulls relevant pages, searches `.lore/work/` for additional context, and synthesizes a cited answer. You can file the answer back into the wiki as a synthesis page.

**Let lint run, or trigger it manually.** The scheduled lint job fires daily and checks for stale pages, orphans, contradictions, and concepts that deserve their own page. Run `/field-guide:lint` directly any time you want a health check.

## Output Structure

All wiki pages are self-contained HTML files in `.lore/reference/`. No external stylesheets or scripts.

```
.lore/reference/
├── index.html              # Catalog of all wiki pages, grouped by type
├── .field-guide.json       # Scheduled lint job ID and schedule config
└── <wiki-pages>.html       # Generated pages
```

### Page Types

Each wiki page carries an `fg-type` meta tag that describes what kind of knowledge it holds:

| Type | What it captures |
|------|-----------------|
| `decision` | A resolved choice and its rationale |
| `lesson` | A generalized rule derived from experience |
| `architecture` | How a system or component is structured |
| `concept` | A recurring term, pattern, or abstraction |
| `entity` | A named person, system, or component |
| `synthesis` | A query answer filed back into the wiki |

### Page Metadata

Each page carries standard lore meta tags (`date`, `status`, `tags`) plus field-guide-specific tags:

- `fg-type` — the page type (see above)
- `fg-sources` — comma-separated paths to the `.lore/` artifacts this page was derived from
- `fg-status` — `current`, `stale` (set by lint when sources have changed), or `archived`

## Dependencies

The `init` skill requires `CronCreate` and `CronList` from the Claude Code harness to register the scheduled lint job. If those tools are unavailable, the wiki directory and `index.html` are still created, but scheduling will not be set up.
