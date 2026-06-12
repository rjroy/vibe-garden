---
title: "Compass Rose rework: file-based issue tracker"
date: 2026-05-20
status: approved
tags: [compass-rose, issue-tracking, file-based, refactor, lore-development]
modules: [compass-rose, lore-development]
req-prefix: CR
---

# Compass Rose rework: file-based issue tracker

Compass Rose currently requires a GitHub Project, a config file, and an extra auth scope. That setup cost is not worth it for solo projects. This spec reworks it as a file-based issue tracker: issues live in `.lore/work/issues/`, no external dependencies, zero config.

## Context and decisions

The `file-issue` skill in lore-development already writes to `.lore/work/issues/` using the standard document schema. Compass Rose's `add-item` is the same action plus GitHub overhead. Consolidating them removes duplication and makes compass-rose the single place for issue tracking, from "log this quick" through "what should I work on next."

`start-work` is retired. Its main value was updating GitHub Projects status; without that, it adds nothing that `/lore-development:implement` doesn't already cover. `gh-api-scripts` becomes dead code and is deleted. The vision document's anti-goal ("the backlog lives in GitHub") contradicts Principle 3 (file-based state is a deliberate constraint) — the vision must be updated to reflect this direction change.

## Change summary

| Item | Before | After |
|------|--------|-------|
| `compass-rose/add-item` | Creates GitHub Issue + links to Project | Creates `.lore/work/issues/` HTML file |
| `compass-rose/next-item` | Queries GitHub Projects GraphQL API | Reads local issue files, sorts by priority meta |
| `compass-rose/backlog` | Queries GitHub Projects, spawns analyzer | Reads local issue files, spawns analyzer |
| `compass-rose/reprioritize` | Full codebase scan + batch GitHub API updates | Scan + update local file meta; no batch API calls, no saved report |
| `compass-rose/start-work` | Updates GitHub status, loads issue | Retired |
| `compass-rose/gh-api-scripts` | GitHub Projects API scripts + tests | Deleted |
| `lore-development/file-issue` | Standalone issue-filing skill | Retired (superseded by add-item) |
| `.compass-rose/` directory | Required per-repo config directory | Deleted (entire directory, no config needed) |
| `compass-rose/README.md` | 870-line GitHub Projects documentation | Rewritten for file-based model; all GitHub Projects content removed |
| `lore-development/README.md` | Lists `file-issue` in skills table | Updated to remove `file-issue` row; no broken skill reference |
| Agents: `backlog-analyzer`, `codebase-scanner` | Work against GitHub Projects data | Kept, work against local issue files |

## Issue file format

Issues use the standard lore document schema. Two additional meta tags carry structured metadata:

- `<meta name="priority" content="P0|P1|P2|P3">` — optional; P0 is most urgent
- `<meta name="size" content="S|M|L|XL">` — optional

Status values follow the document schema: `open`, `resolved`, `wontfix`, `archived`. Filename is kebab-case of the issue title.

## Requirements

### REQ-CR-1 — Zero config — no setup required to use any skill

No configuration file, no GitHub authentication, no external dependency of any kind. All skills work immediately in any repository. The `.compass-rose/` directory and its `config.json` are removed from the plugin entirely.

### REQ-CR-2 — Issues are HTML files in `.lore/work/issues/`

All issue files conform to the lore document schema. Required meta fields: `date`, `status`, `tags`. Optional structured meta fields: `priority` (P0–P3) and `size` (S/M/L/XL). Filename is kebab-case of the issue title.

The body is freeform HTML: observation, why it matters, fix direction if known. A visible status badge and priority indicator are required in the rendered output.

### REQ-CR-3 — `add-item` replaces `lore-development:file-issue`

`add-item` prompts for title, description, priority (P0–P3, optional), and size (S/M/L/XL, optional). Status always defaults to `open` — no prompt needed. It creates a conforming issue file at `.lore/work/issues/[kebab-title].html`.

There is no XL escalation prompt. The nudge to spec large items before starting work was part of `start-work`'s flow, which is retired. Users can invoke `/lore-development:specify` directly when they judge it necessary.

If the observation is too vague to write up clearly, the skill says so rather than filing a placeholder. After filing, the skill moves on — it does not work the issue.

The `file-issue` skill in lore-development is retired. Its `SKILL.md` is removed. `lore-development/README.md` must be updated to remove the `file-issue` row from the skills table.

### REQ-CR-4 — `next-item` works from local issue files

