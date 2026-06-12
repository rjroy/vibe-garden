---
title: field-guide plugin
date: 2026-05-20
status: approved
tags: [field-guide, plugin, wiki, knowledge-base, lore]
modules: [field-guide]
req-prefix: FG
---

# field-guide plugin

2026-05-20 · spec · field-guide, plugin, wiki, knowledge-base, lore

## Overview

field-guide is a Claude Code plugin that compiles `.lore/` artifacts into a persistent, query-able HTML wiki stored in `.lore/reference/`. It is a sibling to lore-development: lore-development generates working documents in `.lore/work/`; field-guide synthesizes them into reference material in `.lore/reference/`. The wiki compounds over time — each ingest adds to an evolving knowledge base rather than re-deriving knowledge from scratch.

The pattern is drawn from Andrej Karpathy's LLM Wiki: instead of RAG (re-deriving knowledge on every query), a persistent wiki is built once and kept current. The human curates sources and asks questions; the LLM does the bookkeeping.

## Entry Points

- User invokes `/field-guide:init` to bootstrap a project wiki and register scheduled lint
- User invokes `/field-guide:ingest` with one or more source paths
- User invokes `/field-guide:query` with a natural language question
- User invokes `/field-guide:lint` directly, or a scheduled job fires it automatically

## Requirements

### Plugin Structure

| ID | Requirement |
|----|-------------|
| REQ-FG-1 | field-guide is a Claude Code plugin at `field-guide/` in the vibe-garden repository with a `.claude-plugin/plugin.json` manifest. |
| REQ-FG-2 | The plugin exposes four user-invocable skills: `init`, `ingest`, `query`, `lint`. |

### Init

| ID | Requirement |
|----|-------------|
| REQ-FG-3 | Init creates the `.lore/reference/` directory if it does not exist and writes an empty `index.html`. |
| REQ-FG-4 | Init registers a durable scheduled lint job by calling CronCreate with `durable: true` and the prompt `/field-guide:lint`. The schedule is passed as an argument to init (`daily`, `weekly`); the default is daily. The job ID returned by CronCreate is stored in `.lore/reference/.field-guide.json`. |
| REQ-FG-5 | Init is idempotent — before registering a scheduled job, init reads `.lore/reference/.field-guide.json` to check for an existing job ID, then calls CronList to confirm the job is still active. If an active job exists, no new job is created. Existing wiki pages are never overwritten. |

### Ingest

| ID | Requirement |
|----|-------------|
| REQ-FG-6 | Ingest accepts one or more source paths from the user — individual files or directories within `.lore/`. |
| REQ-FG-7 | For each source, ingest uses model judgment to extract distinct knowledge units and creates or updates the corresponding wiki pages in `.lore/reference/`. |
| REQ-FG-8 | A single ingest may create or update multiple wiki pages from one source. |
| REQ-FG-9 | Re-ingesting a source reconciles existing wiki pages — stale content is updated and contradictions with existing pages are flagged to the user. Reconciliation is done by reading current wiki page content and comparing it against the source at ingest time; no separate activity log is maintained. |
| REQ-FG-10 | After ingest, `index.html` in `.lore/reference/` is updated to reflect new and modified pages. |
| REQ-FG-11 | Ingest is stateless — no activity log is maintained. The wiki itself is the record of what was ingested. |

### Wiki Pages

| ID | Requirement |
|----|-------------|
| REQ-FG-12 | Each wiki page is a self-contained HTML file stored under `.lore/reference/` with no external dependencies. |
| REQ-FG-13 | Wiki pages carry standard lore meta tags (`date`, `status`, `tags`) per the lore document schema. The standard `status` field tracks the page's document lifecycle using reference document values: `current`, `outdated`, `archived`. |
| REQ-FG-14 | Wiki pages additionally carry field-guide meta tags: `fg-type`, `fg-sources`, `fg-status`. The `fg-status` field tracks freshness relative to source files specifically: `current` (sources unchanged since ingest), `stale` (one or more sources modified since ingest), `archived` (deliberately retired). Lint uses `fg-status` to detect pages needing re-ingest. |
| REQ-FG-15 | Valid `fg-type` values: `decision`, `lesson`, `architecture`, `concept`, `synthesis`, `entity`. |
| REQ-FG-16 | `fg-sources` lists the `.lore/` paths the page was derived from, comma-separated. |

> **fg-type assignment:** Ingest uses model judgment to assign a type to each knowledge unit extracted from a source. A `decision` captures a resolved choice and its rationale. A `lesson` captures a generalized rule derived from experience (typically from retros or learned entries). An `architecture` captures how a system or component is structured. A `concept` captures a recurring term, pattern, or abstraction that appears across multiple sources. An `entity` captures a named person, system, or component. A `synthesis` is reserved for query answers filed back into the wiki — ingest never assigns this type.

