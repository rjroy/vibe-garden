---
name: tend
description: "This skill performs periodic hygiene on the .lore/ directory through four modes: status (verify/update document status), tags (unify tags, find connections), filenames (convention consistency, rename suggestions), directories (structure optimization). Use when documents have accumulated, status fields are stale, or organization needs attention. Triggers include \"tend the lore\", \"check document status\", \"lore hygiene\", \"what's stale\", \"review lore health\", \"tag audit\", \"organize lore\"."
---

# Tend

Maintain hygiene across `.lore/` documents through four sequential modes.

## Config Loading

Before any mode, check for `.lore/lore-config.md`. If it exists, read it and use its frontmatter to inform all subsequent checks. See `references/lore-config.md` for the config format and how each mode uses it.

If no config exists, use defaults from `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Non-standard patterns will be flagged as findings (not errors) and feed into the config suggestion step at the end.

## Modes

| Mode | Purpose | Produces |
|------|---------|----------|
| `status` | Verify and update document status fields | Accuracy: documents reflect reality |
| `tags` | Unify variants, find connections, identify clusters | Semantics: tags are consistent and meaningful |
| `filenames` | Check conventions, suggest renames based on content | Findability: names match content |
| `directories` | Suggest subdivision, archive candidates, detect orphans | Navigation: structure serves scale |

**Dependency chain**: status → tags → filenames → directories

Each mode builds on prior work. Status must be accurate before tag analysis is meaningful. Tags inform filename suggestions. Tag clusters inform directory suggestions.

## Invocation

```
/tend                    # Run all modes sequentially (pause between each)
/tend status             # Run only status mode
/tend tags               # Run only tags mode
/tend filenames          # Run only filenames mode
/tend directories        # Run only directories mode
```

## Common Pattern

All modes follow dry-run → confirm → apply:

1. **Scan**: Gather information without changing anything
2. **Report**: Present findings in categorized format
3. **Confirm**: Wait for user decisions on proposed changes
4. **Apply**: Make confirmed changes and report final state

Never skip confirmation for changes to existing content.

## Running a Mode

Load the appropriate reference file for detailed guidance:

| Mode | Reference |
|------|-----------|
| config | `references/lore-config.md` |
| status | `references/status.md` |
| tags | `references/tags.md` |
| filenames | `references/filenames.md` |
| directories | `references/directories.md` |

Each reference defines: checks to perform, output report format, how to apply changes.

## Sequential Execution

When running `/tend` without arguments, execute modes in order with pauses:

1. Run status mode to completion
2. Ask: "Status complete. Continue to tags?"
3. On confirmation, run tags mode
4. Ask: "Tags complete. Continue to filenames?"
5. On confirmation, run filenames mode
6. Ask: "Filenames complete. Continue to directories?"
7. On confirmation, run directories mode
8. Present final summary

User can stop after any mode. The pause allows them to absorb findings before proceeding.

**Re-scan between modes**: After filenames or directories mode makes changes, paths may have changed. Re-scan `.lore/` before the next mode to pick up new state.

## Config Suggestion

After completing all requested modes (or when the user stops), check whether any findings were dismissed as intentional during this run. If so, offer to write or update `.lore/lore-config.md` so those patterns aren't flagged next time.

See `references/lore-config.md` for what gets suggested and when to skip.

This step only fires when there's something to suggest. If the project's config already covers everything, or nothing non-standard was found, skip silently.

## Task Tracking

Use `TaskCreate` to make tending visible and structured:

```
TaskCreate: "Scan .lore/ for [mode-specific findings]"
TaskCreate: "Present [mode] findings"
TaskCreate: "Get user decisions"
TaskCreate: "Apply confirmed updates"
```

Mark tasks `in_progress` before starting, `completed` when done. Task boundaries force deliberate pacing through each phase.

**Why this matters**:
- Rushing through phases causes missed documents
- Each mode requires different analysis; collapsing them loses thoroughness
- A task marked complete is a claim that the work was done properly

## When to Use

- Documents have accumulated and status is unclear
- Before starting new work, to understand what's active
- Periodically, to keep lore healthy
- When something feels "off" about the project state
- After completing a feature cycle (good time to archive)
- When search isn't finding documents you know exist (tag/naming issues)
