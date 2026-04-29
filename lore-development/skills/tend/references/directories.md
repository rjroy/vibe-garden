# Directories Mode Reference

Audit directory organization and suggest structural improvements.

## Purpose

Directory structure shapes navigation. The `.lore/` tree is partitioned into three top-level zones (`work/`, `reference/`, `learned/`). Each zone has a defined purpose; documents drift between zones as they mature. This mode keeps the partitioning honest and identifies structural improvements within each zone.

## The Three Zones

`.lore/` always holds three top-level directories. Everything else is either a subdirectory of one of these or a legacy orphan to migrate.

```
.lore/
├── work/        # Work scaffolding: in-flight thinking and plans
├── reference/    # Solidified knowledge: what callers can rely on
└── learned/      # Mistakes-only: lessons worth remembering
```

**`work/`** is for documents tied to an active work cycle (specs, plans, tasks, brainstorms, research, retros, issues, design notes, diagrams). Documents here churn.

**`reference/`** is for documents that have stabilized into shared knowledge (vision, project briefings, glossaries, durable diagrams). Callers cite this, so updates are deliberate.

**`learned/`** is mistakes-only. Each entry names a mistake, names the remedy, and stays terse. Successes do not belong here.

## Standard Structure

**Build subtree** (work scaffolding):
```
.lore/work/
├── brainstorm/   # Ideas and exploration
├── specs/        # Requirements and definitions
├── design/       # Technical decisions
├── plans/        # Implementation plans
├── tasks/        # Plan execution tasks
├── notes/        # Implementation notes
├── research/     # External context
├── retros/       # Retrospective notes
├── issues/       # Tracked issues
└── diagrams/     # Visual documentation tied to active work
```

**Reference subtree** (solidified):
```
.lore/reference/
├── vision.md     # Project vision (when present)
├── diagrams/     # Durable visual documentation
└── ...           # Other stabilized knowledge
```

**Learned subtree** (mistakes-only):
```
.lore/learned/
└── ...           # Terse entries naming mistake + remedy
```

**Project-specific directories**: If `.lore/lore-config.md` exists, directories listed in `custom_directories` are treated as standard alongside the structure above. They won't be flagged as orphans. The config's `archive_directory` value (if set) controls archive location.

## Checks

### Zone Discipline

The first sweep is partition discipline. Anything outside `work/`, `reference/`, `learned/` is a legacy orphan or a registered custom directory. Treat these as primary findings.

| Signal | Action |
|--------|--------|
| Any of the 14 legacy top-level directories or `.lore/vision.md` is present | Emit "**legacy structure detected; run `/tend migrate`**" as the first finding and stop further per-directory analysis until migration completes |
| Top-level directory not in `{work, reference, learned}` and not in `custom_directories` (and not a known legacy name) | Flag as orphan; ask whether to register in `custom_directories` |
| Document in `work/` whose status is terminal and content has stabilized | Candidate for promotion to `reference/` |
| Document in `reference/` whose status is `outdated` for an extended period | Candidate for refresh or archive |
| `learned/` entry that doesn't name a mistake | Flag for rewrite; learned is mistakes-only |

**Legacy top-levels** (from the pre-redesign layout):
`brainstorm/`, `specs/`, `design/`, `plans/`, `tasks/`, `notes/`, `research/`, `retros/`, `issues/`, `ideas/`, `validation/`, `stubs/`, `excavations/`, `diagrams/`, plus the file `vision.md`.

When any of these are detected, the directories report should lead with the legacy banner and route the user to `/tend migrate`. Other findings still apply to documents already inside `work/`, `reference/`, `learned/`, but reorganizing inside legacy directories is wasted work — they are about to move.

`_archive/` is a separate concern: it is the historical default name for an out-of-tree archive directory. If a project relied on the old default, see `lore-config.md` for how to register it via `archive_directory`. It is not a redesign legacy.

### Size Threshold

Directories with 8+ files are flagged for evaluation. Tend does not author subdivision plans inline; routing keeps tend in its hygiene-pass role and concentrates reorganization decisions (layer model, index authoring, cross-reference verification) in one place.

| Zone | Action when oversized |
|------|----------------------|
| `reference/`, `learned/`, or any custom stable subtree | Surface as a candidate for `/lore-development:progressive-discovery <path>`. That skill owns layered reorganization and writes the navigational index. |
| `work/` | Note the count but propose no fix. Work churns and gets archived; reorganization rarely pays off before the directory empties. The exception is a stalled work subdirectory that has hardened into de facto reference — recommend `/lore-development:distill work <path>` first, then re-evaluate the resulting `reference/` directory. |

**8 is a threshold, not a rule.** A directory with 10 tightly-related specs might be fine. A directory with 6 unrelated documents might warrant a closer look.

### Archive Candidates

Identify documents that could move to archive:

| Signal | Example | Notes |
|--------|---------|-------|
| Status: superseded | Old spec replaced by newer version | |
| Status: archived not yet moved | Stale entry in active subtree | |
| Status: implemented (spec) | Feature cycle finished | **Run distill-before-archive soft prompt** before archiving (see "Applying Changes" below) |
| Status: implemented + related retro exists | Feature cycle finished, retro captured | Same soft prompt applies to the spec |
| No modifications in 90+ days + status: parked | Abandoned ideas | |
| Explicit archive tag | User marked for archival | |

Archive location: defaults to the `archived` status in place, or the directory named by `archive_directory` in `.lore/lore-config.md` if configured. Some projects use domain-specific names that serve the same purpose.

**Don't auto-archive.** Present candidates and let user decide.

**Distill-before-archive coupling**: any spec with `status: implemented` surfaced as an archive candidate must trigger the soft prompt described in `tend/SKILL.md` ("Distill-Before-Archive") before it is archived. This is the only place in `directories` where a per-file prompt fires inside the apply flow. Archiving without the prompt silently loses the reference-promotion opportunity captured by `/distill work <spec>`. See `lore-development/skills/distill/SKILL.md` for the distill flow.

### Orphan Detection

Within a zone, find subdirectories that exist but serve no clear purpose:

- Empty directories
- Directories with only one file (should file move up?)
- Directories not in the standard structure or `custom_directories`

Note on raw idea capture: if the project uses an `/idea` hook that writes to a queue file (e.g., `.lore/work/ideas/`), those files are plain markdown without frontmatter. They are queues, not lore documents. Tend should not flag them for missing frontmatter, and lore-researcher should not search them.

Non-standard directories aren't wrong, but should be intentional. When the user confirms a flagged directory as intentional, record it for the config suggestion step so it's recognized on the next run.

## Output Report

```markdown
## Directories Report

### Zone Discipline
**Legacy structure detected; run `/tend migrate`** (when any pre-redesign layout is present)

| Path | Issue | Suggested Action |
|------|-------|------------------|
| .lore/specs/ | Legacy top-level (pre-redesign) | Run /tend migrate -> .lore/work/specs/ |
| .lore/vision.md | Legacy file (pre-redesign) | Run /tend migrate -> .lore/reference/vision.md |
| .lore/work/specs/old-auth.md | status: superseded | Archive or remove |
| .lore/learned/win-story.md | Not a mistake entry | Rewrite or move to reference/ |

### Oversized Directories
| Directory | Files | Suggested Action |
|-----------|-------|------------------|
| reference/ | 14 | Run `/lore-development:progressive-discovery reference/` |
| learned/ | 11 | Run `/lore-development:progressive-discovery learned/` |
| work/specs/ | 12 | Note only; work zone churns |

### Archive Candidates
| File | Reason | Last Modified |
|------|--------|---------------|
| work/specs/old-auth.md | status: superseded | 60 days ago |
| work/plans/v1-migration.md | implemented + retro exists | 45 days ago |

### Orphan Directories
| Directory | Issue |
|-----------|-------|
| .lore/temp/ | Outside the three zones, 2 files |
| .lore/work/specs/legacy/ | Empty |

```

Subdivision moves are not part of tend's output. When the Oversized Directories table recommends progressive-discovery, hand off — tend does not author the plan or execute the moves.

## Applying Changes

**Directory restructuring requires careful execution**:

1. Present full restructuring plan
2. Show all file moves and their dependency updates
3. **For each archive candidate that is a spec with `status: implemented`**, run the distill-before-archive soft prompt from `tend/SKILL.md` (yes / no / skip):
   - **yes**: pause this file's archive step and suggest `/distill work <path-to-spec>`. After the user runs distill (or declines mid-distill), return to the archive confirmation for this file.
   - **no**: proceed with archiving as proposed.
   - **skip**: drop this file from the current archive batch; leave it in place for this run.
   This prompt is soft; the user retains agency to archive without distilling. Do not block the broader restructuring on the distill outcome.
4. On confirmation of the remaining plan:
   - Create new directories
   - Move files (including any archive moves the user accepted in step 3)
   - Update all `related:` paths
   - Update all markdown links
   - Remove empty old directories

**Batch operations**:
- All moves in a restructuring are atomic (all or none)
- Create directories before moving files
- Update references after moves complete
- Report final structure

## Progressive Discovery

Directories mode works in passes:

1. **Scan pass**: Inventory all directories and file counts; check zone partitioning first
2. **Analysis pass**: Apply thresholds, detect clusters, find orphans, flag legacy top-levels
3. **Report pass**: Present categorized findings with suggestions
4. **Apply pass**: Execute confirmed restructuring (route legacy orphans via `/tend migrate`)

Use TaskCreate for each pass.

## Re-scan After Changes

After completing directories mode, the tag and filename indices may need refreshing (file paths changed). The orchestrator handles this by re-scanning between modes when running sequentially.
