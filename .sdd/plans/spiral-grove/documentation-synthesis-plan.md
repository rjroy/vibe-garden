# Documentation Synthesis Feature - Technical Plan

**Specification**: [../../specs/spiral-grove/documentation-synthesis.md](../../specs/spiral-grove/documentation-synthesis.md)
**Parent Plan**: [../spiral-grove-plan.md](../spiral-grove-plan.md)
**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-20
**Last Updated**: 2025-10-20

## Overview

Documentation Synthesis extends Spiral Grove with lifecycle management capabilities that bridge specifications (`.sdd/`) and operational documentation (`CLAUDE.md`). The technical approach centers on **parallel agent orchestration** for scalability (100+ modules in <5 minutes), **stateful resumability** via JSON manifests, and **semantic drift detection** through spec-code comparison. The architecture introduces one reusable agent (`module-doc-synthesizer`), one new orchestration command (`/synthesize-docs`), and one extension to existing validation (`/review spec-vs-code`).

Key architectural principle: **Agent-command separation** - the `module-doc-synthesizer` agent is framework-agnostic and reusable beyond Spiral Grove, while the `/synthesize-docs` command adds SDD-specific orchestration (spec linking, hierarchy handling).

## Architecture

### System Context

Documentation Synthesis operates as an extension to the existing Spiral Grove plugin:

```
┌─────────────────────────────────────────────────────────────┐
│                   Claude Code CLI                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Spiral Grove Plugin                     │   │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌─────────┐  │   │
│  │  │   Commands      │  │    Agents    │  │ Skills  │  │   │
│  │  │ (NEW) synthesize│  │ (NEW) module │  │ (guide) │  │   │
│  │  │ (EXT) review    │  │  -doc-synth  │  │         │  │   │
│  │  └────────┬────────┘  └──────┬───────┘  └─────────┘  │   │
│  │           │                  │                       │   │
│  └───────────┼──────────────────┼───────────────────────┘   │
│              │                  │                           │
│              ▼                  ▼                           │
│        Uses Task tool     Spawns multiple                   │
│        to spawn agents    instances in parallel             │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │  Filesystem Artifacts        │
    │  ├── .sdd/                   │
    │  │   ├── specs/              │
    │  │   ├── module-manifest.json│ ← NEW (resumability)
    │  │   └── ...                 │
    │  └── CLAUDE.md files         │ ← NEW (generated docs)
    │      ├── CLAUDE.md (root)    │
    │      └── module-a/CLAUDE.md  │
    └──────────────────────────────┘
```

**External interactions:**
- **No new runtime dependencies**: Pure markdown agents/commands
- **Parallel execution**: Multiple agent instances run simultaneously via Claude Code's Task tool
- **Stateful resumability**: `.sdd/module-manifest.json` enables interruption recovery
- **Bidirectional flow**: Development → Maintenance (synthesize), Maintenance → Development (review spec-vs-code)

### Component Overview

#### 1. Module Documentation Synthesizer Agent (NEW)

**Location**: `spiral-grove/agents/module-doc-synthesizer.md`

**Purpose**: Standalone agent that analyzes a single module and generates/updates its CLAUDE.md file (≤400 lines).

**Key characteristics**:
- **Framework-agnostic**: Works without Spiral Grove context
- **Spawnnable in parallel**: Multiple instances can run simultaneously
- **Idempotent**: Can re-run without breaking existing docs
- **Hand-edit preserving**: Respects `<!-- BEGIN: HAND-EDITED -->` markers

**Agent definition structure** (markdown with YAML frontmatter):
```yaml
---
description: Analyzes a single module and generates/updates its CLAUDE.md documentation
capabilities:
  - module-documentation
  - claude-md-generation
  - hand-edit-preservation
---

# Module Documentation Synthesizer

[Agent prompt content with routine, guidelines, output format]
```

**Routine (executed every invocation)**:
1. Check if CLAUDE.md exists for module
2. If exists: Read and extract hand-edited sections (between markers)
3. Analyze module code, tests, comments (using Read, Glob, Grep tools)
4. Generate structured content:
   - Purpose (1-2 sentences)
   - Key Components (classes/functions/files)
   - Public API (exported interfaces)
   - Integration Points (dependencies)
   - Common Operations (usage patterns)
   - Testing (how to test)
5. If updating: Merge new content with preserved hand-edits
6. Validate ≤400 lines
7. Return markdown content (command writes to disk)

**Input**: Module path (e.g., `src/authentication`)
**Output**: CLAUDE.md markdown content

#### 2. Synthesize Documentation Command (NEW)

**Location**: `spiral-grove/commands/synthesize-docs.md`

**Purpose**: Orchestrate documentation generation across entire project using module-doc-synthesizer agents.

**Command definition structure**:
```yaml
---
argument-hint: [scope]
description: Generate operational CLAUDE.md documentation from implementation
---
```

**Three-phase workflow**:

**Phase 1: Module Discovery**
- Scan codebase for logical module boundaries (directories with code + tests)
- Heuristics:
  - Directories with 3+ source files
  - Presence of index/main file
  - Test directories as indicators
  - Package/namespace boundaries (language-specific)
- Present list to user for approval/modification
- Save to `.sdd/module-manifest.json`:
  ```json
  {
    "generated_at": "2025-10-20T...",
    "project_root": "/path/to/project",
    "modules": [
      {"path": "src/module-a", "status": "pending", "claude_md_path": "src/module-a/CLAUDE.md"},
      {"path": "src/module-b", "status": "pending", "claude_md_path": "src/module-b/CLAUDE.md"}
    ]
  }
  ```

**Phase 2: Parallel Documentation Generation**
- For each module in manifest (status: "pending"):
  - Spawn `module-doc-synthesizer` agent via Task tool
  - Agent prompt includes: module path, existing CLAUDE.md (if any)
  - Agent returns markdown content
  - Command writes content to `[module]/CLAUDE.md`
  - Update manifest status: "pending" → "completed" (or "failed" on error)
- Generate root `CLAUDE.md` with project overview:
  - Project purpose and architecture
  - Directory structure
  - Module index (links to child CLAUDE.md files)
  - Getting started guide

