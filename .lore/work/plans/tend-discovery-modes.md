---
status: executed
---

# Plan: Tend Skill Mode-Based Architecture

## Summary

Refactor `/tend` from a monolithic 222-line skill into a mode-based architecture with four sequential modes. Each mode lives in its own reference file; SKILL.md becomes a lean orchestrator.

## Context

- **Retro**: `.lore/work/retros/tend-discovery-expansion.md` - Discovery ≠ accuracy; both needed
- **Brainstorm**: `.lore/work/brainstorm/tend-discovery-modes.md` - Four modes, dependency chain, tags as organizing spine
- **Pattern**: `ddp` skill uses `references/mermaid-patterns.md` (~150 lines)
- **Guide**: Skill Development says SKILL.md should be 1,500-2,000 words, detailed content in references/

## Architecture

```
tend/
├── SKILL.md                    # Orchestrator (~50 lines)
└── references/
    ├── status.md               # Extracted from current SKILL.md
    ├── tags.md                 # New: tag hygiene
    ├── filenames.md            # New: filename consistency
    └── directories.md          # New: directory organization
```

**Dependency chain:**
```
status → tags → filenames → directories
   ↓        ↓         ↓            ↓
accuracy  semantics  findability  navigation
```

## Invocation Pattern

```
/tend                    # Run all modes sequentially (pause between each)
/tend status             # Run only status mode
/tend tags               # Run only tags mode
/tend filenames          # Run only filenames mode
/tend directories        # Run only directories mode
```

Default `/tend` pauses after each mode: "Status complete. Continue to tags?" User can stop after any mode.

## Implementation Steps

### 1. Create references/ directory
```bash
mkdir -p lore-development/skills/tend/references
```

### 2. Extract status.md from current SKILL.md

Move these sections to `references/status.md`:
- Status Values (keep link to frontmatter-schema.md)
- Verification Approach (all document-type-specific checks)
- Honest Status guidance
- Progressive Discovery / task tracking for status mode
- Output report format
- Prefix collision detection
- Frontmatter Retrofitting
- Adding Status to Documents

Keep in SKILL.md:
- When to Use (update for modes)
- Common dry-run → confirm → apply pattern
- Mode routing table

### 3. Create tags.md (~80 lines)

New content:
- Tag consistency checks (similar tags that should unify)
- Related links audit (documents sharing 3+ tags but no link)
- Tag clusters (natural groupings)
- Output report format
- Apply changes guidance

### 4. Create filenames.md (~70 lines)

New content:
- Convention consistency (kebab-case, date formats)
- Tag-informed naming suggestions
- Collision detection
- Batch rename with dependency updates

### 5. Create directories.md (~80 lines)

New content:
- Size threshold (8+ files triggers suggestion)
- Subdirectory suggestions based on tag clusters
- Archive candidates (completed feature cycles)
- Orphan detection

### 6. Rewrite SKILL.md as orchestrator (~80 lines)

Structure:
```markdown
---
name: tend
description: [Updated with mode triggers]
---

# Tend

## Modes

[Table: mode | purpose | produces]

## Invocation

[Examples with arguments]

## Common Pattern

Dry-run → confirm → apply (all modes follow this)

## Running a Mode

[Routing table: mode → reference file path]
[Re-scan guidance between modes]

## Sequential Execution

[Pause-and-confirm flow for default /tend]

## Task Tracking

[Brief guidance, same for all modes]
```

## Files to Modify

| File | Action |
|------|--------|
| `lore-development/.claude-plugin/plugin.json` | Bump version (1.1.0 → 1.2.0) |
| `lore-development/skills/tend/SKILL.md` | Rewrite as orchestrator |
| `lore-development/skills/tend/references/status.md` | Create (extract from SKILL.md) |
| `lore-development/skills/tend/references/tags.md` | Create (new) |
| `lore-development/skills/tend/references/filenames.md` | Create (new) |
| `lore-development/skills/tend/references/directories.md` | Create (new) |

## Patterns to Reuse

- **Reference routing**: From `ddp/SKILL.md` line 144-145
- **Invocation with arguments**: From `excavate/SKILL.md` lines 22-29
- **Frontmatter schema reference**: `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`

## Verification

1. Run `/tend status` - should match current behavior exactly
2. Run `/tend tags` - should audit tags and related links
3. Run `/tend filenames` - should suggest naming improvements
4. Run `/tend directories` - should suggest organization when warranted
5. Run `/tend` - should execute all modes with pause points
6. Test on Memory Loop's `.lore/` (41 documents) to validate at scale
