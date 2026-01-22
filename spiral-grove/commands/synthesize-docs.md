---
argument-hint: "[scope]"
description: Generate operational CLAUDE.md documentation from implementation
allowed-tools: Skill(spiral-grove:sdd-format-docs), Task, Read, Write, Glob, Grep, Bash
---

# Documentation Synthesis Mode

Generate operational CLAUDE.md documentation by analyzing module implementations across the project.

## Command Usage

```
/spiral-grove:synthesize-docs           # Full project synthesis
/spiral-grove:synthesize-docs src/auth  # Single module regeneration
```

## Your Role

You orchestrate the three-phase workflow:
1. **Phase 1: Module Discovery** - Detect modules, get user approval, create manifest
2. **Phase 2: Parallel Generation** - Spawn module-doc-synthesizer agents, generate root CLAUDE.md
3. **Phase 3: SDD Integration** - Link modules to specs if .sdd/specs/ exists

## Phase 1: Module Discovery

### If scope provided (e.g., `src/auth`):
1. Validate path exists: `Glob: [scope]/**/*`
2. If no files: Exit with error
3. Create single-module manifest, skip to Phase 2

### If no scope (full project):

**Step 1: Check for Resumability**
```
Read: .sdd/module-manifest.json

If exists and valid:
  Count statuses: completed, pending, failed

  If all completed:
    Ask: "All X modules complete. Re-run to regenerate all? [y/n]"
    If yes: Reset all to pending, continue
    If no: Exit

  If pending or failed exist:
    Ask: "Found progress: X completed, Y pending, Z failed. Continue? [y/n]"
    If yes: Skip to Phase 2 (use pending/failed modules only)
    If no: Exit

If not exists: Continue to Step 2
```

**Step 2: Check Cross-Command Integration**
```
Read: .sdd/spec-manifest.json

If exists:
  Ask: "Found spec manifest from /synthesize-specs. Use it? [y/n]"
  If yes:
    Convert to module-manifest.json format:
    - Copy modules array
    - Add claude_md_path: "[path]/CLAUDE.md"
    - Remove drift fields
    - Set all status: "pending"
    Write: .sdd/module-manifest.json
    Skip to Phase 2

If not exists: Continue to Step 3
```

**Step 3: Invoke Module Discovery**
```
Task(
  description: "Discover modules in codebase",
  prompt: "Analyze codebase and detect logical module boundaries using all 5 heuristics. Return ranked list with confidence ≥50%. Project root: [pwd]",
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

Construct JSON:
{
  "generated_at": "[ISO 8601 timestamp]",
  "project_root": "[pwd output]",
  "modules": [
    {
      "path": "[module path]",
      "status": "pending",
      "claude_md_path": "[path]/CLAUDE.md",
      "error": null
    }
  ]
}

Write: .sdd/module-manifest.json
```

---

## Phase 2: Parallel Documentation Generation

**Step 1: Filter Modules**
```
Read: .sdd/module-manifest.json
Filter: status === "pending" OR status === "failed"
Count: N modules to process
```

**Step 2: Spawn Agents (Batches of 10)**
```
Split into batches of 10
For each batch:

  Send SINGLE message with MULTIPLE Task calls:

  Task(
    description: "Generate CLAUDE.md for [module-name]",
    prompt: "Generate CLAUDE.md for module at path: [module_path]",
    subagent_type: "spiral-grove:module-doc-synthesizer",
    model: "haiku"
  )

  Wait for all agents in batch
  Parse results (see Step 3)
```

**Step 3: Update Manifest**
```
For each agent response:

  If contains "✅ CLAUDE.md written":
    modules[i].status = "completed"
    modules[i].error = null
    Log: "✓ [path]/CLAUDE.md (XXX lines)"

  Else if contains "❌ ERROR:":
    modules[i].status = "failed"
    modules[i].error = "[error message]"
    Log: "✗ Failed [path]: [error]"
    Continue (don't stop)

Update manifest.generated_at
Write: .sdd/module-manifest.json
```

