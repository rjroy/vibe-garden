---
name: migrate
description: Preview and, after explicit user confirmation, migrate pre-work and .lore/work lore layouts into historical intents, shared work, and gitignored local paths, converting legacy HTML artifacts to Markdown with original-byte backups. Does not migrate project files automatically.
---

# Migrate

Help a project transition legacy lore folders into the current storage layout without rewriting their history. This skill is optional; existing files remain readable if the user does not migrate them.

## Scope and safety

The helper is `scripts/migrate_lore.py`, resolved from this skill's installed plugin directory. It supports flat legacy directories directly under `.lore/` and equivalent legacy subdirectories under `.lore/work/`:

- `specs/**` → `.lore/work/intents/**` (legacy specs under `.lore/work/` use the same destination)
- `intents`, `brainstorm`, `design`, `research`, `retros`, `issues`, `ideas`, `validation`, `stubs`, `diagrams`, and `excavations` → matching `.lore/work/` directories
- `plans`, `tasks`, and `notes` → matching `.lore/local/` directories

Preserve nested names, numbering, bodies, and unrelated frontmatter. During explicit migration, mapped legacy documents' `status` is normalized per `shared/frontmatter-schema.md`; changed values are retained in `legacy_status`. In particular, legacy `current`/`active` becomes `completed` because it records maintained/agent-produced content, not approval or guaranteed currency. Unknown status values refuse the whole preflight. Migration does not rewrite other project histories. Legacy specs remain historical context, not newly authored intents or binding requirements.

Unmapped root directories/files are reported and left untouched; current `work/`, `reference/`, `learned/`, and `local/` trees are not flattened or moved. The helper moves regular files of any extension, so unsupported non-HTML formats are preserved rather than discarded. Migrating `.html`/`.htm` artifacts converts ordinary headings, paragraphs, lists, links, and code to Markdown and backs up the original bytes under `.lore/local/migration-backups/`. Tables, SVG/complex styled markup remain raw inline HTML where possible. Scripts/styles are preserved only as escaped, inert source and their runtime/rendering behavior is not preserved. Conversion warnings and backup destinations appear in preview; it is conservative, not a promise of complete fidelity. Destination and backup collisions block the entire migration.

The helper rewrites only resolvable Markdown/HTML links and known path-bearing frontmatter fields in `.lore/` documents. Legacy-spec `fg-sources` provenance follows moved specs; `fg-sources` entries for plans/tasks/notes are deliberately not repointed into reference provenance and are reported for field-guide reassessment. It reports external document references but does not edit them. Unresolved literal references must be reviewed; do not claim they were fixed. Local paths may be unavailable to collaborators.

## Workflow

1. Resolve the helper relative to this installed skill directory. Run `python3 <resolved-helper-path> '<project-root>'` for a no-write preview, quoting the actual project-root path for the shell. The preview checks the complete move set for symlinks and collisions and lists reference updates, tracked-file actions, and unresolved references. It creates neither `.lore/local/` nor ignore rules.
2. Explain that moving to `.lore/local/` makes these artifacts machine-local/ignored and that existing users/collaborators may not have them. Ask the user whether to apply this exact preview.
3. Only after the user confirms, rerun with `--apply`. When moving local files, apply ensures `.lore/local/` is effectively Git-ignored before moving any file. If setup fails, stop without moving files.
4. If a local destination source is tracked, normal apply refuses. Explain the exact paths and ask separately whether to stage only their Git index removals. Only if explicitly approved rerun with `--apply --untrack`. The files remain in `.lore/local/`; this option never uses `git rm` on file data and does not stage unrelated changes. Dirty or staged changes to affected tracked sources are a blocker.
5. Report the resulting moves, rewritten references, unresolved references, and any tracked index removals. Ask the user to inspect Git status. Do not stage other changes or run the migration on repository artifacts without the user's explicit request.

## Explain and recover from blockers

Never relay a Python exception as the whole answer or suggest a force/bypass flag. Name the exact path and observed value/condition, explain why that guard stopped migration, and give the matching safe next step. For preflight blockers, state that no migration moves/reference edits began, resolve only the condition, then rerun the no-write preview using the command above. Do not claim an apply failure left the tree unchanged: inspect the reported source, destination, references, `.gitignore`, and Git status first. Offer to help inspect or normalize a document, but ask the user to confirm any content/status edit.

- **Unknown or malformed status:** identify the file and line and quote the observed value/line. Ask what it means; the user must explicitly choose `draft`, `approved`, `completed`, or `archived`. Never infer `approved` from agent work or arbitrary edits. Offer to help make that user-confirmed edit and, if useful, preserve the old value as `legacy_status`. Then rerun preview. Do not choose a status or edit it automatically.
- **Destination or HTML-backup collision:** name source and occupied destination/backup. Compare both contents and their intended ownership; resolve the paths explicitly without overwriting or deleting either automatically, then preview again.
- **Dirty/staged tracked source or reference:** name the path. Inspect both `git -C '<root>' diff -- '<path>'` and `git -C '<root>' diff --cached -- '<path>'`; preserve and intentionally resolve those changes before retrying. Never recommend reset, checkout, or discarding edits.
- **Tracked source needs `--untrack`:** explain that ordinary apply stopped before moving it; `--untrack` stages an index removal for only the listed source path(s), while file bytes remain in `.lore/local/`. Ask for explicit user approval of that narrow index change before suggesting `--apply --untrack`.
- **Symlink/non-regular path:** name the link/path and state migration will not dereference it. Inspect its target/type and decide whether the linked content belongs in the migration; do not replace, follow, or remove it automatically.
- **Ignore setup/negation:** name `.gitignore`/`.lore/local` and inspect the relevant ignore rule with `git -C '<root>' check-ignore -v --no-index .lore/local/.ensure-local-ignore-probe`. Ask before editing a conflicting rule; never force setup. Since setup may append `/.lore/local/` before a later verification failure, inspect `.gitignore` and `git status` rather than claiming no change.
- **Reference permissions:** name the file and reported mode/error. Resolve its ownership/permissions deliberately while preserving contents; do not use `sudo` or blanket `chmod`.
- **HTML encoding:** identify the source path and invalid UTF-8 condition. Keep the original bytes; ask for an explicit encoding/conversion decision or leave that file unmigrated. Do not silently decode lossily.
- **Rollback/recovery error:** quote each unresolved path and recovery error. STOP; do not rerun apply blindly. Manually inspect source/destination/reference files and Git status/staged diff, preserve all remaining content, and decide recovery before any new preview/apply.

If the project root is missing or wrong, show the supplied path and ask for the correct project root (the directory containing `.lore/`).

The helper is idempotent: after a successful run, rerunning it reports no legacy files to move. A collision or unsafe symlink anywhere in the planned source/destination paths blocks the full migration before moves begin. Never work around a blocker by overwriting or deleting a destination.