**Phase 3: SDD Integration**
- For each completed CLAUDE.md:
  - Analyze module path against `.sdd/specs/` hierarchy
  - Identify corresponding spec (e.g., `src/auth` → `.sdd/specs/authentication.md`)
  - Add `**Origin**: Implemented from .sdd/specs/[name].md` to CLAUDE.md header
- Handles parent/child specs:
  - Child modules link to child specs
  - Root CLAUDE.md references parent spec

**Resumability**:
- If manifest exists with partial completion, skip "pending" → ask user to continue
- Re-run only modules with status "pending" or "failed"
- Allows interruption recovery (idempotent)

**Output**: File manifest showing created/updated/failed modules

#### 3. Review Command Extension (MODIFICATION)

**Location**: `spiral-grove/commands/review.md` (existing file, add new mode)

**New mode**: `spec-vs-code` for drift detection

**Command usage**:
```
/review spec-vs-code [feature-name]
```

**Workflow**:
1. **Read spec**: Parse `.sdd/specs/[feature-name].md` acceptance criteria
2. **Analyze implementation**:
   - Use Glob to find feature's code files (heuristics: spec name → directory/namespace)
   - Use Grep to search for test files matching spec criteria
   - Read key implementation files
3. **Compare spec vs. reality**:
   - Extract spec acceptance criteria (numbered tests)
   - Extract actual test suite (test descriptions, assertions)
   - Categorize drift:
     - **Missing**: In spec, not in code (spec criterion has no matching test)
     - **Extra**: In code, not in spec (feature exists but not documented)
     - **Modified**: Behavior changed (test exists but assertions differ from spec)
4. **Calculate drift percentage**:
   - `drift% = (missing + extra + modified) / total_spec_criteria * 100`
5. **Present findings**:
   ```
   ## Spec-Code Drift Analysis: [feature-name]

   **Spec**: .sdd/specs/[feature-name].md
   **Status**: [spec-status]
   **Drift**: 15% (3/20 criteria)

   ### Missing (in spec, not implemented): 1
   - [ ] Acceptance Test 5: "Users can export preferences as JSON"
         → No matching test found in test suite

   ### Extra (implemented, not in spec): 2
   - [x] Feature: "Wishlist functionality"
         → Found in src/wishlist.js, tests in test/wishlist.test.js
   - [x] Feature: "Save for later"
         → Found in src/save-later.js

   ### Modified (behavior diverged): 0

   ### Recommendation:
   Drift detected (15%). Consider running `/spec-writing` to update spec:
   - Add "wishlist" and "save for later" to functional requirements
   - Remove unimplemented export feature or create task to implement
   ```
6. **Advisory only**: Do NOT modify spec (user must run `/spec-writing` manually)

**Integration with existing review modes**:
- Add new validation checklist section for `spec-vs-code`
- Preserve existing spec/plan/tasks/progress modes
- Use same frontmatter `argument-hint: [spec|plan|tasks|progress|spec-vs-code]`

#### 4. Module Manifest (NEW)

**Location**: `.sdd/module-manifest.json`

**Purpose**: Stateful resumability for documentation synthesis

**Schema**:
```json
{
  "generated_at": "ISO-8601 timestamp",
  "project_root": "absolute path to project",
  "modules": [
    {
      "path": "relative/path/to/module",
      "status": "pending | completed | failed",
      "claude_md_path": "relative/path/to/CLAUDE.md",
      "error": "optional error message if status=failed"
    }
  ]
}
```

**Lifecycle**:
- Created in Phase 1 (Discovery) before any generation
- Updated in Phase 2 (Generation) as each module completes
- Read on subsequent `/synthesize-docs` runs for resumption
- Committed to git for team coordination

#### 5. CLAUDE.md Files (NEW)

**Location**: `[module-dir]/CLAUDE.md` + root `CLAUDE.md`

**Format specification** (to be documented in `spiral-grove/docs/claude-md-format.md`):

**Module CLAUDE.md template**:
```markdown
# [Module Name]

**Origin**: Implemented from .sdd/specs/[feature-name].md *(added by SDD integration)*

## Purpose

[1-2 sentence description of what this module does]

## Key Components

### [Component 1 Name]
**File**: `path/to/file.ext`
**Purpose**: [What it does]

### [Component 2 Name]
...

## Public API

### Functions/Classes
- `functionName(params)` - Description
- `ClassName` - Description

### Exports
- What this module exports for other modules to use

## Integration Points

### Dependencies
- **[Module Name]**: How this module uses it
- **[External Library]**: What it provides

### Dependents
- **[Other Module]**: How it uses this module

## Common Operations

### [Operation 1]
```language
// Example code snippet
```

### [Operation 2]
...

## Testing

- **Test file**: `path/to/test.ext`
- **How to run**: `command to run tests`
- **Key test scenarios**: [List main test cases]

<!-- BEGIN: HAND-EDITED -->
<!-- Users can add custom sections here -->
<!-- END: HAND-EDITED -->
```

**Root CLAUDE.md template**:
```markdown
# [Project Name]

**Origin**: Implemented from .sdd/specs/[root-spec].md *(if applicable)*

## Overview

[Project purpose and high-level architecture]

## Directory Structure

```
project/
├── module-a/    - Description
├── module-b/    - Description
└── ...
```

## Module Index

- [module-a](./module-a/CLAUDE.md) - Brief description
- [module-b](./module-b/CLAUDE.md) - Brief description

## Getting Started

[Quick start instructions for new developers]

## Architecture

[High-level system design]

<!-- BEGIN: HAND-EDITED -->
<!-- Project-specific content -->
<!-- END: HAND-EDITED -->
```

