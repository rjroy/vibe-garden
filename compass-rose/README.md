# Compass Rose

<img src="logo.webp" align="right" width="128" height="128" alt="Compass Rose Logo">

A file-based issue tracker for solo projects. Zero config, no GitHub required.

## What It Is

Compass Rose manages your backlog as HTML files in `.lore/work/issues/`, versioned with your code. Issues live next to the work they describe. No external services, no authentication setup, no project number hunting. Install it and start filing.

It complements [Lore Development](../lore-development/) by handling small, actionable items (bugs, quick tasks, feature seeds) that don't yet warrant a full spec or plan.

## Installation

```
/plugin install compass-rose@vibe-garden
```

## Issue File Format

Issues are stored at `.lore/work/issues/[kebab-title].html` using the standard lore schema meta fields plus two optional compass-rose fields:

```html
<meta name="title" content="Short descriptive title">
<meta name="date" content="YYYY-MM-DD">
<meta name="status" content="open|in-progress|closed">
<meta name="tags" content="bug, auth">
<meta name="priority" content="P0|P1|P2|P3">
<meta name="size" content="S|M|L|XL">
```

Priority runs P0 (critical) to P3 (low). Size runs S to XL. Both are optional but improve `/next-item` and `/reprioritize` output.

## Skills

**`/compass-rose:add-item`** — File a new issue. Prompts for title, description, priority, and size. Status is always `open` on creation. Writes the issue file directly to `.lore/work/issues/`. No GitHub required.

**`/compass-rose:next-item`** — Recommend the highest-priority open issue. Sorts by priority first, then by date within a priority tier. Returns a single recommendation with rationale so the human makes the call.

**`/compass-rose:backlog`** — Full backlog health analysis via the backlog-analyzer agent. Scores definition quality across open issues, flags vague or stale items, and surfaces patterns (priority clustering, size distribution, tag gaps).

**`/compass-rose:reprioritize`** — Scan the codebase against open issues. Identifies issues that reference code that has changed, been refactored, or no longer exists. Presents a recommended priority and status change for each affected issue, then updates the HTML meta tags after user confirmation.
