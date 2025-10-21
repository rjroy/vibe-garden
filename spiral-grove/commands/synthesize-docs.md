---
argument-hint: [scope]
description: Generate operational CLAUDE.md documentation from implementation
---

# Documentation Synthesis Mode

You are now in **Documentation Synthesis Mode**. Your role is to generate operational CLAUDE.md documentation by analyzing module implementations across the project, providing concise maintenance context extracted from actual code.

## Your Focus

- **Module discovery**: Detect logical module boundaries in the codebase
- **Documentation generation**: Spawn module-doc-synthesizer agents for parallel CLAUDE.md creation
- **SDD integration**: Link generated documentation back to specifications
- **Resumability**: Support interrupted generation via manifest state tracking
- **Quality assurance**: Ensure all documentation meets constraints (≤400 lines per module)

## Command Usage

This command accepts an optional scope argument:
```
/spiral-grove:synthesize-docs           # Full project synthesis
/spiral-grove:synthesize-docs src/auth  # Single module regeneration
```

**Scope behavior**:
- **No argument**: Synthesize documentation for entire project (all modules)
- **With path**: Regenerate documentation for specific module only

## Prerequisites

Before starting synthesis, verify:

1. **Project structure**:
   - Working directory contains a code project (source files present)
   - Ideally has `.sdd/` directory (for SDD integration), but NOT required
   - Module structure is logical (directories with related code)

2. **For scoped synthesis** (single module):
   - The specified module path exists
   - Module contains source files (not an empty directory)

3. **Check for existing manifest**:
   - If `.sdd/module-manifest.json` exists: Resumability mode (continue from previous run)
   - If missing: First run (full discovery and generation)
   - Manifest structure documented in: `spiral-grove/docs/module-manifest-schema.md`

**Note**: This command works on ANY codebase, not just Spiral Grove projects. The `.sdd/` integration is optional.

## Behavior Guidelines

1. **User approval required**:
   - ALWAYS present detected module list before generation
   - Allow user to approve, modify, or cancel
   - Never generate documentation without explicit approval

2. **Parallel execution for performance**:
   - Spawn multiple module-doc-synthesizer agents simultaneously
   - Use single message with multiple Task tool calls
   - Target: 100 modules in <5 minutes

3. **Preserve hand-edited content**:
   - Agent automatically preserves content between `<!-- BEGIN: HAND-EDITED -->` markers
   - Trust the agent to handle preservation correctly
   - Never overwrite hand-edits

4. **Graceful failure handling**:
   - If a module fails, continue with remaining modules
   - Record failures in manifest with error messages
   - Report all failures at end with guidance

5. **Idempotent operation**:
   - Re-running the command is safe
   - Resumability: Skip already-completed modules
   - Hand-edit preservation ensures no content loss

## Three-Phase Workflow

### Phase 1: Module Discovery

**Execute these steps in order:**

**Step 1: Check for existing manifests** (Resumability & Cross-Command Integration)
```
IMPORTANT: Check manifests in this order:

1. Check .sdd/module-manifest.json (this command's manifest)
   - If exists: Run Resumability section (see below) → may resume or continue

2. If no module-manifest.json, check .sdd/spec-manifest.json (from /synthesize-specs)
   - If exists:
     → Output: "Found spec manifest from /synthesize-specs. Use it as starting point? [y/n]"
     → If "y": Convert spec-manifest.json to module-manifest.json format:
       - Copy "modules" array (path, spec_path)
       - Add claude_md_path: "[path]/CLAUDE.md"
       - Remove drift_detected, drift_summary fields (not needed for docs)
       - Set all status: "pending"
       - Write to .sdd/module-manifest.json
       → Continue to Step 7 (skip discovery Steps 2-6)
     → If "n": Continue to Step 2 (full discovery)

3. If neither manifest exists:
   → Continue to Step 2 (full Phase 1 execution - fresh discovery)
```

**Step 2: Scan for package files** (strongest signal)
```
Glob patterns (with exclusions):
  package.json (exclude node_modules), setup.py (exclude venv), go.mod,
  Cargo.toml (exclude target), pom.xml (exclude target), __init__.py (exclude venv/__pycache__),
  *.uproject (Unreal Engine projects)

For each match: Extract directory → mark as high-confidence candidate

Special handling for Unreal Engine:
  - If *.uproject found at root: Scan Source/ for module directories
  - Each Source/[ModuleName]/ with *.Build.cs → high-confidence module
  - Content/ directory → treat as single asset module (medium confidence)
  - Plugins/[PluginName]/Source/[ModuleName]/ → high-confidence plugin module
```