**Hand-edited section preservation**:
- Any content between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->` is preserved verbatim
- Agent identifies markers, extracts content, merges after generating new content
- Prevents loss of human-added context (gotchas, tips, examples)

## Technical Decisions

### Decision 1: Agent vs. Inline Command Logic

**Context**: Documentation generation could be implemented as inline command logic or as a separate agent.

**Options Considered**:
- **Option A**: Inline logic in `/synthesize-docs` command
  - Pros: Simpler architecture (one component), easier to maintain
  - Cons: Not reusable outside Spiral Grove, hard to parallelize, command bloat
- **Option B**: Separate agent + orchestration command (chosen)
  - Pros: Reusable agent, parallel execution, clean separation, testable in isolation
  - Cons: More files, coordination complexity

**Decision**: Implement `module-doc-synthesizer` as standalone agent, `/synthesize-docs` as orchestrator

**Rationale**:
1. **Parallelization requirement**: Spec requires 100 modules in <5 minutes (spec line 26-27), impossible without parallel agents
2. **Reusability**: Agent can be used outside Spiral Grove for any project needing module docs
3. **Framework separation**: Spec explicitly states "Do NOT couple module-doc-synthesizer agent to Spiral Grove" (line 216)
4. **Isolation**: Agents can be spawned with isolated context (no cross-agent dependencies per spec line 186-187)
5. **Maintainability**: Agent focuses on single-module analysis, command handles orchestration

### Decision 2: Module Boundary Detection Algorithm

**Context**: Need to automatically detect logical module boundaries in diverse codebases (monorepos, microservices, libraries).

**Options Considered**:
- **Option A**: Language-specific detection (Python packages, JS modules, Go packages)
  - Pros: Precise boundaries, respects language conventions
  - Cons: Requires language parsers, not universal
- **Option B**: Directory-based heuristics with user approval (chosen)
  - Pros: Language-agnostic, simple, user validates
  - Cons: May miss nuanced boundaries, requires user review
- **Option C**: Manual manifest creation
  - Pros: Full user control, no heuristics errors
  - Cons: Tedious for 100+ modules, error-prone

**Decision**: Use directory-based heuristics with mandatory user approval before generation

**Rationale**:
1. **Language-agnostic**: Spiral Grove supports any project type (spec NFR line 164)
2. **User validation**: Spec requires "Module boundary detection asks for user confirmation" (line 193)
3. **Simplicity**: No need for language-specific parsers (aligns with "no executable code" principle)
4. **Editable manifest**: User can modify detected modules before generation starts
5. **Spec alignment**: "Do NOT enforce specific module granularity" (line 213)

**Heuristics** (applied in order):
1. Directories with package files (`package.json`, `setup.py`, `go.mod`, `Cargo.toml`)
2. Directories with 3+ source files + test directory
3. Subdirectories of `src/`, `lib/`, `modules/`, `packages/`
4. Exclude: `node_modules/`, `vendor/`, `.git/`, `dist/`, `build/`

### Decision 3: Agent Parallelization Strategy

**Context**: Need to process 100+ modules in <5 minutes (spec success criterion #3, line 26-27).

**Options Considered**:
- **Option A**: Sequential processing (one module at a time)
  - Pros: Simple, predictable resource usage
  - Cons: Too slow (~30 sec/module = 50 min for 100 modules)
- **Option B**: Batch parallelization (10 modules at a time)
  - Pros: Controlled concurrency, avoids overload
  - Cons: Still slow, requires queue management
- **Option C**: Full parallel spawning (all modules simultaneously) (chosen)
  - Pros: Fastest execution, leverages Claude Code's agent system
  - Cons: Higher initial resource spike, requires agent isolation

**Decision**: Spawn all module-doc-synthesizer agents in parallel using single message with multiple Task tool calls

**Rationale**:
1. **Performance requirement**: Spec mandates <5 minutes for 100 modules (line 26-27)
2. **Claude Code capability**: Task tool supports parallel agent spawning in single message
3. **Agent isolation**: Spec requires "Each agent operates independently with isolated context" (line 186-187)
4. **Resumability safety**: Manifest tracks failures for retry (idempotent)
5. **Precedent**: Parent spec guidance (line 151) emphasizes parallel tool calls when independent

**Implementation**: `/synthesize-docs` command constructs single response with 100+ Task tool calls, Claude Code runtime handles parallelization

### Decision 4: Manifest Format (JSON vs. Markdown)

**Context**: Need to store module list and status for resumability.

**Options Considered**:
- **Option A**: Markdown table in `.sdd/module-manifest.md`
  - Pros: Human-readable, git-friendly, consistent with `.sdd/` format
  - Cons: Harder to parse/update programmatically (via Claude)
- **Option B**: JSON in `.sdd/module-manifest.json` (chosen)
  - Pros: Structured data, easy to parse/update, standard format
  - Cons: Slightly less readable raw, deviation from markdown-only `.sdd/`
- **Option C**: Both (JSON for processing, markdown for display)
  - Pros: Best of both worlds
  - Cons: Sync complexity, redundant files

**Decision**: Use `.sdd/module-manifest.json` exclusively

**Rationale**:
1. **Programmatic access**: Commands need to read, filter, update status fields (easier with JSON)
2. **Spec requirement**: Spec line 250-259 explicitly defines JSON schema
3. **Resumability**: Idempotent updates require reliable parsing (JSON safer than markdown table)
4. **Precedent**: Configuration files (`.vscode/settings.json`, `package.json`) use JSON in git repos
5. **Acceptable deviation**: Technical context (line 224-260) overrides general markdown preference for this specific use case

### Decision 5: CLAUDE.md Conciseness Enforcement

**Context**: Spec requires CLAUDE.md files ≤400 lines (success criterion #1, line 23).

**Options Considered**:
- **Option A**: Strict truncation at 400 lines
  - Pros: Hard guarantee, simple validation
  - Cons: May cut mid-section, loses context
- **Option B**: Soft guideline with overflow warning
  - Pros: Preserves completeness, educates user
  - Cons: No enforcement, may creep over time
- **Option C**: Validation with retry (chosen)
  - Pros: Enforces limit, allows agent to self-correct
  - Cons: Requires retry logic

**Decision**: Agent validates ≤400 lines in step 6 of routine; if over, condense and retry once

**Rationale**:
1. **Spec requirement**: Success criterion #1 is measurable (≤400 lines), not advisory
2. **Context efficiency**: Spec NFR line 201 requires ≤5% context budget when loaded
3. **Self-correction**: Agent can identify verbose sections and condense (e.g., reduce examples, shorten descriptions)
4. **User override**: If still over after retry, present to user with warning (rare edge case)
5. **Quality over quantity**: Conciseness forces focus on operational essentials

**Condensing strategies** (agent applies if over 400 lines):
- Remove redundant examples (keep 1-2 most representative)
- Shorten component descriptions to 1 sentence
- Collapse similar sections (e.g., multiple similar functions → summary)
- Move extensive code snippets to hand-edited section (user can add back)

### Decision 6: Spec-Code Drift Detection Approach

**Context**: Need to detect when implementation diverges from spec without AST parsing or runtime analysis.

**Options Considered**:
- **Option A**: AST-based semantic analysis
  - Pros: Precise, understands code structure
  - Cons: Language-specific, complex, requires parsers
- **Option B**: Test suite comparison (chosen)
  - Pros: Language-agnostic, tests reflect actual behavior, maintainable
  - Cons: Only detects tested behavior (not untested changes)
- **Option C**: Manual code review
  - Pros: Human judgment, nuanced
  - Cons: Not automated, not scalable

**Decision**: Compare spec acceptance criteria against test suite descriptions and coverage

**Rationale**:
1. **Language-agnostic**: Works for any language with test files (spec NFR line 164)
2. **Spec alignment**: Acceptance tests map to implementation tests (parent spec line 45-48)
3. **Practical proxy**: If feature exists without test, it's untested anyway (should be flagged)
4. **Simple implementation**: Use Grep to find test files, Read to parse test descriptions
5. **<5% false positive**: Spec success criterion #4-5 (line 27-28) achievable with semantic matching (not just keyword search)

**Semantic matching approach**:
- Extract spec acceptance criteria (e.g., "Users can export preferences as JSON")
- Search test files for related tests (flexible matching: "export", "preferences", "JSON")
- Classify matches: Exact (same feature), Partial (related but different), None (missing)
- Identify extra tests not in spec (tests without matching criteria)

### Decision 7: SDD Integration Phase Design

**Context**: Need to link CLAUDE.md files back to their originating specs without breaking non-SDD usage.

**Options Considered**:
- **Option A**: Agent adds `**Origin**` field directly
  - Pros: Single pass, no extra phase
  - Cons: Agent needs SDD knowledge (violates separation), breaks non-SDD reusability
- **Option B**: Separate SDD integration phase in command (chosen)
  - Pros: Agent remains generic, command adds SDD context, clear separation
  - Cons: Extra processing pass (minimal cost)
- **Option C**: Optional parameter to agent
  - Pros: Flexible, single component
  - Cons: Agent must understand SDD concepts, parameter passing complexity

**Decision**: Agent generates pure CLAUDE.md, command adds `**Origin**` field in Phase 3

**Rationale**:
1. **Agent reusability**: Spec requirement "Do NOT couple module-doc-synthesizer agent to Spiral Grove" (line 216)
2. **Separation of concerns**: Agent does module analysis, command does SDD orchestration
3. **Test criterion**: Spec acceptance test #6 (line 337-343) validates standalone agent usage without `**Origin**`
4. **Minimal overhead**: Adding one line to existing CLAUDE.md is fast (<<5 min target)
5. **Future extensibility**: Other orchestrators (non-SDD) can use agent without modification

**Implementation**: Phase 3 reads each CLAUDE.md, inserts `**Origin**: ...` line after title, re-writes file

## Data Model

### Module Manifest Schema

**File**: `.sdd/module-manifest.json`

```typescript
interface ModuleManifest {
  generated_at: string;        // ISO-8601 timestamp
  project_root: string;         // Absolute path to project
  modules: ModuleEntry[];
}