Reads all `.lore/work/issues/*.html` files with `status: open`. Sorts by priority (P0 > P1 > P2 > P3 > unprioritized), then by date ascending. Displays top 2–3 options in a table with title, priority, size, and date. Provides a recommendation with rationale.

If no open issues exist, says so clearly and suggests `add-item`.

### REQ-CR-5 — `backlog` works from local issue files

Reads all issue files with status `open` or `wontfix` (wontfix items are deferred, not done — intentionally included so they surface if priority context changes). Spawns the `backlog-analyzer` agent to score each issue on clarity, completeness, and fix direction. Reports: top 2–3 recommendations, a health summary (priority distribution, definition quality breakdown), and a list of vague items needing clarification.

The `backlog-analyzer` agent is updated to accept a file-based input array instead of GitHub Projects GraphQL JSON. New input shape per item:

```
{ filepath, title, priority, size, status, date, body }
```

Output format is unchanged (scored recommendations + health summary), but issue references use file paths instead of GitHub issue numbers and URLs.

### REQ-CR-6 — `reprioritize` is simplified: scan + update local meta

Reads all open issue files. Spawns the `codebase-scanner` agent to compare issue descriptions against current code. For each issue, the agent reports whether it appears already resolved, unchanged, more urgent, or less urgent than its current priority.

Presents recommendations with codebase evidence. After user confirmation, updates the `priority` and/or `status` meta tags in the affected HTML files directly. No batch GitHub API calls. No report file saved to disk.

The `codebase-scanner` agent is updated to accept the same file-based input array as `backlog-analyzer`: `{ filepath, title, priority, size, status, date, body }`. Its output changes from `gh project item-edit` batch commands to a list of file path + meta field update pairs that the skill applies directly. All other output structure (recommendations table, codebase evidence, confidence levels) is unchanged.

### REQ-CR-7 — `start-work` and `gh-api-scripts` are removed

The `start-work` skill directory is deleted. The `gh-api-scripts` skill directory (scripts and tests) is deleted. No references to either remain in the plugin.

### REQ-CR-8 — READMEs updated; vision document updated

**compass-rose/README.md**: The current README documents GitHub Projects setup, auth scopes, config file format, and skills that are being deleted. It is rewritten to describe the file-based model: issue file format, the four surviving skills, and zero-config operation. All GitHub Projects references are removed.

**lore-development/README.md**: The skills table currently lists `/lore-development:file-issue`. That row is removed. No replacement row is needed — `compass-rose:add-item` is the replacement and lives in a different plugin.

**.lore/reference/vision.md**: The vision currently contains a direct conflict — an anti-goal states "the backlog lives in GitHub," while Principle 3 states file-based state is a deliberate constraint. The anti-goal is updated to reflect that compass-rose is now a file-based tracker and GitHub Projects is no longer part of the system. _Note: the file exists as `vision.md`, not `vision.html` — the document schema's canonical path differs from reality here._

## AI Validation

After implementation, verify the following behaviorally:

1. **Zero config:** Run `/compass-rose:add-item` in a repo with no `.compass-rose/` directory and no `gh` authentication. The skill completes without error and creates a file in `.lore/work/issues/`.
2. **Issue file conformance:** Inspect the created file — it must have valid `date`, `status: open`, `tags` meta fields, and optional `priority` / `size` meta fields if provided. Body must include a visible status badge.
3. **next-item sorting:** Create three issue files with priorities P2, P0, and no priority. Run `/compass-rose:next-item` and confirm the P0 item is recommended first, P2 second, unprioritized last.
4. **No GitHub Projects calls:** Grep the entire `compass-rose/` directory for `gh project`, `GraphQL`, and `config.json` references. Zero matches expected.
5. **lore-development cleanup:** Confirm `lore-development/skills/file-issue/SKILL.md` no longer exists. Confirm `lore-development/README.md` contains no reference to `file-issue`.
6. **start-work and gh-api-scripts deleted:** Confirm `compass-rose/skills/start-work/` and `compass-rose/skills/gh-api-scripts/` no longer exist.
7. **next-item date tiebreaker:** Create two issue files with the same priority (P1) but different dates. Run `/compass-rose:next-item` and confirm the older file appears first.
8. **reprioritize updates files:** Create an open issue file with `priority: P2`. Run `/compass-rose:reprioritize` against a repo where the issue is clearly resolved. Confirm that after approval, the file's meta tag is updated (priority changed or status set to `resolved`).