**Step 3: Scan for code-heavy directories** (secondary signal)
```
Glob standard dirs with source files: src/, lib/, modules/, packages/, apps/, Source/ (Unreal)
File patterns: *.{ts,js,tsx,jsx,py,go,rs,java,cpp,c,h,cs} (include .h and .cs for Unreal)

For each dir with 3+ source files:
  - Has tests? (tests/, __tests__/, *_test.*, *_spec.*) → medium confidence
  - No tests? → low confidence

Unreal Engine specific:
  - Source/[ModuleName]/ with *.Build.cs → high confidence (C++ module)
  - Source/[ModuleName]Editor/ → high confidence (editor module)
  - Plugins/[Name]/Source/ → high confidence (plugin module)
```

**Exclusions** (apply to all Glob operations):
```
node_modules/**, vendor/**, .git/**, dist/**, build/**, target/**,
__pycache__/**, .pytest_cache/**, .next/**, .nuxt/**, out/**,
.*/** (hidden directories),
Saved/**, Intermediate/**, Binaries/**, DerivedDataCache/** (Unreal Engine)
```

**Step 4: Deduplicate and rank**
```
Combine candidates from Step 2 and Step 3
Remove duplicates (same path)
Sort by confidence: high → medium → low
Limit to reasonable scope (if >100 modules, warn user)
```

**Step 5: Present to user**
```
Output format:

## Detected Modules (X found)

| Path | Language | Files | Tests | Confidence |
|------|----------|-------|-------|------------|
| src/auth | TypeScript | 8 | ✓ | High |
| src/api | TypeScript | 12 | ✓ | High |
...

Approve? Options: "yes" | "add <path>" | "remove <path>" | "cancel"
```

**Step 6: Handle user response**
```
Parse user input:
- "yes" / "approve" / "ok" → Proceed to Step 7
- "add <path>" → Add path to module list, return to Step 5
- "remove <path>" → Remove path from module list, return to Step 5
- "cancel" / "no" → Exit command gracefully
- Other → Ask for clarification, repeat Step 5
```

**Step 7: Create manifest**
```
Use Write tool to create .sdd/module-manifest.json:

{
  "generated_at": "<current ISO 8601 timestamp>",
  "project_root": "<absolute path from Bash: pwd>",
  "modules": [
    {
      "path": "<relative path>",
      "status": "pending",
      "claude_md_path": "<relative path>/CLAUDE.md",
      "error": null
    }
    // ... repeat for each module
  ]
}

If .sdd/ directory doesn't exist: Create it first (Bash: mkdir -p .sdd)
```

**Edge cases**: 0 modules → prompt for manual path | 100+ modules → warn time estimate | Invalid path → verify with Glob

---

### Phase 2: Parallel Documentation Generation

**Execute these steps in order:**

**Step 1: Read manifest**
```
Use Read tool: .sdd/module-manifest.json
Parse JSON to extract modules array
```

**Step 2: Filter modules for generation**
```
Filter modules where status === "pending" OR status === "failed"
Store in pendingModules array
Count: N modules to process
```

**Step 3: Spawn agents in parallel batches (CRITICAL)**
```
IMPORTANT: Process modules in batches of MAX 10 parallel agents

Batch processing loop:
  1. Split pendingModules into batches of 10
  2. For each batch:
     - Send SINGLE message with MULTIPLE Task tool calls (up to 10)
     - For each module in batch:
         Task(description: "Generate CLAUDE.md for [path]",
              prompt: "Generate CLAUDE.md for module at path: [path]",
              subagent_type: "spiral-grove:module-doc-synthesizer")
     - Wait for ALL agents in batch to complete
     - Collect results (success or error reports)
     - Continue to next batch

Example: 25 modules → 3 batches (10 + 10 + 5)
  Batch 1: 10 parallel Task calls → wait → collect results
  Batch 2: 10 parallel Task calls → wait → collect results
  Batch 3: 5 parallel Task calls → wait → collect results

Rationale: Limits concurrent agent load while maintaining parallelism
```

**Step 4: Update manifest with agent results**
```
For each successful agent response:
  1. Verify agent reported success (agent already wrote the file)
  2. Update manifest in memory:
     - modules[i].status = "completed"
     - modules[i].error = null
  3. Log: "✓ [module.path]/CLAUDE.md"

For each failed agent response:
  1. Extract error message from agent output
  2. Update manifest in memory:
     - modules[i].status = "failed"
     - modules[i].error = "[error message]"
  3. Log: "✗ Failed [module.path]: [error message]"
  4. Continue with remaining modules (don't stop)

Note: Agents write files directly. This step only updates tracking manifest.
```

**Step 5: Update manifest with results**
```
Update manifest in memory:
  - generated_at = current ISO 8601 timestamp (new Date().toISOString())

Use Write tool: .sdd/module-manifest.json
Write updated manifest JSON (pretty-printed, indent: 2)
```

