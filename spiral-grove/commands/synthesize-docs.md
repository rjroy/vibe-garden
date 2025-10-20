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

**Step 1: Check for existing manifest**
```
If .sdd/module-manifest.json exists:
  → Skip to Resumability section
Else:
  → Continue to Step 2
```

**Step 2: Scan for package files** (strongest signal)
```
Glob: "**/package.json" (exclude: node_modules/**)
Glob: "**/setup.py" (exclude: venv/**)
Glob: "**/go.mod"
Glob: "**/Cargo.toml" (exclude: target/**)
Glob: "**/pom.xml" (exclude: target/**)
Glob: "**/__init__.py" (Python packages, exclude: venv/**,__pycache__/**)

For each match:
  - Extract directory path
  - Mark as module candidate (high confidence)
```

**Step 3: Scan for code-heavy directories** (secondary signal)
```
Glob: "src/**/*.{ts,js,tsx,jsx,py,go,rs,java,cpp,c}" (exclude exclusions)
Glob: "lib/**/*.{ts,js,tsx,jsx,py,go,rs,java,cpp,c}"
Glob: "modules/**/*.{ts,js,tsx,jsx,py,go,rs,java,cpp,c}"
Glob: "packages/**/*.{ts,js,tsx,jsx,py,go,rs,java,cpp,c}"
Glob: "apps/**/*.{ts,js,tsx,jsx,py,go,rs,java,cpp,c}"

For each directory with 3+ source files:
  - Check for test directory: tests/, __tests__/, *_test.*, *_spec.*, *.test.*, *.spec.*
  - If tests exist: Mark as module candidate (medium confidence)
  - If no tests: Mark as module candidate (low confidence)
```

**Exclusions** (apply to all Glob operations):
```
node_modules/**, vendor/**, .git/**, dist/**, build/**, target/**,
__pycache__/**, .pytest_cache/**, .next/**, .nuxt/**, out/**,
.*/** (hidden directories)
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

## Detected Modules

Found X modules in the codebase:

| # | Path | Language | Files | Tests | Confidence |
|---|------|----------|-------|-------|------------|
| 1 | src/auth | TypeScript | 8 | ✓ | High |
| 2 | src/api | TypeScript | 12 | ✓ | High |
| 3 | src/utils | TypeScript | 5 | ✗ | Medium |
...

**Total**: X modules detected

Approve this list? You can:
- Type "yes" to proceed with generation
- Type "add src/custom-module" to include additional modules
- Type "remove src/utils" to exclude specific modules
- Type "cancel" to exit
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

**Edge cases:**
- **0 modules detected**: "No modules detected. Provide module path manually? (e.g., 'add src/my-module')"
- **100+ modules**: "Warning: X modules detected. Generation may take Y minutes. Continue?"
- **User adds invalid path**: Verify with Glob before adding, warn if no source files found

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

**Step 3: Spawn agents in parallel (CRITICAL FOR PERFORMANCE)**
```
IMPORTANT: Use SINGLE message with MULTIPLE Task tool calls

For each module in pendingModules:
  Task tool invocation:
    description: "Generate CLAUDE.md for [module.path]"
    prompt: "Generate CLAUDE.md for module at path: [module.path]"
    subagent_type: "general-purpose"

Example for 3 modules (single message, 3 Task calls):
  - Task 1: "Generate CLAUDE.md for module at path: src/auth"
  - Task 2: "Generate CLAUDE.md for module at path: src/api"
  - Task 3: "Generate CLAUDE.md for module at path: src/db"

Wait for all agents to complete (parallel execution)
Collect results: successful (markdown content) or failed (error message)
```

**Step 4: Write module CLAUDE.md files**
```
For each successful agent response:
  1. Extract markdown content from agent output
  2. Use Write tool: [module.path]/CLAUDE.md
  3. Update manifest in memory:
     - modules[i].status = "completed"
     - modules[i].error = null
  4. Log: "✓ Generated [module.path]/CLAUDE.md"

