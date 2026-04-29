---
name: stratify
description: Reorganizes a flat `.lore/` directory of stable docs (typically `reference/` or `learned/`) into dependency-ordered subdirectories with a top-level index, so a reader can drill from "what is this" down to specific detail without reading everything. Use when a single directory has accumulated enough docs that "all in one place" hinders navigation, when readers can't tell where to start, or when `/tend directories` flags an oversized stable directory. Triggers include "stratify", "layer this directory", "split this directory into categories", "rearrange for progressive discovery", "too many files in one directory", "no clear entry point", "where do I start reading".
---

# Stratify

Take a flat directory of stable lore (`.lore/reference/`, `.lore/learned/`, or any project-specific stable subtree) and reorganize it into layered subdirectories so a reader can drill from "what is this" down to specific detail without reading everything.

This skill is the structural-fix counterpart to `/lore-development:tend directories`. Tend flags oversized stable directories during its hygiene pass. Progressive-discovery is what you run when the fix is a layered reorganization with a load-bearing index.

## When this fits

- A `.lore/reference/` or `.lore/learned/` directory has accumulated roughly 10+ docs at one level.
- Files cover overlapping but distinguishable concerns that sort into a dependency direction.
- Readers ask "where do I start?" and there's no obvious answer.
- Cross-doc references exist but the dependency direction is implicit.

If the directory has fewer than ~10 files or every file covers the same concern, do not split. Subdirectories with one or two files create more friction than they save.

`.lore/work/` subdirectories rarely need this treatment. Work churns and gets archived; the navigation pain doesn't last long enough to justify reorganization. If a work subdirectory has stalled and turned into de facto reference, distill it first (`/lore-development:distill work <path>`) so the reorganization happens in `reference/`.

## The shape of the result

Docs sort into **layers** where each layer depends on the one below it. The layer names come from your content's actual dependency direction, not from a fixed template. Two layers is fine; six is suspicious. Three to five is typical.

Directory names should be the layer names, not numbered prefixes. `architecture/` reads better than `01-foundation/`. The reading order belongs in the index, not the directory name.

### Two illustrative shapes

**Shape A — system layering** (architectural reference, e.g. `.lore/reference/` of a codebase whose docs describe a running system):

1. **`architecture/`** — what the system *is*. Process model, data primitives, repository structure.
2. **`surfaces/`** — how anything reaches the system. Clients, routes, UIs, public APIs.
3. **`activities/`** (or `orchestration/`) — the long-running flows the system manages.
4. **`workers/`** (or `components/`) — who or what does the work.
5. **`services/`** — background subsystems that run out-of-band.

**Shape B — abstraction-depth layering** (lessons or learned-style content, e.g. `.lore/learned/`):

1. **`principles/`** — broad posture and verification habits that apply outside this project.
2. **`process/`** — workflow discipline that depends on those principles being held.
3. **`practices/`** — engineering tactics applied during specific implementation work.

A new entry lands one layer above its highest dependency. Both shapes embody the same rule.

Pick the shape that matches what your content actually documents. If neither fits, name your own layers from the content's dependency direction. The shapes above are illustrative, not prescriptive.

## Process

### 1. Survey

`ls` the target directory. Get a line count per file (`wc -l <dir>/*.md`) — wildly different sizes hint at distinct concerns.

Read every file. Skim is fine; you need the topic and the cross-references, not memorized content. Note for each file:

- The dominant concern (what subsystem, lifecycle stage, or abstraction level does it document?).
- Outbound references to other files in the directory.
- Whether it's foundational (other docs depend on it) or leaf-level (nothing else depends on it).

### 2. Group

Sort files into 3–5 layers using the dependency rule: a file goes one layer above its highest dependency.

When grouping is ambiguous, prefer the layer where a reader would *look for* the doc, not the layer that's technically most accurate. The reader's mental model wins over strict dependency hierarchy.

Aim for 3–5 files per layer. A single-file layer is a smell — fold it into an adjacent one.

### 3. Verify cross-references

Grep the directory for `\.md` mentions. Determine whether references are:

- **Bare prose mentions** (`see foo.md`) — survive any move; readers grep by filename.
- **Markdown links** (`[X](foo.md)`) — break when paths change.

Lore-development convention favors bare-name references for exactly this reason. If the directory already follows that convention, leave references alone. If markdown links exist and are load-bearing, plan to update them after the move.

### 4. Move

Create subdirectories. `git mv` each file to its new home. Use `git mv` (not plain `mv`) so rename detection survives in history — a future `git log --follow` works.

Batch moves into one commit's worth of work. Don't reorganize halfway.

### 5. Write the index

Create `README.md` at the top of the reorganized directory. The index is the load-bearing artifact — without it, the directories are just nested storage.

Open with standard lore frontmatter:

```yaml
---
title: <Directory> Index
date: <today>
status: current
tags: [reference, index, navigation]   # adjust tags for the directory's role
---
```

Index content:

- **Reading order**: one paragraph per layer, in dependency order, with "start here if…" guidance for each.
- **Layer dependencies**: state explicitly which layers depend on which. This is the rule that future moves must preserve.
- **What each directory holds**: bullet list per layer with a one-line description of every file. The description should answer "why would I open this" not "what's in this."
- **Conventions**: frontmatter expectations, cross-reference style, status discipline.

Keep the index under ~150 lines. If it grows past that, the reorganization has too many layers.

### 6. Verify

`find <dir> -type f` and confirm every file landed in a layer. `git status` and confirm rename detection caught the moves (look for "renamed:" not "deleted:" + "new file:").

Don't claim the reorganization is done until the index exists and reads cleanly top-to-bottom.

## Anti-patterns

- **Numbered directories** (`01-foundation/`, `02-surfaces/`). Forces a reading order that should live in the index. Renaming is also painful when a layer gets inserted between two others.
- **Single-file directories**. If a layer has one file, it isn't a layer. Fold it.
- **Topic-based grouping disguised as layering**. "Each feature gets its own directory" isn't layering — it's just nested topics. Layers come from dependency direction, not subject matter.
- **Skipping the index**. The directories are infrastructure; the index is the doc. Without it, readers face the same "where do I start" problem one level deeper.
- **Reorganizing without reading**. Pattern-matching on filenames produces incoherent groupings. Read the files.
- **Reorganizing churning directories**. `.lore/work/` subdirectories aren't stable enough for this treatment.

## Done means

- Subdirectories exist and reflect dependency layers.
- Every file is in exactly one layer.
- The index reads top-to-bottom and tells a reader where to start.
- Index frontmatter matches lore conventions (`title`, `date`, `status`, `tags`).
- Cross-references still resolve (bare names grep cleanly; markdown links updated if they existed).
- `git status` shows renames, not delete+create pairs.