interface ModuleEntry {
  path: string;                 // Relative path from project root
  status: "pending" | "completed" | "failed";
  claude_md_path: string;       // Where to write CLAUDE.md (relative)
  error?: string;               // Optional error message if failed
}
```

**Example**:
```json
{
  "generated_at": "2025-10-20T14:23:45Z",
  "project_root": "/home/user/my-project",
  "modules": [
    {
      "path": "src/authentication",
      "status": "completed",
      "claude_md_path": "src/authentication/CLAUDE.md"
    },
    {
      "path": "src/billing",
      "status": "failed",
      "claude_md_path": "src/billing/CLAUDE.md",
      "error": "No source files found in module"
    },
    {
      "path": "src/notifications",
      "status": "pending",
      "claude_md_path": "src/notifications/CLAUDE.md"
    }
  ]
}
```

### CLAUDE.md Document Schema

**File**: `[module-dir]/CLAUDE.md` or root `CLAUDE.md`

**Required sections**:
- Title (H1): Module/project name
- Origin (optional, added by SDD): Reference to source spec
- Purpose: 1-2 sentence overview
- Key Components: Main classes/functions/files
- Public API: Exported interfaces
- Integration Points: Dependencies and dependents
- Common Operations: Usage examples
- Testing: Test file locations and scenarios
- Hand-edited section: Custom user content (preserved on re-generation)

**Constraints**:
- Total length ≤400 lines
- Valid GitHub-flavored markdown
- Hand-edited sections enclosed in HTML comments

### Drift Analysis Report Schema

**Generated by**: `/review spec-vs-code [feature-name]`

**Output format**:
```markdown
## Spec-Code Drift Analysis: [feature-name]

**Spec**: .sdd/specs/[feature-name].md
**Status**: [spec-status]
**Drift**: [percentage]% ([count]/[total] criteria)

### Missing (in spec, not implemented): [count]
- [ ] Acceptance Test [N]: "[description]"
      → [finding]

### Extra (implemented, not in spec): [count]
- [x] Feature: "[description]"
      → Found in [files]

### Modified (behavior diverged): [count]
- [~] Acceptance Test [N]: "[original]"
      → Changed to: "[current]"

