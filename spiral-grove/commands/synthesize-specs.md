---
argument-hint: [scope]
description: Reverse-engineer specifications from implementation across the codebase
---

# Specification Synthesis Mode

You are now in **Specification Synthesis Mode**. Your role is to reverse-engineer specification documents by analyzing module implementations across the project, generating `.sdd/specs/[module-name].md` files that capture **WHAT modules accomplish** by examining **HOW they're implemented**.

## Your Focus

- **Module discovery**: Detect logical module boundaries in the codebase
- **Spec generation**: Spawn module-spec-synthesizer agents for parallel specification creation
- **Drift detection**: Compare synthesized specs to existing specs to identify deviations
- **Resumability**: Support interrupted generation via manifest state tracking
- **Legacy bootstrapping**: Enable SDD workflow on codebases without existing specs

## Command Usage

This command accepts an optional scope argument:
```
/spiral-grove:synthesize-specs           # Full project spec synthesis
/spiral-grove:synthesize-specs src/auth  # Single module spec regeneration
```

**Scope behavior**:
- **No argument**: Synthesize specifications for entire project (all modules)
- **With path**: Regenerate specification for specific module only

## Prerequisites

Before starting synthesis, verify:

1. **Project structure**:
   - Working directory contains a code project (source files present)
   - Module structure is logical (directories with related code)
   - Tests exist (improves spec quality via acceptance criteria extraction)

2. **For scoped synthesis** (single module):
   - The specified module path exists
   - Module contains source files (not an empty directory)

3. **Check for existing manifest**:
   - If `.sdd/spec-manifest.json` exists: Resumability mode (continue from previous run)
   - If missing: First run (full discovery and generation)

4. **Ensure .sdd/specs/ directory exists**:
   - Create if missing: `mkdir -p .sdd/specs`

**Note**: This command reverse-engineers specs from ANY codebase, enabling SDD adoption on legacy projects.

## Behavior Guidelines

1. **User approval required**:
   - ALWAYS present detected module list before generation
   - Allow user to approve, modify, or cancel
   - Never generate specs without explicit approval

2. **Parallel execution for performance**:
   - Spawn multiple module-spec-synthesizer agents simultaneously
   - Use single message with multiple Task tool calls
   - Process in batches of 10 agents (manageable load)
   - Target: 100 modules in ~15 minutes

3. **Drift detection throughout**:
   - Agent automatically detects drift when existing spec present
   - Trust the agent to handle comparison correctly
   - Never overwrite existing specs without marking drift

4. **Graceful failure handling**:
   - If a module fails, continue with remaining modules
   - Record failures in manifest with error messages
   - Report all failures at end with guidance

5. **Idempotent operation**:
   - Re-running the command is safe
   - Resumability: Skip already-completed modules
   - Drift detection ensures changes are tracked

## Three-Phase Workflow

### Phase 1: Module Discovery

**Execute these steps in order:**

**Step 1: Check for existing manifest** (Resumability)
```
IMPORTANT: Run Resumability section FIRST (after this phase header)

If manifest exists and user chose to continue/regenerate:
  → Resume from Resumability Step 4 (skip Phase 1, go to Phase 2)
Else (no manifest or user declined):
  → Continue to Step 2 below (full Phase 1 execution)
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

**Step 7: Create .sdd/specs/ directory and manifest**
```
Use Bash to ensure directory exists:
  mkdir -p .sdd/specs

Use Write tool to create .sdd/spec-manifest.json:

{
  "generated_at": "<current ISO 8601 timestamp>",
  "project_root": "<absolute path from Bash: pwd>",
  "modules": [
    {
      "path": "<relative path>",
      "status": "pending",
      "spec_path": ".sdd/specs/<module-name>.md",
      "drift_detected": false,
      "error": null
    }
    // ... repeat for each module
  ]
}

If .sdd/ directory doesn't exist: Create it first (Bash: mkdir -p .sdd)
```

**Edge cases**: 0 modules → prompt for manual path | 100+ modules → warn time estimate | Invalid path → verify with Glob

---

### Phase 2: Parallel Specification Generation

**Execute these steps in order:**

**Step 1: Read manifest**
```
Use Read tool: .sdd/spec-manifest.json
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
         Task(description: "Generate spec for [path]",
              prompt: "Generate specification for module at path: [path]",
              subagent_type: "general-purpose")

         # Agent prompt should reference the module-spec-synthesizer agent prompt
         # by including its full content or path
     - Wait for ALL agents in batch to complete
     - Collect results (success or error reports)
     - Continue to next batch

Example: 25 modules → 3 batches (10 + 10 + 5)
  Batch 1: 10 parallel Task calls → wait → collect results
  Batch 2: 10 parallel Task calls → wait → collect results
  Batch 3: 5 parallel Task calls → wait → collect results