### index.html

| ID | Requirement |
|----|-------------|
| REQ-FG-17 | `index.html` in `.lore/reference/` catalogs all wiki pages grouped by `fg-type`. |
| REQ-FG-18 | Each index entry includes a relative link to the wiki page and a one-line description drawn from the page's `<title>` element. |
| REQ-FG-19 | The query and lint skills read `index.html` first to discover all wiki pages before drilling into individual files. |

### Query

| ID | Requirement |
|----|-------------|
| REQ-FG-20 | Query accepts a natural language question from the user. |
| REQ-FG-21 | Query reads `index.html` to identify candidate pages, then reads the relevant pages to synthesize an answer. |
| REQ-FG-22 | Query searches both `.lore/reference/` wiki pages and `.lore/work/` source documents. |
| REQ-FG-23 | Query cites the specific pages used in the answer. |
| REQ-FG-24 | After answering, query offers to file the answer back into the wiki as a `synthesis` page. The resulting page lists the cited wiki and work pages in `fg-sources`. |

### Lint

| ID | Requirement | Severity |
|----|-------------|----------|
| REQ-FG-25 | Lint identifies contradictions between wiki pages. | error |
| REQ-FG-26 | Lint identifies orphaned wiki pages not listed in `index.html`. | warning |
| REQ-FG-27 | Lint identifies wiki pages whose `fg-sources` have a modification date newer than the wiki page itself, setting `fg-status` to `stale` on those pages. | warning |
| REQ-FG-28 | Lint identifies concepts mentioned across multiple pages that lack a dedicated `concept` page. | info |
| REQ-FG-29 | Lint produces a report with findings grouped by severity: error, warning, info. | |

## Success Criteria

- User can run `/field-guide:init` on a fresh project and get a bootstrapped `.lore/reference/` with a durable scheduled lint job registered and its ID stored in `.field-guide.json`
- Running `/field-guide:init` a second time produces no duplicate job
- User can ingest a `.lore/work/` artifact and find new HTML pages in `.lore/reference/` with correct `fg-type`, `fg-sources`, `fg-status` meta tags and an updated `index.html`
- User can re-ingest a changed source and see wiki pages updated and contradictions surfaced
- User can ask a natural language question and receive a cited answer drawing from both wiki and work documents
- User can file a query answer back as a `synthesis` page with correct `fg-sources`
- User can run lint and receive a findings report grouped by severity
- Scheduled lint fires without user intervention

## AI Validation

**How to verify this is done**

- **Init**: Running init on a fresh directory creates `.lore/reference/index.html` and `.field-guide.json` containing a CronCreate job ID. Running CronList shows the job as active. Running init again produces no additional entry in CronList.
- **Ingest**: Given a sample `.lore/work/` artifact, ingest produces one or more HTML pages in `.lore/reference/` carrying valid `fg-type`, `fg-sources`, and `fg-status` meta tags. `index.html` is updated and each new page is listed under its correct type group.
- **Query**: Given a populated wiki, a natural language question returns an answer that cites specific wiki or work pages by path. Filing back produces a valid `synthesis` HTML page in `.lore/reference/` with `fg-sources` listing the cited pages.
- **Lint**: Given a wiki with (a) a known orphan, (b) a source file modified after its wiki page, and (c) two pages making conflicting claims about the same concept, lint identifies all three findings at their correct severity levels (warning, warning, error).

## Constraints

- Wiki pages are HTML only — no shared stylesheets, no CDN references, no external assets
- Raw sources in `.lore/` are read-only — field-guide never modifies them
- Wiki and config live entirely within `.lore/reference/` — no files written outside this directory
- Scheduled lint uses CronCreate with `durable: true` — not an OS-level cron or background daemon
- CronCreate recurring jobs auto-expire after 7 days — users must re-run `/field-guide:init` to refresh the scheduled lint job

## Context

- Pattern source: Andrej Karpathy's LLM Wiki (May 2026)
- Sibling plugin: lore-development (generates `.lore/work/` artifacts that field-guide ingests)
- Document schema: `.claude/plugins/cache/vibe-garden/lore-development/*/shared/document-schema.md`
- **CronCreate** is a Claude Code harness tool that schedules a prompt string on a 5-field cron expression. With `durable: true` the job persists to `.claude/scheduled_tasks.json` and survives session restarts. It returns a job ID usable with CronDelete. CronList returns all active jobs for the current session.