**Step 4: Generate Root CLAUDE.md**
```
Detect project name:
- Read package.json → name
- Read Cargo.toml → [package] name
- Read go.mod → module
- Read *.uproject → project name
- Fallback: directory name

Glob: * (top-level directories)

Build module index from manifest (group by prefix)

Read README.md for getting started (if exists)

Construct root CLAUDE.md:
# [Project Name]
**Last Generated**: [timestamp]
## Purpose
[Infer from README/package.json]
## Architecture
[High-level from directory structure]
## Directory Structure
[Tree view]
## Modules
### [Category]
- [path](path/CLAUDE.md) - [description]
## Getting Started
[From README/package.json scripts]
<!-- BEGIN: HAND-EDITED -->
<!-- END: HAND-EDITED -->

Write: CLAUDE.md (project root)
```

**Step 5: Display Progress**
```
Count: successful, failed

Output:
## Generation Complete: [successful] / [total] modules

**Successful**: ✓ [list paths]
**Failed**: ✗ [list paths with errors]
**Root**: CLAUDE.md created at project root

**Next**: Phase 3
```

---

## Phase 3: SDD Integration (Optional)

**Step 1: Check for Specs**
```
Bash: ls -d .sdd/specs 2>/dev/null

If exit code != 0:
  Output: "Skipping SDD integration (no .sdd/specs/)"
  Skip to Final Output
```

**Step 2: Scan Specs**
```
Glob: .sdd/specs/**/*.md

For each spec:
  Extract name: ".sdd/specs/auth.md" → "auth"
  Tokenize: "user-auth" → ["user", "auth"]
  Store: { path, name, tokens }
```

**Step 3: Match Modules to Specs**
```
For each completed module:
  Extract name: "src/auth" → "auth"
  Tokenize: "auth" → ["auth"]

  Try matching:
  a) Exact: name === spec name
  b) Hierarchy: path mirrors spec path
  c) Fuzzy: token overlap ≥ 70%

  Store: matched or unmatched
```

**Step 4: Insert Origin Fields**
```
For each matched module:
  Read: [module.claude_md_path]

  Construct Origin:
  "**Origin**: Implemented from [.sdd/specs/[name].md](.sdd/specs/[name].md)"

  Insert after title, before Last Generated:
  # [Module Name]

  **Origin**: ...
  **Last Generated**: ...
  [rest]

  Write: [module.claude_md_path]
```

**Step 5: Report**
```
Count: linked, unlinked

Output:
## SDD Integration Complete: [linked] / [total]

**Linked**: ✓ [list "module → spec"]
**Unlinked**: [list paths] (expected for utilities)
```

---

## Final Output

```
Read: .sdd/module-manifest.json

Count: totalGenerated, totalFailed, totalModules

Output:
✅ Documentation Synthesis Complete

**Generated Files**:
- 1 root CLAUDE.md
- [totalGenerated] module CLAUDE.md files

**Status Breakdown**:
- Completed: [totalGenerated] modules
- Failed: [totalFailed] modules

[If failed > 0:]
**Failed Modules**:
- [path]: [error]

[If Phase 3 ran:]
**SDD Integration**:
- Linked: [linkedCount]
- Unlinked: [unlinkedCount]

**Manifest**: .sdd/module-manifest.json

✓ Documentation ready!
```

---

## Error Handling

| Error | Action |
|-------|--------|
| No modules detected | Exit, suggest manual path |
| Invalid module path | Exit with error |
| Agent failure | Continue, report in final output |
| Manifest corruption | Prompt to regenerate |

---

## Notes

- **Framework-agnostic**: Works on any codebase
- **Batching**: Max 10 parallel agents
- **Resumability**: Manifest tracks progress
- **Hand-edits**: Preserved between `<!-- BEGIN/END: HAND-EDITED -->` markers
- **Cross-command**: Can import from /synthesize-specs