### Recommendation:
[Advisory message about whether to update spec]
```

**Drift percentage calculation**:
```
drift_percentage = ((missing + extra + modified) / total_spec_criteria) * 100
```

**Recommendation thresholds**:
- <10%: "Minor drift, no action needed"
- 10-20%: "Moderate drift, consider updating spec"
- >20%: "Significant drift, recommend running `/spec-writing`"

## API Design

### Module Documentation Synthesizer Agent API

**Invocation** (via Task tool):
```markdown
Analyze module at `[module-path]` and generate CLAUDE.md documentation (≤400 lines).

If existing CLAUDE.md at `[existing-claude-md-path]`, preserve hand-edited sections.

Module path: [relative/path/to/module]
Existing CLAUDE.md: [path/to/existing.md] *(optional)*
```

**Output** (agent returns as text):
```markdown
# [Module Name]

[Generated CLAUDE.md content following template]
```

**Error handling**:
- If module has no source files: Return error message
- If over 400 lines after retry: Return with warning
- If can't parse existing CLAUDE.md: Warn and regenerate fully

### Synthesize Documentation Command API

**Invocation**:
```
/synthesize-docs              # Full project
/synthesize-docs [scope]      # Specific scope (e.g., feature name)
```

**Phase 1 Output** (Module Discovery):
```
Detected 15 modules:
1. src/authentication (4 files, has tests)
2. src/billing (7 files, has tests)
...
15. src/utils (12 files, no dedicated tests)

Do you want to:
- Approve and continue
- Modify the list (add/remove modules)
- Cancel
```

**Phase 2 Output** (Parallel Generation):
```
Generating documentation for 15 modules...

[Progress indicators]
✓ src/authentication (completed)
✓ src/billing (completed)
✗ src/notifications (failed: no source files)
⏳ src/utils (in progress)
...

Status: 12/15 completed, 1 failed, 2 in progress
```

**Phase 3 Output** (SDD Integration):
```
Linking CLAUDE.md files to specs...

✓ src/authentication/CLAUDE.md → .sdd/specs/authentication.md
✓ src/billing/CLAUDE.md → .sdd/specs/billing.md
⚠ src/utils/CLAUDE.md (no matching spec found)
...
```

**Final Output**:
```
Documentation synthesis complete!

Generated 14 CLAUDE.md files:
- Root: CLAUDE.md
- Modules: 13 files (12 linked to specs, 1 no matching spec)

Failed modules (1):
- src/notifications: No source files found

Manifest saved to: .sdd/module-manifest.json
```

### Review Spec-vs-Code API

**Invocation**:
```
/review spec-vs-code [feature-name]
```

**Output**: Drift analysis report (see Data Model section above)

## Integration Points

### Internal Spiral Grove Systems

**Command system**:
- New command: `commands/synthesize-docs.md` (auto-discovered as `/spiral-grove:synthesize-docs`)
- Extended command: `commands/review.md` (add `spec-vs-code` mode to existing argument hint)

**Agent system** (NEW):
- New agent: `agents/module-doc-synthesizer.md` (auto-discovered as available agent)
- Invoked via Task tool with `subagent_type="module-doc-synthesizer"`

**Artifact storage**:
- New JSON file: `.sdd/module-manifest.json` (resumability state)
- New markdown files: `CLAUDE.md` files throughout codebase (generated docs)

**Existing workflows**:
- After `/implementation` completes: User runs `/synthesize-docs` (Development → Maintenance)
- Before `/spec-writing`: User runs `/review spec-vs-code` (Maintenance → Development)

### External Systems (No Direct Integration)

**Version control (Git)**:
- Manifest (`.sdd/module-manifest.json`) should be committed for team coordination
- CLAUDE.md files should be committed for persistent context
- Agent/command don't execute git commands (user commits manually)

**CI/CD**:
- Future: Could run `/review spec-vs-code` in CI to detect drift before merging
- No direct integration in MVP

**MCP servers**:
- No dependencies on specific MCPs
- Can be directed to use project-specific tools if available

## State Management

### Session Persistence

**Problem**: Documentation generation may be interrupted (timeout, error, user cancellation).

**Solution**: Manifest-based resumability

**Workflow**:
1. Phase 1 creates manifest with all modules status="pending"
2. Phase 2 updates status to "completed" or "failed" as each module finishes
3. If interrupted, manifest persists to disk
4. On re-run, command reads manifest:
   - If all completed: "Already done, re-run to regenerate?"
   - If partial: "Continue from where we left off? (X modules remaining)"
5. User approves, command processes only "pending" and "failed" modules

**Idempotency**:
- Re-running on completed modules regenerates CLAUDE.md (safe due to hand-edit preservation)
- Manifest timestamp updated on each run
- No duplicate modules (keyed by path)

### Hand-Edited Section Preservation

**Problem**: Users add custom content to CLAUDE.md (gotchas, tips), re-generation would lose it.

**Solution**: HTML comment markers

**Markers**:
```html
<!-- BEGIN: HAND-EDITED -->
[User-added content]
<!-- END: HAND-EDITED -->
```

**Agent routine** (step 2):
1. Read existing CLAUDE.md
2. Extract content between markers (regex: `<!-- BEGIN: HAND-EDITED -->.*?<!-- END: HAND-EDITED -->`)
3. Store extracted sections
4. Generate new content
5. Insert preserved sections at same location in new content
6. Validate no duplicate markers (error if nested/malformed)

**Constraints**:
- Only one pair of markers per CLAUDE.md
- Markers must be on own lines
- Content between markers is preserved verbatim (no modification)

## Error Handling Strategy

### Module Detection Errors

**Scenario**: Heuristics detect 0 modules (edge case: empty project, unconventional structure)

**Approach**:
```
No modules detected using standard heuristics.

This could mean:
- Project has unconventional structure
- No source files in standard directories (src/, lib/, etc.)

