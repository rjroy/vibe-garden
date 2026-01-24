---
name: synthesize-docs
description: This skill should be used when the user asks to "generate documentation", "create CLAUDE.md", "document the codebase", "synthesize docs", or invokes /spiral-grove:synthesize-docs. Generates operational CLAUDE.md documentation from module implementations.
allowed-tools: Skill(spiral-grove:sdd-format-docs), Task, Read, Write, Glob, Grep, Bash
---

# Documentation Synthesis

Generate operational CLAUDE.md documentation by analyzing module implementations across the project.

## Command Usage

```
/spiral-grove:synthesize-docs           # Full project synthesis
/spiral-grove:synthesize-docs src/auth  # Single module regeneration
```

## Role

Orchestrate the three-phase workflow:
1. **Phase 1: Module Discovery** - Detect modules, get user approval, create manifest
2. **Phase 2: Parallel Generation** - Spawn module-doc-synthesizer agents, generate root CLAUDE.md
3. **Phase 3: SDD Integration** - Link modules to specs if .sdd/specs/ exists

## Phase 1: Module Discovery

### If Scope Provided (e.g., `src/auth`)

1. Validate path exists: `Glob: [scope]/**/*`
2. If no files: Exit with error
3. Create single-module manifest, skip to Phase 2

### If No Scope (Full Project)

**Step 1: Check Resumability**
```
Read: .sdd/module-manifest.json

If exists and valid:
  Count: completed, pending, failed

  If all completed:
    Ask: "All X modules complete. Re-run to regenerate all? [y/n]"
    If yes: Reset all to pending, continue
    If no: Exit

  If pending or failed exist:
    Ask: "Found progress: X completed, Y pending, Z failed. Continue? [y/n]"
    If yes: Skip to Phase 2 (use pending/failed only)
    If no: Exit

If not exists: Continue to Step 2
```

**Step 2: Check Cross-Command Integration**
```
Read: .sdd/spec-manifest.json

If exists:
  Ask: "Found spec manifest from /synthesize-specs. Use it? [y/n]"
  If yes:
    Convert to module-manifest.json format
    Skip to Phase 2
```

**Step 3: Invoke Module Discovery**
```
Task(
  description: "Discover modules in codebase",
  prompt: "Analyze codebase and detect logical module boundaries using all 5 heuristics. Return ranked list with confidence >= 50%. Project root: [pwd]",
  subagent_type: "spiral-grove:module-discovery-agent"
)
```

**Step 4: Present to User**
```
Display agent's module table

Ask: "Approve? Options: yes | add <path> | remove <path> | cancel"

Handle response:
- yes/approve/ok → Continue
- add <path> → Add to list, repeat
- remove <path> → Remove from list, repeat
- cancel/no → Exit
```

**Step 5: Create Manifest**
```
Bash: mkdir -p .sdd
Bash: pwd  # Get project root

Write .sdd/module-manifest.json:
{
  "generated_at": "[ISO 8601 timestamp]",
  "project_root": "[pwd]",
  "modules": [
    {
      "path": "[module path]",
      "status": "pending",
      "claude_md_path": "[path]/CLAUDE.md",
      "error": null
    }
  ]
}
```

## Phase 2: Parallel Documentation Generation

**Step 1: Filter Modules**
```
Read: .sdd/module-manifest.json
Filter: status === "pending" OR status === "failed"
```

**Step 2: Spawn Agents (Batches of 10)**
```
For each batch of 10 modules:

  Send SINGLE message with MULTIPLE Task calls:

  Task(
    description: "Generate CLAUDE.md for [module-name]",
    prompt: "Generate CLAUDE.md for module at path: [module_path]",
    subagent_type: "spiral-grove:module-doc-synthesizer",
    model: "haiku"
  )

  Wait for all agents in batch
```

**Step 3: Update Manifest**
```
For each agent response:

  If contains "CLAUDE.md written":
    modules[i].status = "completed"
    Log: "[path]/CLAUDE.md (XXX lines)"

  Else if contains "ERROR:":
    modules[i].status = "failed"
    modules[i].error = "[error message]"
    Continue (don't stop)

Write: .sdd/module-manifest.json
```

**Step 4: Generate Root CLAUDE.md**
```
Detect project name from package.json/Cargo.toml/go.mod/directory

Build module index from manifest (group by prefix)

Read README.md for getting started (if exists)

Construct root CLAUDE.md with:
- Purpose (from README/package.json)
- Architecture (from directory structure)
- Directory Structure (tree view)
- Modules (linked to CLAUDE.md files)
- Getting Started
- Hand-edited section markers

Write: CLAUDE.md (project root)
```

**Step 5: Display Progress**
```
Output:
## Generation Complete: [successful] / [total] modules

**Successful**: [list paths]
**Failed**: [list paths with errors]
**Root**: CLAUDE.md created at project root
```

## Phase 3: SDD Integration (Optional)

**Step 1: Check for Specs**
```
If .sdd/specs/ doesn't exist:
  Output: "Skipping SDD integration (no .sdd/specs/)"
  Skip to Final Output
```

**Step 2: Match Modules to Specs**
```
For each completed module:
  Try matching to specs:
  a) Exact name match
  b) Hierarchy path match
  c) Fuzzy token overlap >= 70%
```

**Step 3: Insert Origin Fields**
```
For each matched module:
  Insert after title:
  **Origin**: Implemented from [spec-path]
```

**Step 4: Report**
```
Output:
## SDD Integration Complete: [linked] / [total]

**Linked**: [list "module → spec"]
**Unlinked**: [list paths] (expected for utilities)
```

## Final Output

```
Documentation Synthesis Complete

**Generated Files**:
- 1 root CLAUDE.md
- [count] module CLAUDE.md files

**Status Breakdown**:
- Completed: [count] modules
- Failed: [count] modules

[If SDD integration ran:]
**SDD Integration**:
- Linked: [count]
- Unlinked: [count]

**Manifest**: .sdd/module-manifest.json
```

## Error Handling

| Error | Action |
|-------|--------|
| No modules detected | Exit, suggest manual path |
| Invalid module path | Exit with error |
| Agent failure | Continue, report in final output |
| Manifest corruption | Prompt to regenerate |

## Key Points

- **Framework-agnostic**: Works on any codebase
- **Batching**: Max 10 parallel agents
- **Resumability**: Manifest tracks progress
- **Hand-edits**: Preserved between `<!-- BEGIN/END: HAND-EDITED -->` markers
- **Cross-command**: Can import from /synthesize-specs