**Step 6: Generate root CLAUDE.md**
```
Analyze project:
  - Project name: package.json/Cargo.toml/go.mod/*.uproject (if exists)
  - Directory structure: top-level dirs only
  - Module index: link each completed module → [path]/CLAUDE.md

Construct root CLAUDE.md (≤400 lines):
  # [Project Name]
  **Last Generated**: [timestamp]
  ## Purpose / ## Architecture / ## Directory Structure / ## Modules / ## Getting Started
  [Infer from README.md, package.json scripts, Makefile]

For Unreal Engine projects:
  - Include Unreal version from .uproject
  - List C++ modules (Source/), Editor modules, and Plugins separately
  - Note key Config/*.ini files and Content organization

Use Write tool: CLAUDE.md (at project root)
```

**Step 7: Display progress summary**
```
Output:
## Generation Complete: [N successful] / [N total] modules
**Successful**: ✓ src/auth, ✓ src/api, ...
**Failed** (if any): ✗ src/broken (error: ...), ...
**Root**: CLAUDE.md created
**Next**: Phase 3 (if .sdd/specs/ exists)
```

**Performance**: Batched parallel execution (10 at a time) = manageable load while maintaining speed (target ~10-15 min for 100 modules)

---

### Phase 3: SDD Integration (Optional)

**Execute these steps in order:**

**Step 1: Check for .sdd/specs/ directory**
```
Use Bash: ls -d .sdd/specs 2>/dev/null
If exit code != 0 (directory doesn't exist):
  → Skip Phase 3 entirely
  → Output: "Skipping SDD integration (no .sdd/specs/ directory)"
  → Jump to Final Output section
Else:
  → Continue to Step 2
```

**Step 2: Scan for all spec files**
```
Use Glob: ".sdd/specs/**/*.md"
Collect all spec file paths

For each spec path:
  - Extract spec name (e.g., ".sdd/specs/authentication.md" → "authentication")
  - Extract spec tokens (e.g., "user-authentication" → ["user", "authentication"])
  - Store in specIndex: { path, name, tokens }
```

**Step 3: Match modules to specs**
```
For each completed module:
  1. Extract name: "src/auth" → "auth", "lib/user-service" → "user-service"
  2. Tokenize: "user-service" → ["user", "service"]
  3. Try 3-tier matching:
     a) Exact: name === spec name (e.g., "auth" matches "auth.md")
     b) Hierarchy: "src/auth/oauth" → look for "specs/authentication/oauth.md"
     c) Fuzzy: token overlap ≥70% (e.g., ["auth"] overlaps 50% with ["user", "authentication"])
  4. Store: { module, spec, confidence } or { module, spec: null }
```

**Step 4: Insert Origin fields**
```
For each matched module:
  1. Read CLAUDE.md at [module.path]
  2. Extract title (line 1): "# [Module Name]"
  3. Construct Origin: "**Origin**: Implemented from [.sdd/specs/[name].md](.sdd/specs/[name].md)"
  4. Check if Origin exists → replace | else → insert after title
  5. Reconstruct: Line 1: title | Line 2: blank | Line 3: Origin | Line 4: Last Generated | Line 5+: rest
  6. Write updated CLAUDE.md (preserves hand-edited sections)
  7. Log: "✓ Linked [module.path] → [spec.path]"
```

**Step 5: Report results**
```
Output:
## SDD Integration Complete: [N linked] / [N total]
**Linked**: ✓ src/auth → authentication.md, ✓ src/api → api-design.md, ...
**Unlinked**: src/utils, src/scripts (expected for utility modules)
**Next**: Final Output
```

**Edge cases**: Multiple matches → shortest path | Parent/child specs → handle hierarchy | Existing Origin → replace | Hand-edits → preserved

---

## Resumability

Handles interrupted sessions and re-runs. **Execute at command start** (before Phase 1):

**Step 1: Check for existing manifest**
```
Use Read tool: .sdd/module-manifest.json
- If file not found → No manifest, proceed to Phase 1 (first run)
- If file exists → Parse JSON, proceed to Step 2
- If parse error → Manifest corrupted, prompt: "Manifest corrupted. Regenerate from scratch? [y/n]"
```

**Step 2: Count module statuses**
```
Parse manifest.modules array, count by status:
  completedCount = modules.filter(m => m.status === "completed").length
  failedCount = modules.filter(m => m.status === "failed").length
  pendingCount = modules.filter(m => m.status === "pending").length
  totalCount = modules.length
```

