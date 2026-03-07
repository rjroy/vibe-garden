# Directories Mode Reference

Audit directory organization and suggest structural improvements.

## Purpose

Directory structure shapes navigation. When directories grow too large or contain unrelated documents, finding things becomes harder. This mode identifies structural improvements.

## Checks

### Size Threshold

Directories with 8+ files should be evaluated for subdivision:

```
.lore/specs/          # 12 files - consider splitting
├── auth-flow.md
├── auth-oauth.md
├── auth-session.md   # Auth cluster (3)
├── api-rest.md
├── api-graphql.md    # API cluster (2)
├── payment-stripe.md
├── payment-flow.md   # Payment cluster (2)
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
.lore/specs/
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

**Don't over-nest.** Two levels is usually enough. Deep nesting trades one navigation problem for another.

### Archive Candidates

Identify documents that could move to archive:

| Signal | Example |
|--------|---------|
| Status: superseded | Old spec replaced by newer version |
| Status: complete + related retro exists | Feature cycle finished |
| No modifications in 90+ days + status: parked | Abandoned ideas |
| Explicit archive tag | User marked for archival |

Archive location: `.lore/_archive/` by default, or the value of `archive_directory` in `.lore/lore-config.md` if configured. Some projects use domain-specific names (e.g., `_abandoned/`) that serve the same purpose.

**Don't auto-archive.** Present candidates and let user decide.

### Orphan Detection

Find directories that exist but serve no clear purpose:

- Empty directories
- Directories with only one file (should file move up?)
- Directories not matching standard `.lore/` structure

### Standard and Custom Directories

**Default standard structure** (from frontmatter schema):
```
.lore/
├── brainstorm/    # Ideas and exploration
├── specs/         # Requirements and definitions
├── plans/         # Implementation plans
├── design/        # Technical decisions
├── research/      # External context
├── retros/        # Lessons learned
├── diagrams/      # Visual documentation
├── reference/     # Excavated features
├── excavations/   # Excavation index
├── issues/        # Tracked issues (lore documents with frontmatter)
├── ideas/         # Raw idea capture (NOT lore documents, see note)
└── _archive/      # Completed/superseded work
```

**Project-specific directories**: If `.lore/lore-config.md` exists, directories listed in `custom_directories` are treated as standard alongside the defaults above. They won't be flagged as orphans. The config's `archive_directory` value (if set) replaces `_archive/` in this list.

**Note on `.lore/ideas/`**: This directory holds raw captures from the `/idea` hook. Files are plain markdown with a date header and bullet list, no frontmatter. They are queues, not lore documents. Tend should not flag ideas files for missing frontmatter, and lore-researcher should not search them.

Non-standard directories aren't wrong, but should be intentional. When the user confirms a flagged directory as intentional, record it for the config suggestion step so it's recognized on the next run.

## Output Report

```markdown
## Directories Report

### Oversized Directories
| Directory | Files | Suggested Subdivision |
|-----------|-------|----------------------|
| specs/ | 12 | auth/, api/, payment/ |
| brainstorm/ | 9 | Consider by theme |

### Archive Candidates
| File | Reason | Last Modified |
|------|--------|---------------|
| specs/old-auth.md | status: superseded | 60 days ago |
| plans/v1-migration.md | complete + retro exists | 45 days ago |

### Orphan Directories
| Directory | Issue |
|-----------|-------|
| .lore/temp/ | Non-standard, 2 files |
| .lore/specs/legacy/ | Empty |

### Suggested Moves
| File | From | To | Reason |
|------|------|-------|--------|
| auth-flow.md | specs/ | specs/auth/ | Cluster with 2 others |
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

1. **Scan pass**: Inventory all directories and file counts
2. **Analysis pass**: Apply thresholds, detect clusters, find orphans
3. **Report pass**: Present categorized findings with suggestions
4. **Apply pass**: Execute confirmed restructuring

Use TaskCreate for each pass.

## Re-scan After Changes

After completing directories mode, the tag and filename indices may need refreshing (file paths changed). The orchestrator handles this by re-scanning between modes when running sequentially.