You can:
- Manually create .sdd/module-manifest.json with your modules
- Run synthesis on specific directory: /synthesize-docs src/my-module
- Adjust project structure to match conventions
```

**Implementation**: Command checks `modules.length === 0`, presents guidance

### Agent Spawn Failures

**Scenario**: Task tool fails to spawn agent (resource limits, Claude Code error)

**Approach**:
- Catch spawn errors per module
- Update manifest status to "failed" with error message
- Continue processing other modules (don't fail entire batch)
- Report failures at end:
  ```
  3 modules failed to generate:
  - src/module-a: Agent spawn timeout
  - src/module-b: Agent returned error
  - src/module-c: Module path not found

  To retry failures: /synthesize-docs (will process only failed modules)
  ```

### CLAUDE.md Over 400 Lines

**Scenario**: Agent generates 420-line CLAUDE.md (verbose module with many components)

**Approach** (agent step 6):
1. Validate line count
2. If >400:
   - Identify condensable sections (long code snippets, repetitive examples)
   - Apply condensing strategies (see Decision 5)
   - Retry validation
3. If still >400 after retry:
   - Return with warning:
     ```
     ⚠️ Warning: Generated CLAUDE.md is 420 lines (target: ≤400)

     Module `[module-name]` is complex with many components.

     Options:
     - Accept longer doc (may exceed context budget guideline)
     - Split module into smaller sub-modules
     - Manually edit to condense after generation
     ```

### Spec-Code Drift False Positives

**Scenario**: Test exists but description doesn't match spec wording (semantic match fails)

**Approach**:
- Use flexible matching (not exact string match):
  - Tokenize spec criteria (keywords: "export", "preferences", "JSON")
  - Search test descriptions for keyword combinations
  - Accept partial matches with confidence score
- Present matches with confidence:
  ```
  ### Possible match (75% confidence):
  - Spec: "Users can export preferences as JSON"
  - Test: `test('should export user settings to JSON format', ...)`
  - Match score: 3/4 keywords

  If this is a match, no action needed. If false positive, run /spec-writing to clarify.
  ```
- Spec success criterion #4: <5% false positive rate (achievable with semantic matching)

### Missing Spec for Module

**Scenario**: Phase 3 tries to link CLAUDE.md to spec, but no matching spec exists

**Approach**:
```
⚠️ Module `src/utils` has no matching spec in .sdd/specs/