**Step 3: Determine resumption scenario**
```
Scenario A: All completed (pendingCount === 0 && failedCount === 0)
  → Output: "All X modules complete. Re-run to regenerate all? [y/n]"
  → If "y": Reset all to pending (modules[*].status = "pending"), proceed to Phase 2
  → If "n": Exit gracefully with "No changes made"

Scenario B: Partial completion (pendingCount > 0 || failedCount > 0)
  → Output: "Found progress: X completed, Y pending, Z failed. Continue from where we left off? [y/n]"
  → If "y": Proceed to Phase 2 with pending/failed modules only
  → If "n": Exit gracefully

Scenario C: No manifest (from Step 1)
  → Proceed to Phase 1 (module discovery)
```

**Step 4: Resume Phase 2 (if Scenario A or B with "y")**
```
Filter modules for generation:
  modulesToProcess = manifest.modules.filter(m => m.status === "pending" || m.status === "failed")

Skip Phase 1 (use existing manifest)
Run Phase 2 with modulesToProcess (not all modules)
  - Spawn agents only for modulesToProcess
  - Update manifest statuses: pending/failed → completed or failed with error
  - Generate/update root CLAUDE.md (includes all modules, not just processed ones)
```

**Step 5: Run Phase 3 on ALL modules**
```
Run Phase 3 (SDD Integration) on ALL modules in manifest, not just newly processed
Reason: New specs may have been added since last run
For each module (regardless of when it was completed):
  - Try to match to spec
  - Add/update Origin field if match found
```

**Step 6: Update manifest timestamp**
```
manifest.generated_at = new Date().toISOString()
Use Write tool: .sdd/module-manifest.json (overwrite with updated manifest)
```

**Idempotency**: Re-running is safe. Completed modules stay completed unless user chooses "regenerate all". Hand-edits always preserved.

---

## Final Output

After all phases complete, display comprehensive summary (per TASK-008):

**Step 1: Calculate metrics**
```
Count from manifest:
  totalGenerated = modules.filter(m => m.status === "completed").length
  totalFailed = modules.filter(m => m.status === "failed").length
  linkedCount = modules.filter(m => m has Origin field).length (track during Phase 3)
  unlinkedModules = modules without Origin field (names only)
Calculate elapsed time: end_time - start_time (track at command start)
```

**Step 2: Display report**
```
✅ Documentation Synthesis Complete

**Total Time**: X minutes Y seconds

**Generated Files**:
- 1 root CLAUDE.md (project overview)
- X module CLAUDE.md files

**Status Breakdown**:
- Completed: X modules
- Failed: Y modules (if > 0, list below)

**SDD Integration** (if Phase 3 ran):
- Modules with Origin field: X
- Modules without specs: Y (expected for utility code)
  - List: src/utils, src/scripts, ...

**Failed Modules** (if any):
- src/broken-module: No source files found in module directory
- src/complex-module: Generated CLAUDE.md exceeded 400 lines after condensing
**Retry Guidance**: Re-run `/synthesize-docs` to retry failed modules only

**Manifest**: Progress saved to .sdd/module-manifest.json
```

**Step 3: Edge case messages**
```
If totalGenerated === 0:
  "⚠️ No modules generated successfully. Review errors above and adjust module detection heuristics."

If all failed (totalFailed === totalCount):
  "❌ All modules failed. Common causes:
   - No source files in detected directories
   - Permission issues
   - Module structure doesn't match expected patterns
   Suggestion: Try manual manifest or check heuristics"
```

---

## Error Handling

| Error | Action | Guidance |
|-------|--------|----------|
| No modules detected | Exit gracefully | Specify module path manually |
| Invalid module path | Exit gracefully | Check path and retry |
| Agent spawn failure | Continue with others | Report in final output |
| CLAUDE.md exceeds 400 lines | Write with warning | Consider splitting module |
| Manifest corruption | Prompt to regenerate | Delete old manifest if approved |
| Write permission denied | Mark module failed | Check directory permissions |

---

## Notes

- **Framework-agnostic**: Works on any codebase (TypeScript, Python, Go, Rust, Java, Unreal Engine, etc.)
- **Unreal Engine support**: Detects .uproject files, C++ modules (*.Build.cs), Editor modules, Plugins, and Content
- **Optional SDD integration**: Phase 3 only runs if `.sdd/` exists
- **Agent does the work**: This command orchestrates; `module-doc-synthesizer` agent analyzes code
- **Performance target**: 100 modules in ~10-15 minutes (batched parallel execution, max 10 concurrent agents)
- **Hand-edit safety**: Agent preserves user content automatically
- **Cross-command integration**: Can use spec-manifest.json from `/synthesize-specs` as starting point (avoids re-discovery)
- **Module manifest**: Schema documented in `spiral-grove/docs/module-manifest-schema.md` (tracks documentation generation status)
- **Spec manifest**: Schema documented in `spiral-grove/docs/spec-manifest-schema.md` (companion for specs synthesis)
- **CLAUDE.md format**: Specification in `spiral-grove/docs/claude-md-format.md`
