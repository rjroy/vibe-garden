---
title: Tend discovery modes - expanding beyond status hygiene
date: 2026-02-04
status: resolved
tags: [tend, discovery, organization, skill-architecture]
modules: [lore-development, tend-skill]
related: [.lore/retros/tend-discovery-expansion.md]
---

# Brainstorm: Tend Discovery Modes

## Context

Running `/tend` on Memory Loop's `.lore/` directory (41 documents) successfully caught stale statuses but surfaced a larger gap: tend addresses accuracy but not discoverability. The retro proposed several extensions, but cramming them all into the existing skill would bloat the prompt.

Core insight from the retro: status hygiene and discovery are orthogonal problems.

## Ideas Explored

### Feature-based directories (rejected)

What if `.lore/` organized by feature instead of document type?

```
.lore/
├── features/
│   └── daily-prep/
│       ├── brainstorm.md
│       ├── spec.md
│       └── retro.md
```

**Why it doesn't work:** Relationships aren't linear. A brainstorm can lead to multiple specs. A spec can have multiple retros. The many-to-many nature breaks the clean hierarchy.

### Filename-based clustering (rejected)

What if tend detected shared prefixes (`vi-mode-*`, `daily-prep-*`) and suggested subdirectories?

**Why it doesn't work:** Assumes files are well-named. They often aren't. Building organization on unreliable foundations creates fragile suggestions.

### Mode-based tend with reference files (promising)

Break tend into focused modes, each with its own reference file:

```
tend/
├── SKILL.md           # Orchestrator: describes flow, invocation patterns
├── references/
│   ├── status.md      # Current tend logic (frontmatter, verification)
│   ├── tags.md        # Tag hygiene
│   ├── filenames.md   # Filename consistency
│   └── directories.md # Directory organization
```

**The dependency chain:**

```
status → tags → filenames → directories
   ↓        ↓         ↓            ↓
accuracy  semantics  findability  navigation
```

Each mode produces inputs the next mode consumes:
- Can't suggest directory groupings until you know what tags cluster together
- Can't suggest better file names until you know what tags the file should surface
- Can't audit tags until you know which documents are actually active vs abandoned

**This follows an existing pattern.** The `ddp` skill already uses `references/mermaid-patterns.md` for domain-specific detail. Tend would follow the same structure.

### Tags as the organizing spine

If `tend: tags` gets tagging right, then `tend: directories` becomes "materialize the tag clusters into the filesystem." Organization emerges from metadata that already exists, not inferred from unreliable file names.

### Each mode has dry-run → confirm → apply

Consistent with current status behavior:
1. Surface findings
2. Wait for confirmation
3. Apply changes

You could stop after any phase or run all four in one session.

## Open Questions

**Invocation patterns:** Should modes be explicitly selectable?

```
/tend              # Run all modes in sequence
/tend status       # Just status verification
/tend tags         # Just tag audit
```

Or is explicit selection over-engineering? Maybe tend always runs sequentially but you can stop after any phase.

**Cross-mode awareness:** If `tags.md` changes tags, should `filenames.md` reload documents to see new tags before suggesting renames? Or does each mode operate on state at invocation time?

**Reference file location:** Reference files live within the skill directory (not in `.lore/` per project, not in shared). This keeps the skill self-contained.

## Next Steps

- Spec the mode-based tend architecture
- Define what each mode actually does (status.md already exists as current SKILL.md)
- Design the SKILL.md orchestrator content