For each failed agent response:
  1. Extract error message
  2. Update manifest in memory:
     - modules[i].status = "failed"
     - modules[i].error = "[error message]"
  3. Log: "✗ Failed [module.path]: [error message]"
  4. Continue with remaining modules (don't stop)
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
Analyze project structure:
  - Get project name from package.json/Cargo.toml/go.mod (if exists)
  - Use Bash: pwd to get project root path
  - Extract directory structure (top-level dirs only)

Build module index:
  For each completed module:
    - Extract module name from path (last segment)
    - Create markdown link: - [Module Name]([path]/CLAUDE.md)

Construct root CLAUDE.md content:
  # [Project Name]

  **Last Generated**: [ISO 8601 timestamp]

  ## Purpose
  [Brief description - infer from README.md if exists, else generic]

  ## Architecture
  [High-level overview - mention key directories: src/, lib/, etc.]

  ## Directory Structure
  ```
  project-root/
  ├── src/          [Description]
  ├── lib/          [Description]
  └── ...
  ```

  ## Modules
  [Module index with links to module CLAUDE.md files]

  ## Getting Started
  [Build/run/test commands - detect from package.json scripts, Makefile, etc.]

  **Total Lines**: Ensure ≤ 400 lines

Use Write tool: CLAUDE.md (at project root)
```

**Step 7: Display progress summary**
```
Output:

## Documentation Generation Complete

**Generated**: [N successful] / [N total] modules

**Successful**:
- ✓ src/auth/CLAUDE.md
- ✓ src/api/CLAUDE.md
...

**Failed** (if any):
- ✗ src/broken (error: No source files found)
...

**Root**: CLAUDE.md (project overview)

**Next**: Phase 3 - SDD Integration (if .sdd/specs/ exists)
```

**Performance notes:**
- Single message with multiple Task calls = parallel execution
- Target: 100 modules in <5 minutes
- Don't wait for each agent sequentially (bottleneck)

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
For each module in manifest where status === "completed":
  1. Extract module name from path:
     - "src/auth" → "auth"
     - "lib/user-service" → "user-service"
     - "packages/api/routes" → "routes"

  2. Tokenize module name:
     - "auth" → ["auth"]
     - "user-service" → ["user", "service"]

  3. Try exact match first (HIGHEST PRIORITY):
     - Search specIndex for name === module name
     - Example: module "auth" matches spec "auth.md"

  4. If no exact match, try parent/child hierarchy:
     - Module: "src/auth/oauth"
     - Look for: ".sdd/specs/authentication/oauth.md"
     - Pattern: parent dir in module path → parent dir in specs

  5. If still no match, try fuzzy token matching:
     - Calculate token overlap for each spec
     - Overlap = (matching tokens) / (total unique tokens)
     - Example: module ["auth"] vs spec ["user", "authentication"]
       → "auth" in "authentication" → 50% overlap
     - Accept if overlap >= 70%

  6. Store result:
     - If match found: { module: path, spec: specPath, confidence: "exact"|"hierarchy"|"fuzzy" }
     - If no match: { module: path, spec: null }
```

**Step 4: Insert Origin fields**
```
For each matched module:
  1. Read current CLAUDE.md: Use Read tool: [module.path]/CLAUDE.md

  2. Extract first line (title): Should match pattern "# [Module Name]"

  3. Find insertion point:
     - After title (line 1)
     - Before any existing "**Last Generated**" or "**Origin**" lines

  4. Construct Origin line:
     - Format: "**Origin**: Implemented from [.sdd/specs/[name].md](.sdd/specs/[name].md)"
     - Example: "**Origin**: Implemented from [.sdd/specs/authentication.md](.sdd/specs/authentication.md)"

  5. Check if Origin already exists:
     - Search for "**Origin**:" in current content
     - If exists: Replace existing Origin line
     - If not: Insert new Origin line after title

  6. Reconstruct CLAUDE.md:
     - Line 1: # [Module Name]
     - Line 2: (blank)
     - Line 3: **Origin**: [spec link]
     - Line 4: **Last Generated**: [timestamp]
     - Line 5+: Rest of content

  7. Use Write tool: [module.path]/CLAUDE.md
     - Overwrites with updated content
     - Preserves all other content including hand-edited sections

  8. Log: "✓ Linked [module.path] → [spec.path]"
```

**Step 5: Report results**
```
Count modules:
  - linked = modules with spec match
  - unlinked = modules without spec match

Output:

## SDD Integration Complete

**Linked to specs**: [N linked] / [N total] modules
- ✓ src/auth → .sdd/specs/authentication.md
- ✓ src/api → .sdd/specs/api-design.md
...

**No matching spec** (expected for utility modules):
- src/utils
- src/scripts
...

**Next**: Proceed to Final Output
```

**Edge cases:**
- **Multiple fuzzy matches**: Choose shortest spec path (most specific)
- **Spec in subdirectory**: Handle parent/child correctly (e.g., specs/auth/oauth.md)
- **Module already has Origin**: Replace old Origin, don't duplicate
- **Hand-edited sections**: Preserved during re-write (origin insertion doesn't affect them)

---

## Resumability

**Scenario**: User interrupts generation (timeout, cancellation, error) mid-process.

**Detection**:
- On command start: Check if `.sdd/module-manifest.json` exists
- Read manifest and count statuses:
  - `completed`: N modules
  - `pending`: M modules
  - `failed`: P modules

**Behavior based on manifest state**:

1. **All completed** (0 pending, 0 failed):
   - Message: "All documentation already generated (X modules). Re-run to regenerate?"
   - Options: "Yes" (reset all to pending) or "No" (exit)

2. **Partial completion** (some pending or failed):
   - Message: "Found existing progress. Continue from where we left off? (X pending, Y failed)"
   - Options: "Continue" (process pending/failed only) or "Start fresh" (reset all)

3. **No manifest** (first run):
   - Proceed with Phase 1 (module discovery)

**Idempotency guarantee**:
- Re-running on completed modules updates them safely
- Hand-edited sections always preserved
- Manifest tracks latest `generated_at` timestamp

---

## Final Output

After completing all three phases, display summary report:

```
✅ Documentation Synthesis Complete

**Generated**:
- 1 root CLAUDE.md (project overview)
- 12 module CLAUDE.md files

**SDD Integration**:
- 10 modules linked to specs
- 2 modules without matching specs (src/utils, src/scripts)

**Status**:
- 12 successful
- 0 failed

**Manifest**: .sdd/module-manifest.json (updated)

**Total time**: 2m 34s
```

**If failures occurred**:
```
⚠️ Documentation Synthesis Completed with Failures

**Generated**: 10/12 modules

**Failed Modules**:
- src/broken-module: No source files found in module directory
- src/complex-module: Generated CLAUDE.md exceeded 400 lines (suggest splitting)

**Guidance**:
- Review failed modules and fix issues
- Re-run command to retry failed modules only
```

---

## Error Handling

### Common Errors

**1. No modules detected**:
- Message: "No modules detected. Is this a code project?"
- Guidance: Specify module path manually or adjust detection heuristics
- Exit gracefully

**2. Module path doesn't exist** (scoped synthesis):
- Message: "Module path 'src/invalid' not found"
- Guidance: Check path and try again
- Exit gracefully

**3. Agent spawn failure**:
- Cause: Agent unavailable or Task tool error
- Behavior: Log error, continue with other modules
- Report in final output

**4. Module CLAUDE.md exceeds 400 lines**:
- Agent applies condensing strategies
- If still over: Agent returns with warning
- Command writes file anyway, reports warning
- Guidance: "Consider splitting module into smaller submodules"

**5. Manifest corruption**:
- Cause: Invalid JSON or missing fields
- Detection: JSON parse error on manifest read
- Behavior: Prompt user "Manifest corrupted. Regenerate from scratch?"
- On approval: Delete old manifest, start fresh

**6. Write permission denied**:
- Cause: Insufficient permissions for target directory
- Behavior: Log error, mark module as failed
- Guidance: "Check directory permissions for [path]"

---

## Notes

- **Framework-agnostic**: Works on any codebase (TypeScript, Python, Go, Rust, Java, etc.)
- **Optional SDD integration**: Phase 3 only runs if `.sdd/` exists
- **Agent does the work**: This command orchestrates; `module-doc-synthesizer` agent analyzes code
- **Performance target**: 100 modules in <5 minutes (parallel execution critical)
- **Hand-edit safety**: Agent preserves user content automatically
- **Module manifest**: Schema documented in `spiral-grove/docs/module-manifest-schema.md`
- **CLAUDE.md format**: Specification in `spiral-grove/docs/claude-md-format.md`
