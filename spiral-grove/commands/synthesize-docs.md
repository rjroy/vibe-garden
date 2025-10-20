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

**Goal**: Identify logical module boundaries and save to manifest.

**Heuristics for module detection**:
- Directories with **package files**: `package.json`, `setup.py`, `go.mod`, `Cargo.toml`, `pom.xml`
- Directories with **3+ source files** AND a test directory (`tests/`, `__tests__/`, `*_test.*`)
- Subdirectories under: `src/`, `lib/`, `modules/`, `packages/`, `apps/`
- Language-specific patterns: Python packages (`__init__.py`), Go modules, Rust crates

**Exclusions** (never treat these as modules):
- `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`, `target/`, `__pycache__/`, `.pytest_cache/`
- Hidden directories (starting with `.`)
- Build artifacts and dependency directories

**Steps**:
1. Use `Glob` tool to scan codebase
2. Apply heuristics to identify modules
3. Present list to user in table format:
   ```
   Detected Modules:
   1. src/auth (TypeScript, 8 files, has tests)
   2. src/api (TypeScript, 12 files, has tests)
   3. src/db (TypeScript, 5 files, no tests)
   ...
   ```
4. Ask user: "Approve this module list? (You can request additions/removals)"
5. On approval: Create `.sdd/module-manifest.json`:
   ```json
   {
     "generated_at": "2025-10-20T14:30:00Z",
     "project_root": "/home/user/projects/my-app",
     "modules": [
       {
         "path": "src/auth",
         "status": "pending",
         "claude_md_path": "src/auth/CLAUDE.md",
         "error": null
       }
     ]
   }
   ```

**Edge cases**:
- **0 modules detected**: Guide user to manually specify module paths
- **100+ modules**: Warn about long generation time, offer to batch
- **Existing manifest**: Skip discovery, go to Phase 2 (resumability mode)

---

### Phase 2: Parallel Documentation Generation

**Goal**: Generate CLAUDE.md for all pending/failed modules in parallel.

**Steps**:

1. **Read manifest**: Load `.sdd/module-manifest.json`
2. **Filter modules**: Get list of modules with `status: "pending"` or `status: "failed"`
3. **Spawn agents in parallel**:
   - For each module: spawn `module-doc-synthesizer` agent via Task tool
   - Use **single message with multiple Task tool calls** (critical for performance)
   - Agent receives: module path (e.g., "src/auth")
   - Agent returns: Complete CLAUDE.md markdown content

4. **Write CLAUDE.md files**:
   - For each successful agent response:
     - Write content to `[module_path]/CLAUDE.md`
     - Update manifest: `status: "pending"` → `status: "completed"`
     - Update manifest: `error: null`
   - For each failed agent:
     - Update manifest: `status: "failed"`
     - Update manifest: `error: "[error message]"`
     - Log failure for final report

5. **Generate root CLAUDE.md**:
   - Create project-level `CLAUDE.md` at repository root
   - Include:
     - Project purpose and architecture overview
     - Directory structure
     - Module index with links: `- [Auth Module](src/auth/CLAUDE.md)`
     - Getting started guide (how to build, run, test)
   - Concise overview (≤400 lines)

6. **Update manifest timestamp**: Set `generated_at` to current ISO 8601 timestamp

**Agent invocation example**:
```markdown
Task: Generate CLAUDE.md for module at path: src/auth
```

**Progress indicators**:
- Show progress as agents complete: "Generated 5/10 modules..."
- Display module names as they complete

---

### Phase 3: SDD Integration (Optional)

**Goal**: Link generated CLAUDE.md files back to specifications.

**This phase only runs if `.sdd/specs/` directory exists.** Otherwise, skip to final output.

**Steps**:

1. **Check for .sdd/specs/ directory**:
   - If missing: Skip Phase 3 (not a Spiral Grove project)
   - If present: Proceed with integration

2. **For each completed module**:
   - Read `[module]/CLAUDE.md`
   - Analyze module path (e.g., `src/auth`)
   - Search for matching spec in `.sdd/specs/`:
     - Exact match: `authentication.md`, `auth.md`
     - Fuzzy match: `user-authentication.md` (contains "auth")
     - Parent/child: `authentication/oauth.md` for `src/auth/oauth`

3. **If match found**:
   - Insert Origin field after title:
     ```markdown
     # Authentication Module

     **Origin**: Implemented from [.sdd/specs/authentication.md](.sdd/specs/authentication.md)
     **Last Generated**: 2025-10-20T14:30:00Z
     ```
   - Re-write CLAUDE.md with Origin field
   - Preserve hand-edited sections during re-write

4. **If no match found**:
   - Skip Origin field (utility modules may not have specs)
   - Log for final report: "Module X has no matching spec"

5. **Handle parent/child hierarchies**:
   - Child module `src/auth/oauth` → child spec `.sdd/specs/authentication/oauth.md`
   - Child module `src/auth/session` → child spec `.sdd/specs/authentication/session.md`

**Fuzzy matching logic**:
- Tokenize module name: `src/auth` → `["auth"]`
- Search specs for matching tokens
- Confidence threshold: 70% token overlap
- If multiple matches: Prefer exact, then shortest path
- If uncertain: Present options to user

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