This could mean:
- Module is a utility/helper (doesn't need spec)
- Spec exists but named differently (check .sdd/specs/ manually)
- Module implemented without SDD workflow

CLAUDE.md generated without **Origin** field.
```

**Implementation**: Phase 3 attempts fuzzy match (module path → spec name), if no match, skip `**Origin**` addition

## Performance Considerations

### Parallel Agent Scalability

**Target**: 100 modules in <5 minutes (spec success criterion #3, line 26-27)

**Analysis**:
- Serial processing: ~30 sec/module = 50 min for 100 (unacceptable)
- Parallel processing: All 100 spawn simultaneously
  - Bottleneck: Claude Code's Task tool throughput
  - Assumption: 100 agents can run concurrently (Claude infrastructure capacity)
  - Per-agent time: 20-40 sec (code analysis + generation)
  - Total time: ~40 sec (longest agent) + 20 sec (orchestration overhead) = ~60 sec

**Mitigation if over 5 min**:
- Batch spawning: 50 agents at a time (2 batches = 2-3 min total)
- Resumability: If timeout, manifest tracks completion for retry

**Monitoring**: Track timestamps in manifest for performance regression detection

### Context Window Efficiency

**Target**: CLAUDE.md files consume ≤5% of context budget when loaded (spec NFR line 201)

**Analysis**:
- Context budget: ~200K tokens (Claude Sonnet 4.5)
- 5% budget: ~10K tokens
- 400 lines markdown ≈ 2K tokens (avg 5 tokens/line)
- 5 CLAUDE.md files loaded: 2K × 5 = 10K tokens ✓

**Validation**: Agent enforces ≤400 lines in step 6 (see Decision 5)

### Manifest File Size

**Target**: Manifest should not become unwieldy for large projects (1000+ modules)

**Analysis**:
- 1000 modules × 200 bytes/entry = ~200KB JSON file
- Git-friendly: Diffs show status changes clearly
- Parseable: Claude can read/update 200KB JSON efficiently

**Optimization** (if needed later):
- Compress completed modules to single count: `"completed": 950`
- Keep only pending/failed with details

## Security Design

### No Sensitive Data in CLAUDE.md

**Policy**: CLAUDE.md files document code structure, not secrets

**Agent guidance** (in prompt):
- Do NOT include API keys, credentials, or secrets in examples
- If code contains secrets, sanitize in documentation (e.g., `api_key="***"`)
- Link to environment variable usage, don't show values

**User responsibility**: Developers manage secrets via `.env` files (excluded from CLAUDE.md)

### Manifest File Safety

**Policy**: `.sdd/module-manifest.json` contains paths, not code or secrets

**Safe to commit**: Manifest only stores module paths and status (no sensitive data)

**User control**: Developers can add manifest to `.gitignore` if desired (prevents team coordination)

## Testing Strategy

### Agent Testing

**Approach**: Standalone invocation (without Spiral Grove context)

**Test Case 1**: Generate CLAUDE.md for simple module
- Input: Path to module with 3 files (1 main, 1 test, 1 helper)
- Expected output: CLAUDE.md ≤400 lines with all required sections
- Validation: Sections present, line count valid, markdown valid

**Test Case 2**: Preserve hand-edited sections
- Setup: Existing CLAUDE.md with `<!-- BEGIN: HAND-EDITED -->` content
- Input: Regenerate for same module after code changes
- Expected output: Hand-edited section preserved verbatim, new components added
- Validation: Hand-edited content identical, new sections reflect changes

**Test Case 3**: Handle over-400-line module
- Input: Complex module with 20+ components
- Expected output: Agent condenses to ≤400 lines or returns warning
- Validation: Line count ≤400 or warning message present

### Command Testing

**Test Case 4**: Full project synthesis (acceptance test #1, spec line 268-278)
- Setup: Project with 10 modules across 3 subsystems
- Run: `/synthesize-docs`
- Validate:
  - Phase 1: Detects 10 modules, saves manifest
  - Phase 2: Spawns 10 agents, generates 11 CLAUDE.md files (10 modules + 1 root)
  - Phase 3: Links CLAUDE.md to specs (matches by path)
  - Completion: <1 minute (well under 5-min target for 10 modules)

**Test Case 5**: Resumability after interruption (acceptance test #5, spec line 324-333)
- Setup: Manifest with 5 modules (3 completed, 2 pending)
- Run: `/synthesize-docs` (simulated re-run)
- Validate:
  - Command detects partial completion
  - Skips 3 completed modules
  - Processes only 2 pending modules
  - Final output: 5/5 completed (3 existing + 2 new)

**Test Case 6**: Spec-code drift detection (acceptance test #3, spec line 298-305)
- Setup: Spec with 8 criteria, implementation with 10 features (2 extra)
- Run: `/review spec-vs-code [feature-name]`
- Validate:
  - Report shows: 0 Missing, 2 Extra, 0 Modified
  - Drift: 20% (2/10)
  - Recommendation: "Consider running `/spec-writing`"
  - No automatic spec changes

### Integration Testing

**Test Case 7**: Development-Maintenance-Development cycle (acceptance test #4, spec line 310-321)
- Phase 1: Complete feature implementation
- Phase 2: Run `/synthesize-docs` → generates CLAUDE.md
- Phase 3: Make bug fixes (code evolves, spec unchanged)
- Phase 4: Run `/review spec-vs-code` → detects 15% drift
- Phase 5: Run `/spec-writing` → user updates spec to reflect reality
- Validate: Full cycle works, specs stay synchronized with code

### Manual Validation

**CLAUDE.md quality**:
- Readability: Human developer can understand module from CLAUDE.md alone
- Completeness: All public APIs documented
- Accuracy: Documentation matches actual code behavior
- Conciseness: ≤400 lines, no redundancy

**Drift detection accuracy**:
- Run on 10 features with known drift
- Measure false positives: Target <5% (spec success criterion #4, line 27)
- Validate categorization: Missing/Extra/Modified correctly classified

## Deployment Considerations

### Plugin Structure Update

**New files**:
- `spiral-grove/agents/module-doc-synthesizer.md` (agent definition)
- `spiral-grove/commands/synthesize-docs.md` (command definition)
- `spiral-grove/docs/claude-md-format.md` (documentation)

**Modified files**:
- `spiral-grove/commands/review.md` (add `spec-vs-code` mode)
- `spiral-grove/.claude-plugin/plugin.json` (version bump to 0.3.0)

**Directory structure** (after implementation):
```
spiral-grove/
├── .claude-plugin/
│   └── plugin.json (v0.3.0)
├── agents/
│   └── module-doc-synthesizer.md (NEW)
├── commands/
│   ├── synthesize-docs.md (NEW)
│   ├── review.md (MODIFIED)
│   └── [existing commands]
├── docs/
│   └── claude-md-format.md (NEW)
└── skills/
    └── [existing skills]
```

### Versioning Strategy

**Version bump**: 0.2.0 → 0.3.0 (minor version, new features)

**Changelog**:
```
## v0.3.0 - Documentation Synthesis

### Added
- `/synthesize-docs` command for generating CLAUDE.md operational docs
- `module-doc-synthesizer` agent for module-level documentation
- `/review spec-vs-code` mode for spec-code drift detection
- `.sdd/module-manifest.json` for resumable generation
- CLAUDE.md format specification

### Changed
- Extended `/review` command with new `spec-vs-code` argument

### Performance
- Supports 100+ module projects with parallel agent execution (<5 min)
```

### Rollback Plan

**If documentation synthesis introduces issues**:
1. Revert git commits (CLAUDE.md files and manifest)
2. Checkout previous plugin version: `git checkout v0.2.0 -- spiral-grove/`
3. No data corruption risk (all artifacts are markdown/JSON files)
4. Existing `.sdd/` artifacts (specs, plans, tasks, progress) unaffected

**User safety**: Documentation synthesis is additive (doesn't modify existing workflows)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Agent parallelization exceeds Claude Code limits** | Medium | High | Implement batch spawning (50 at a time) as fallback; manifest enables resumability |
| **Module detection heuristics miss boundaries** | Medium | Medium | Mandatory user approval before generation; editable manifest; document heuristics clearly |
| **CLAUDE.md files exceed 400 lines frequently** | Low | Medium | Agent condensing strategies; validation with retry; warn user to split modules |
| **Hand-edited section markers malformed/nested** | Low | Low | Agent validates markers before processing; error on malformed; document format in `claude-md-format.md` |
| **Spec-code drift detection high false positive rate** | Medium | Medium | Semantic matching (not keyword-only); confidence scores; <5% target via testing |
| **SDD integration phase breaks non-SDD usage** | Low | High | Test standalone agent separately; keep agent generic (no SDD knowledge) |
| **Manifest file merge conflicts** | Medium | Low | JSON diffs are readable; document merge strategy; consider last-write-wins for status |
| **Context overflow with many CLAUDE.md files** | Low | Medium | Enforce ≤400 lines; validate 5% context budget; document loading strategy |

## Dependencies

### Technical Dependencies

**Claude Code platform**:
- Version: Current (agent system with Task tool support)
- Features used: Slash commands, Task tool for agent spawning, parallel execution

**No new external dependencies**: Pure markdown agents/commands

**System requirements**:
- Filesystem write access for CLAUDE.md files and manifest
- No language-specific tools (language-agnostic)

### Team Dependencies

**None**: Solo developer project (Ronald Roy)

**Future**: Community contributions welcome (agent templates, condensing strategies)

## Timeline Estimate

### Phase 1: Agent Implementation (4-6 hours)
- Create `agents/module-doc-synthesizer.md` agent definition
- Implement 7-step routine with CLAUDE.md template
- Add hand-edit preservation logic
- Add ≤400 line validation with condensing
- Test standalone agent on sample modules

### Phase 2: Synthesize-Docs Command (6-8 hours)
- Create `commands/synthesize-docs.md` command definition
- Implement Phase 1 (module detection heuristics, manifest creation)
- Implement Phase 2 (parallel agent spawning, status tracking)
- Implement Phase 3 (SDD integration, spec linking)
- Add resumability logic (read manifest, skip completed)
- Test on multi-module project

### Phase 3: Review Extension (3-4 hours)
- Extend `commands/review.md` with `spec-vs-code` mode
- Implement spec parsing (acceptance criteria extraction)
- Implement test suite analysis (find tests, match to criteria)
- Implement drift categorization (Missing/Extra/Modified)
- Add drift percentage calculation and recommendation logic
- Test on features with known drift

### Phase 4: Documentation (2-3 hours)
- Create `docs/claude-md-format.md` specification
- Document CLAUDE.md template and conventions
- Document hand-edited section markers
- Update parent Spiral Grove docs with new commands
- Update skill guide with lifecycle workflows

### Phase 5: Integration Testing (3-4 hours)
- Run acceptance tests 1-7 (spec lines 268-370)
- Test on vibe-garden repository (dogfooding)
- Validate performance targets (100 modules <5 min)
- Validate drift detection accuracy (<5% false positives)
- Fix any discovered issues

### Phase 6: Plugin Metadata & Release (1-2 hours)
- Update `plugin.json` to v0.3.0
- Write changelog
- Create example `.sdd/module-manifest.json` for documentation
- Git commit and tag release

**Total estimate**: 19-27 hours (approximately 2.5-3.5 development days)

## Open Questions

All questions from spec have been resolved through technical decisions:

- [x] **Should `/synthesize-docs` support custom module detection rules?**
  - **Decision**: Not in MVP; use heuristics + user approval (Decision 2)
  - **Future**: Could add `.sdd/module-detection-rules.json` for custom patterns

- [x] **How should we handle specs that have no corresponding code?**
  - **Decision**: `/review spec-vs-code` detects this as "Missing" drift (all criteria unmapped)
  - **Implementation**: No special handling needed; standard drift detection covers it

- [x] **Should module-doc-synthesizer agent have configurable templates?**
  - **Decision**: Not in MVP; use single template for consistency (Decision 5)
  - **Future**: Could add template selection via agent parameter

- [x] **Should manifest track partial completion within a module?**
  - **Decision**: No; module is atomic unit (either completed or failed)
  - **Rationale**: Simplifies resumability; failed modules can be retried fully

## Appendix

### Existing Code Analysis

**Command prompt patterns** (from `review.md`, `implementation.md`):
1. YAML frontmatter with `description` and `argument-hint`
2. "You are now in X Mode" header
3. "Your Focus" section with bullet points
4. "Prerequisites" with verification steps
5. "Behavior Guidelines" with numbered rules
6. "Workflow" or phase-specific instructions
7. Templates and examples

**Reusable utilities**:
- Glob for finding files by pattern
- Grep for searching code content
- Read for analyzing file contents
- Task tool for spawning agents (existing Spiral Grove commands use this)

**Anti-patterns to avoid**:
- Don't hardcode file paths (use Glob to discover)
- Don't assume specific languages (remain agnostic)
- Don't execute git commands (user commits manually)
- Don't modify specs automatically (advisory only)

### Agent System Reference

**Agent file structure** (based on Claude Code plugin spec):
```markdown
---
description: One-line description of agent purpose
capabilities:
  - capability-1
  - capability-2
---

# Agent Name

[Agent system prompt with role, guidelines, routine, output format]
```

**Invocation via Task tool**:
```markdown
Use Task tool with:
- subagent_type: "module-doc-synthesizer" (matches filename without .md)
- prompt: "Detailed task description with parameters"
- description: "Short 3-5 word task name"
```

**Parallel spawning**:
```markdown
Send single message with multiple Task tool uses:
- Task 1: Module A
- Task 2: Module B
- Task 3: Module C
Claude Code runtime executes in parallel
```

### Similar Patterns in Ecosystem

**Documentation generation**:
- JSDoc (JavaScript): Inline comments → docs (language-specific)
- Sphinx (Python): Docstrings → docs (language-specific)
- Rustdoc (Rust): Doc comments → docs (language-specific)
- **Difference**: module-doc-synthesizer is language-agnostic (analyzes code structure, not comments)

**Module detection**:
- Lerna (JavaScript monorepos): package.json detection
- Go modules: go.mod detection
- **Difference**: Our heuristics work across all languages (directory-based)

**State management**:
- Terraform state files: JSON for infrastructure state
- Kubernetes manifests: YAML for cluster state
- **Similarity**: `.sdd/module-manifest.json` tracks generation state

### CLAUDE.md Format Rationale

**Why CLAUDE.md specifically**:
1. **Convention**: Established pattern in Claude Code ecosystem (like README.md)
2. **Always-loaded**: Claude Code auto-loads CLAUDE.md files for context
3. **Hierarchy**: Supports nested CLAUDE.md (module-level + root-level)
4. **Purpose**: Operational docs (how to work with code) vs. specs (what to build)

**Conciseness target (≤400 lines)**:
- **Context budget**: 5% of 200K tokens = ~10K tokens
- **Token ratio**: ~5 tokens/line (markdown with code examples)
- **Calculation**: 400 lines × 5 tokens/line = 2K tokens/file → 5 files = 10K tokens ✓
- **Practical**: Fits on 1-2 screens, quick to scan

---

## Validation Checklist

Before marking this plan as approved:
- [x] All spec requirements are addressed in the plan
- [x] Existing codebase patterns have been analyzed (command prompts, agent invocation)
- [x] Technical decisions have documented rationales (7 decisions)
- [x] Integration points are clearly defined (agents, commands, manifest, CLAUDE.md)
- [x] Security and performance are addressed (no secrets, parallelization, context budget)
- [x] Testing strategy is defined (7 test cases covering acceptance tests)
- [x] Risks are identified with mitigations (7 risks)
- [x] Data model supports all use cases (manifest, CLAUDE.md, drift reports)
- [x] Parent plan context incorporated (follows SDD principles, markdown-based)
- [x] Child spec fully planned (all functional requirements mapped to components)

## Next Steps

Once this plan is approved, use `/spiral-grove:task-breakdown` to decompose the architecture into implementable tasks for:
1. Creating `agents/module-doc-synthesizer.md`
2. Creating `commands/synthesize-docs.md`
3. Extending `commands/review.md` with `spec-vs-code` mode
4. Creating `docs/claude-md-format.md` documentation
5. Testing and validation
6. Plugin metadata updates and release