Rationale: Limits concurrent agent load while maintaining parallelism
```

**Agent Invocation Details**:
```
For each module, construct Task prompt:

"You are a specification synthesis agent. Analyze the module at path: [module_path]

Follow the routine defined in spiral-grove/agents/module-spec-synthesizer.md:

1. Check if .sdd/specs/[module-name].md exists
   - If exists: Load for drift detection
   - If not: Fresh synthesis

2. Analyze module implementation:
   - Discover all source files, tests, configs
   - Extract user stories from tests and APIs
   - Identify functional requirements from code capabilities
   - Extract non-functional requirements (performance, security, reliability)
   - Find explicit constraints (DO NOT) from validation, comments
   - Map integration points (dependencies, external APIs)
   - Convert test cases to acceptance criteria

3. Generate specification following SDD template:
   - Executive Summary
   - User Story
   - Stakeholders
   - Success Criteria
   - Functional Requirements
   - Non-Functional Requirements
   - Explicit Constraints (DO NOT)
   - Technical Context
   - Acceptance Tests
   - Open Questions
   - Out of Scope

4. If existing spec found: Perform drift detection
   - Compare requirements (added, missing, modified)
   - Identify constraint violations
   - Generate drift report section

5. Write spec to .sdd/specs/[module-name].md
   - Include metadata: Reverse-Engineered: true
   - Include drift report if applicable

Report success or failure with details."
```

**Step 4: Update manifest with agent results**
```
For each successful agent response:
  1. Verify agent reported success (agent already wrote the file)
  2. Check if drift was detected (from agent report)
  3. Update manifest in memory:
     - modules[i].status = "completed"
     - modules[i].drift_detected = true/false (from agent report)
     - modules[i].error = null
  4. Log: "✓ [module.spec_path]" + (drift detected? " [DRIFT]" : "")

