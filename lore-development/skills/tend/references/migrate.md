# Migrate Mode Reference

One-shot migration from the legacy `.lore/` layout to the three-directory model
(`build/`, `reference/`, `learned/`). Backed by
`${CLAUDE_PLUGIN_ROOT}/scripts/tend_migrate.py`.

## Purpose

Move a project from the pre-redesign `.lore/` layout (14 top-level subject
directories plus `.lore/vision.md`) to the canonical three-directory model.
Updates internal path references at the same time so the post-migration tree
is internally consistent.

This mode is **not** part of the default `/tend` sequential run
(`status → tags → filenames → directories`). It runs only when invoked
explicitly. Once a project is migrated, `/tend migrate` re-runs are no-ops.

## Invocation

```
/tend migrate                # Dry-run (default)
```

Run the script directly with `--apply` once you've reviewed the plan:

```
python ${CLAUDE_PLUGIN_ROOT}/scripts/tend_migrate.py            # dry-run
python ${CLAUDE_PLUGIN_ROOT}/scripts/tend_migrate.py --apply    # confirm prompt
python ${CLAUDE_PLUGIN_ROOT}/scripts/tend_migrate.py --apply --yes
```

The script writes to the project's `.lore/` (default `./.lore`). Pass
`--lore-dir <path>` to point at a different tree.

## Detection

`/tend migrate` considers a project to be on the legacy layout if any of these
are present at `.lore/` root:

- `brainstorm/`, `specs/`, `design/`, `plans/`, `tasks/`, `notes/`,
  `research/`, `retros/`, `issues/`, `ideas/`, `validation/`, `stubs/`,
  `excavations/`, `diagrams/`
- `vision.md`

When none are present, the script reports "no legacy structure detected" and
exits cleanly.

## Move plan

Files move to the new home defined by REQ-REDESIGN-6 in
`.lore/specs/lore-redesign.md`. Summary:

| Old location               | New location                  |
|----------------------------|-------------------------------|
| `.lore/<subject>/...`      | `.lore/build/<subject>/...`   |
| `.lore/vision.md`          | `.lore/reference/vision.md`   |
| `.lore/diagrams/*`         | `.lore/build/diagrams/*` (default; promote individuals to `reference/diagrams/` after migrate) |

`build/`, `reference/`, and the necessary subdirectories are created on
demand. `.lore/learned/` is **not** pre-created; it is born on first `/learn`
invocation (REQ-REDESIGN-4).

## Link rewriting

For every markdown file that is being moved or already lives under the new
tree, the script rewrites legacy `.lore/<subject>/...` and `.lore/vision.md`
references in three contexts:

1. Frontmatter `related:` values
2. Frontmatter `source:` values
3. In-body markdown links (`[text](.lore/<old>/...)`, prose mentions, etc.)

**Fenced code blocks are never rewritten.** Snippets inside ` ``` ` or `~~~`
are documentation, not live links. Indented (4-space) code blocks are *not*
detected — if a legacy path inside an indented block matters, switch the block
to fenced syntax before running `/tend migrate` or mark the file as a
`migration-doc` to skip body rewriting entirely.

## Migration-doc opt-out

Documents whose frontmatter `tags:` list contains `migration-doc` keep their
body verbatim — the whole point of a migration walkthrough is to show old
paths in prose. Frontmatter `related:` and `source:` values are still
rewritten, and the file is still moved if it sits in a legacy directory.

Convention:

```yaml
---
title: "How we migrated to the three-directory layout"
tags: [migration-doc, docs]
---
```

## Protected paths

`/tend migrate` does **not** touch:

- `.lore/commissions/` (guild-hall scope)
- `.lore/meetings/` (guild-hall scope)
- `.lore/heartbeat.md`
- `.lore/lore-agents.md`
- `.lore/lore-config.md`
- Any directory listed in `.lore/lore-config.md`'s `custom_directories`

Files inside protected paths keep their content as-is, even if they reference
old `.lore/` paths.

## Dry-run by default

`tend_migrate.py` prints a full plan on every run: every move, every rewrite
(line-by-line `before` → `after`). Without `--apply`, no files are touched.
With `--apply` and without `--yes`, the script asks for explicit confirmation
before executing.

## Idempotency guarantee

Running `/tend migrate` against an already-migrated tree finds no legacy
top-levels and exits without changes. Re-running after a successful apply is
safe and reports "no legacy structure detected."

## Workflow

1. Run `/tend migrate` (or `python ${CLAUDE_PLUGIN_ROOT}/scripts/tend_migrate.py`).
2. Read the printed plan. Pay attention to:
   - Files moved into `build/diagrams/`. If any belong in
     `reference/diagrams/`, promote them manually after the migration.
   - Rewrites that touch a `migration-doc` (their bodies should be untouched —
     verify the line list reflects this).
3. Re-run with `--apply`.
4. Spot-check internal links resolve in the post-migration tree.
5. Commit.

## Related

- Spec: `.lore/specs/lore-redesign.md` (REQ-REDESIGN-18 through 25).
- Schema: `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`.
- Other tend modes: `references/{status,tags,filenames,directories,lore-config}.md`.
