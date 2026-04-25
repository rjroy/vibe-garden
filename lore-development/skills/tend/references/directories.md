# Directories Mode Reference

Audit directory organization and suggest structural improvements.

## Purpose

Directory structure shapes navigation. The `.lore/` tree is partitioned into three top-level zones (`build/`, `reference/`, `learned/`). Each zone has a defined purpose; documents drift between zones as they mature. This mode keeps the partitioning honest and identifies structural improvements within each zone.

## The Three Zones

`.lore/` always holds three top-level directories. Everything else is either a subdirectory of one of these or a legacy orphan to migrate.

```
.lore/
├── build/        # Work scaffolding: in-flight thinking and plans
├── reference/    # Solidified knowledge: what callers can rely on
└── learned/      # Mistakes-only: lessons worth remembering
```

**`build/`** is for documents tied to an active work cycle (specs, plans, tasks, brainstorms, research, retros, issues, design notes, diagrams). Documents here churn.

**`reference/`** is for documents that have stabilized into shared knowledge (vision, project briefings, glossaries, durable diagrams). Callers cite this, so updates are deliberate.

**`learned/`** is mistakes-only. Each entry names a mistake, names the remedy, and stays terse. Successes do not belong here.

## Standard Structure

**Build subtree** (work scaffolding):
```
.lore/build/
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

The first sweep is partition discipline. Anything outside `build/`, `reference/`, `learned/` is a legacy orphan or a registered custom directory. Treat these as primary findings.

| Signal | Action |
|--------|--------|
| Top-level directory not in `{build, reference, learned}` and not in `custom_directories` | Flag as legacy orphan; recommend `/tend migrate` to route into the right zone |
| Document in `build/` whose status is terminal and content has stabilized | Candidate for promotion to `reference/` |
| Document in `reference/` whose status is `outdated` for an extended period | Candidate for refresh or archive |
| `learned/` entry that doesn't name a mistake | Flag for rewrite; learned is mistakes-only |

**Common legacy orphans** (from the pre-redesign layout):
`brainstorm/`, `specs/`, `design/`, `plans/`, `tasks/`, `notes/`, `research/`, `retros/`, `issues/`, `ideas/`, `validation/`, `stubs/`, `excavations/`, `diagrams/`. All of these now live under `build/` (or have been folded into `reference/learned/`). Route via `/tend migrate`.

`_archive/` is a separate concern: it is the historical default name for an out-of-tree archive directory. If a project relied on the old default, see `lore-config.md` for how to register it via `archive_directory`. It is not a redesign legacy.

### Size Threshold

Directories with 8+ files should be evaluated for subdivision:

```
.lore/build/specs/        # 12 files - consider splitting
├── auth-flow.md
├── auth-oauth.md
├── auth-session.md       # Auth cluster (3)
├── api-rest.md
├── api-graphql.md        # API cluster (2)
├── payment-stripe.md
├── payment-flow.md       # Payment cluster (2)
└── ... 5 more
```

**8 is a threshold, not a rule.** A directory with 10 tightly-related specs might be fine. A directory with 6 unrelated documents might need splitting.

### Subdirectory Suggestions

Use tag clusters (from tags mode) to suggest subdivisions:

1. Identify documents in oversized directory
2. Group by shared tags (3+ documents sharing 2+ tags = candidate cluster)
3. Suggest subdirectory per cluster

Example suggestion:
```
.lore/build/specs/
├── auth/
│   ├── auth-flow.md
│   ├── auth-oauth.md
│   └── auth-session.md
├── api/
│   ├── api-rest.md
│   └── api-graphql.md
├── payment/
│   ├── payment-stripe.md
│   └── payment-flow.md
└── [remaining unclustered files]
```

**Don't over-nest.** Two levels under a zone is usually enough. Deep nesting trades one navigation problem for another.

### Archive Candidates

Identify documents that could move to archive:

| Signal | Example |
|--------|---------|
| Status: superseded | Old spec replaced by newer version |
| Status: archived not yet moved | Stale entry in active subtree |
| Status: implemented + related retro exists | Feature cycle finished |
| No modifications in 90+ days + status: parked | Abandoned ideas |
| Explicit archive tag | User marked for archival |

Archive location: defaults to the `archived` status in place, or the directory named by `archive_directory` in `.lore/lore-config.md` if configured. Some projects use domain-specific names that serve the same purpose.

**Don't auto-archive.** Present candidates and let user decide.

### Orphan Detection

Within a zone, find subdirectories that exist but serve no clear purpose:

- Empty directories
- Directories with only one file (should file move up?)
- Directories not in the standard structure or `custom_directories`

Note on raw idea capture: if the project uses an `/idea` hook that writes to a queue file (e.g., `.lore/build/ideas/`), those files are plain markdown without frontmatter. They are queues, not lore documents. Tend should not flag them for missing frontmatter, and lore-researcher should not search them.

Non-standard directories aren't wrong, but should be intentional. When the user confirms a flagged directory as intentional, record it for the config suggestion step so it's recognized on the next run.

## Output Report

```markdown
## Directories Report

### Zone Discipline
| Path | Issue | Suggested Action |
|------|-------|------------------|
| .lore/specs/ | Legacy top-level (pre-redesign) | Run /tend migrate -> .lore/build/specs/ |
| .lore/build/specs/old-auth.md | status: superseded | Archive or remove |
| .lore/learned/win-story.md | Not a mistake entry | Rewrite or move to reference/ |

### Oversized Directories
| Directory | Files | Suggested Subdivision |
|-----------|-------|----------------------|
| build/specs/ | 12 | auth/, api/, payment/ |
| build/brainstorm/ | 9 | Consider by theme |

### Archive Candidates
| File | Reason | Last Modified |
|------|--------|---------------|
| build/specs/old-auth.md | status: superseded | 60 days ago |
| build/plans/v1-migration.md | implemented + retro exists | 45 days ago |

### Orphan Directories
| Directory | Issue |
|-----------|-------|
| .lore/temp/ | Outside the three zones, 2 files |
| .lore/build/specs/legacy/ | Empty |

### Suggested Moves
| File | From | To | Reason |
|------|------|-------|--------|
| auth-flow.md | build/specs/ | build/specs/auth/ | Cluster with 2 others |
```

## Applying Changes

**Directory restructuring requires careful execution**:

1. Present full restructuring plan
2. Show all file moves and their dependency updates
3. On confirmation:
   - Create new directories
   - Move files
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