For each failed agent response:
  1. Extract error message from agent output
  2. Update manifest in memory:
     - modules[i].status = "failed"
     - modules[i].drift_detected = false
     - modules[i].error = "[error message]"
  3. Log: "✗ Failed [module.path]: [error message]"
  4. Continue with remaining modules (don't stop)

Note: Agents write files directly. This step only updates tracking manifest.
```

**Step 5: Update manifest with results**
```
Update manifest in memory:
  - generated_at = current ISO 8601 timestamp (new Date().toISOString())

Use Write tool: .sdd/spec-manifest.json
Write updated manifest JSON (pretty-printed, indent: 2)
```

**Step 6: Display progress summary**
```
Output:
## Generation Complete: [N successful] / [N total] modules

**Successful**: ✓ src/auth [DRIFT], ✓ src/api, ...
**Failed** (if any): ✗ src/broken (error: ...), ...

**Drift Detected**: [N modules with drift]
- src/auth: 2 requirements added, 1 modified
- src/payments: 1 constraint violated

**Next**: Review specs in .sdd/specs/ directory
```

**Performance**: Batched parallel execution (10 at a time) = manageable load while maintaining speed (target ~15 min for 100 modules)

---

### Phase 3: Summary and Recommendations

**Execute these steps in order:**

**Step 1: Analyze generated specs**
```
For each completed module:
  1. Read .sdd/spec-manifest.json
  2. Count modules by drift status:
     - driftCount = modules.filter(m => m.drift_detected === true).length
     - cleanCount = modules.filter(m => m.drift_detected === false && m.status === "completed").length
  3. Identify modules without existing specs (new specs)
  4. Identify modules with drift (existing specs that diverged)
```

**Step 2: Generate recommendations**
```
Based on drift analysis:

If driftCount > 0:
  Recommendation: "Review drift reports in specs with [DRIFT] marker.
  Decide whether to:
  - Update specs to match implementation (accept drift)
  - Update implementation to match specs (fix drift)
  - Document intentional deviations in spec"

If cleanCount === totalCount:
  Recommendation: "All specs match implementation perfectly (rare for legacy code).
  Review specs for completeness and accuracy."

If newSpecsCount > 0:
  Recommendation: "New specs generated for modules without existing specs.
  Review for accuracy and begin using SDD workflow:
  - /spiral-grove:plan-generation
  - /spiral-grove:task-breakdown
  - /spiral-grove:implementation"
```

**Step 3: Display final report**
```
Output:
✅ Specification Synthesis Complete

**Total Time**: X minutes Y seconds

**Generated Specs**:
- Total: X specs
- New specs: Y (no existing spec)
- Updated specs: Z (existing spec found)

**Drift Analysis**:
- Clean: N modules (implementation matches spec)
- Drift detected: M modules (implementation diverged from spec)

**Drift Details** (if M > 0):
| Module | Added | Missing | Modified | Constraints Violated |
|--------|-------|---------|----------|---------------------|
| auth | 2 | 0 | 1 | 0 |
| payments | 0 | 1 | 0 | 1 |

**Failed Modules** (if any):
- src/broken-module: No source files found in module directory
- src/no-tests: WARNING - No tests found (limited spec quality)

**Recommendations**:
1. Review drift reports in .sdd/specs/[module-name].md (search for "Drift Detection Report")
2. Decide on drift resolution strategy per module (update spec or fix code)
3. For new specs: Validate accuracy by reviewing against implementation
4. Begin SDD workflow for future development:
   - /spiral-grove:plan-generation
   - /spiral-grove:task-breakdown
   - /spiral-grove:implementation

**Manifest**: Progress saved to .sdd/spec-manifest.json
```

**Step 4: Edge case messages**
```
If all modules have drift:
  "⚠️ All modules show drift from existing specs. This may indicate:
   - Specs are outdated
   - Implementation has evolved significantly
   - Original specs were aspirational rather than descriptive
   Recommendation: Prioritize drift review and resolution"

If no modules have tests:
  "⚠️ No test files found in any module. Spec quality will be limited.
   Acceptance criteria are inferred from code behavior only.
   Recommendation: Add tests to improve spec accuracy"
```

---

## Resumability

Handles interrupted sessions and re-runs. **Execute at command start** (before Phase 1):

**Step 1: Check for existing manifest**
```
Use Read tool: .sdd/spec-manifest.json
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
  → Output: "All X modules complete. Re-run to regenerate all (with drift detection)? [y/n]"
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
  - Drift detection happens per-module (agent handles it)
```

**Step 5: Update manifest timestamp**
```
manifest.generated_at = new Date().toISOString()
Use Write tool: .sdd/spec-manifest.json (overwrite with updated manifest)
```

**Idempotency**: Re-running is safe. Completed modules stay completed unless user chooses "regenerate all". Drift detection ensures changes are tracked.

---

## Final Output

After all phases complete, display comprehensive summary (see Phase 3 Step 3 above).

---

## Error Handling

| Error | Action | Guidance |
|-------|--------|----------|
| No modules detected | Exit gracefully | Specify module path manually |
| Invalid module path | Exit gracefully | Check path and retry |
| Agent spawn failure | Continue with others | Report in final output |
| No tests found | Warn, continue | Spec quality will be limited |
| Manifest corruption | Prompt to regenerate | Delete old manifest if approved |
| Write permission denied | Mark module failed | Check directory permissions |
| .sdd/specs/ missing | Create it | mkdir -p .sdd/specs |

---

## Use Cases

### 1. Legacy Codebase Adoption

**Scenario**: You have a large codebase without specs. You want to adopt SDD.

**Workflow**:
```
/spiral-grove:synthesize-specs
→ Generates specs for all modules
→ Review specs for accuracy
→ Begin using SDD workflow for new features
```

### 2. Spec Drift Detection

**Scenario**: You have existing specs but suspect implementation has diverged.

**Workflow**:
```
/spiral-grove:synthesize-specs
→ Compares implementation to existing specs
→ Marks drift in spec files
→ Review drift reports
→ Update specs or fix code as needed
```

### 3. Onboarding Documentation

**Scenario**: New team member needs to understand what the system does.

**Workflow**:
```
/spiral-grove:synthesize-specs
→ Generates requirement-focused specs
→ Read .sdd/specs/ to understand capabilities
→ Use as complement to CLAUDE.md (which explains HOW)
```

### 4. Single Module Spec Refresh

**Scenario**: You've significantly changed one module and need updated spec.

**Workflow**:
```
/spiral-grove:synthesize-specs src/auth
→ Regenerates only src/auth spec
→ Detects drift from previous version
→ Review changes
```

---

## Notes

- **Reverse engineering**: Specs describe existing behavior, not intended behavior
- **Drift detection**: Compares intended (spec) vs. actual (code) behavior
- **Framework-agnostic**: Works on any codebase (TypeScript, Python, Go, Rust, Java, Unreal Engine, etc.)
- **SDD bootstrapping**: Enables SDD adoption on legacy codebases
- **Agent does the work**: This command orchestrates; `module-spec-synthesizer` agent analyzes code
- **Performance target**: 100 modules in ~15 minutes (batched parallel execution, max 10 concurrent agents)
- **Spec quality depends on tests**: Better tests = better specs (acceptance criteria from test assertions)
- **Spec manifest**: Schema similar to module-manifest.json but tracks drift status
- **Complementary to synthesize-docs**: Use both for complete codebase understanding (WHAT + HOW)

---
