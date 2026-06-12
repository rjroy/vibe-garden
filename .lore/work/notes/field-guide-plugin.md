---
title: "Implementation notes: field-guide plugin"
date: 2026-05-20
status: complete
tags: [field-guide, plugin, implementation, wiki]
source: .lore/work/specs/field-guide-plugin.md
modules: [field-guide]
---

# Implementation notes: field-guide plugin

2026-05-20 · source: field-guide-plugin.md

Complete — All 5 phases done, validation passed

## Phases

**1. Plugin scaffolding** — done

**Goal:** Create `field-guide/.claude-plugin/plugin.json` and `field-guide/skills/` directory structure.

**2. init skill** — done

**Goal:** Write `field-guide/skills/init/SKILL.md` — bootstrap wiki, register durable CronCreate lint job, idempotency via CronList.

**3. ingest skill** — done

**Goal:** Write `field-guide/skills/ingest/SKILL.md` — accept source paths, extract knowledge units by fg-type, create/update wiki pages, update index.html.

**4. query skill** — done

**Goal:** Write `field-guide/skills/query/SKILL.md` — accept question, read index.html, search wiki + .lore/work/, synthesize with citations, offer synthesis filing.

**5. lint skill** — done

**Goal:** Write `field-guide/skills/lint/SKILL.md` — contradictions (error), orphans (warning), stale sources (warning), missing concept pages (info), report by severity.

## Log

Session started 2026-05-20. No prior work found in lore. Spec: field-guide-plugin.md (REQ-FG-1 through REQ-FG-29). Agents: general-purpose (implementation), plugin-dev:skill-reviewer + plugin-dev:plugin-validator (review).
