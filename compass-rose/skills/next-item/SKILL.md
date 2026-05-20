---
name: next-item
description: Use when the user asks "what should I work on", "what's next", "highest priority", "next item", or invokes /compass-rose:next-item. Reads local issue files and recommends the highest-priority open item.
allowed-tools: Bash, Read, Glob
---

# Next Item Recommendation

You are in Next Item Recommendation mode. Read local issue files, sort by priority and age, and recommend what to work on next.

## Workflow

### 1. Find Open Issues

Use Glob to find all issue files:

```
.lore/work/issues/*.html
```

If no files exist, tell the user there are no issues tracked yet and suggest `/compass-rose:add-item`.

### 2. Extract Metadata

For each file, extract the following meta tags and the page title. The most efficient approach is a single grep pass:

```bash
grep -h 'name="status"\|name="priority"\|name="size"\|name="date"\|<title>' .lore/work/issues/*.html
```

Fields to collect per file:
- `status` — keep only files where this is `open`
- `priority` — P0, P1, P2, P3, or absent
- `size` — any value present (e.g. S, M, L, XL)
- `date` — ISO date string
- `title` — from the `<title>` tag

If no open issues exist after filtering, say so clearly and suggest `/compass-rose:add-item`.

### 3. Sort

Sort the open issues by:

1. **Priority** (primary): P0 first, then P1, P2, P3, unprioritized last
2. **Date** (tiebreaker): ascending — oldest issue first

### 4. Present Top Items

Display the top 2–3 as a table:

```
| # | Title                        | Priority | Size | Date       |
|---|------------------------------|----------|------|------------|
| 1 | Fix session expiry handling  | P0       | S    | 2026-03-12 |
| 2 | Add export to CSV            | P1       | M    | 2026-02-28 |
| 3 | Improve error messages       | P1       | S    | 2026-04-01 |
```

Follow with a recommendation paragraph: name the top item, its priority, and a plain-language rationale for why it ranks first (priority level, age, or both if relevant).

If two items tie on priority, note that date broke the tie.

### 5. Edge Cases

**No open issues**: State that clearly. Suggest `/compass-rose:add-item` to create the first one.

**Missing priority on some items**: Treat them as lower than P3. Mention in the output that some items have no priority set.

**Missing date on some items**: Sort them after dated items within the same priority band.

## Anti-Patterns

- Do not reference GitHub, gh CLI, or any remote API
- Do not run git log or any codebase analysis
- Do not show more than 3 items
- Do not prompt the user to start work — just present the recommendation

## Related Skills

- `/compass-rose:add-item` — create a new issue
- `/compass-rose:backlog` — review the full backlog
- `/compass-rose:reprioritize` — adjust priorities across the backlog
