# Documentation Synthesis Feature - Technical Plan

**Specification**: [../../specs/spiral-grove/documentation-synthesis.md](../../specs/spiral-grove/documentation-synthesis.md)
**Parent Plan**: [../spiral-grove-plan.md](../spiral-grove-plan.md)
**Version**: 2.0.0
**Status**: Draft
**Created**: 2025-10-20
**Last Updated**: 2025-10-20

## Overview

Documentation Synthesis extends Spiral Grove with bidirectional lifecycle management between development (`.sdd/` specs) and maintenance (`CLAUDE.md` files). The architecture uses **parallel agent orchestration** for scalability (100+ modules in <5 minutes), **stateful resumability** via JSON manifests, and **semantic drift detection** through test suite comparison. Core principle: **agent-command separation** - the `module-doc-synthesizer` agent is framework-agnostic and reusable, while the `/synthesize-docs` command adds SDD-specific orchestration.

## Architecture

### System Context

Documentation Synthesis operates as extension to Spiral Grove plugin:

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
│  └───────────┼──────────────────┼───────────────────────┘   │
│              ▼                  ▼                           │
│        Orchestrates       Spawns in parallel                │
└──────────────┬──────────────────────────────────────────────┘
               │
               ▼
    ┌──────────────────────────────┐
    │  Filesystem Artifacts        │
    │  ├── .sdd/module-manifest.json (resumability state)
    │  └── CLAUDE.md files         │ (generated docs)
    └──────────────────────────────┘
```

**Key characteristics:**
- No new runtime dependencies (pure markdown agents/commands)
- Parallel execution via Claude Code's Task tool
- Stateful resumability for interruption recovery
- Bidirectional: Development → Maintenance (synthesize), Maintenance → Development (review spec-vs-code)

### Components

#### 1. Module Documentation Synthesizer Agent (NEW)
**File**: `spiral-grove/agents/module-doc-synthesizer.md`

Standalone agent that analyzes a single module and generates/updates CLAUDE.md (≤400 lines). Framework-agnostic, spawnnable in parallel, idempotent, preserves hand-edited sections via `<!-- BEGIN/END: HAND-EDITED -->` markers.

**Responsibilities:**
- Analyze module code, tests, comments (Read, Glob, Grep)
- Generate structured CLAUDE.md: Purpose, Key Components, Public API, Integration Points, Common Operations, Testing
- Preserve existing hand-edited sections when updating
- Validate ≤400 lines; if over, condense and retry once

#### 2. Synthesize Documentation Command (NEW)
**File**: `spiral-grove/commands/synthesize-docs.md`

Orchestrates documentation generation across project by spawning `module-doc-synthesizer` agents.

**Three-phase workflow:**
1. **Module Discovery**: Scan codebase for module boundaries (heuristics: package files, 3+ source files + tests, standard dirs). Present to user for approval. Save to `.sdd/module-manifest.json`.
2. **Parallel Generation**: Spawn one `module-doc-synthesizer` agent per module via Task tool (`subagent_type: "module-doc-synthesizer"`). Write agent-returned markdown to `[module]/CLAUDE.md`. Track status in manifest (pending → completed/failed). Generate root CLAUDE.md with project overview and module index.
3. **SDD Integration**: Match modules to specs by path. Add `**Origin**: .sdd/specs/[name].md` reference to CLAUDE.md header. Handle parent/child spec hierarchies.

**Resumability**: Read manifest on re-run; process only pending/failed modules.

#### 3. Review Command Extension (MODIFY)
**File**: `spiral-grove/commands/review.md` (add new mode)

New mode: `/review spec-vs-code [feature-name]` for drift detection.

**Approach:**
- Read spec acceptance criteria
- Analyze implementation via test suite comparison
- Categorize drift: Missing (in spec, not code), Extra (in code, not spec), Modified (behavior changed)
- Calculate drift percentage: `(missing + extra + modified) / total_spec_criteria * 100`
- Present findings with recommendations (advisory only - no auto-updates)

#### 4. Module Manifest (NEW)
**File**: `.sdd/module-manifest.json`

JSON manifest for resumability:
```json
{
  "generated_at": "ISO-8601 timestamp",
  "project_root": "absolute path",
  "modules": [
    {"path": "relative/path", "status": "pending|completed|failed", "claude_md_path": "path", "error": "optional"}
  ]
}
```

Created in Phase 1, updated in Phase 2, read on subsequent runs. Committed to git for coordination.

#### 5. CLAUDE.md Files (NEW)
**Files**: `[module-dir]/CLAUDE.md` + root `CLAUDE.md`

Structured markdown with required sections: Title, Origin (optional), Purpose, Key Components, Public API, Integration Points, Common Operations, Testing, Hand-edited section.

**Constraints:** ≤400 lines, valid GitHub-flavored markdown, hand-edited sections preserved verbatim.

Format specification to be documented in `spiral-grove/docs/claude-md-format.md`.

## Technical Decisions

### Decision 1: Agent vs. Inline Command Logic

**Choice**: Separate `module-doc-synthesizer` agent + `/synthesize-docs` orchestrator

**Rationale**: Parallelization requirement (100 modules in <5 minutes) impossible without parallel agents. Agent reusable outside Spiral Grove. Spec explicitly states "Do NOT couple agent to Spiral Grove." Clean separation: agent handles module analysis, command handles SDD orchestration.

### Decision 2: Module Boundary Detection

**Choice**: Directory-based heuristics with mandatory user approval

**Rationale**: Language-agnostic (works for any project type). Spec requires user confirmation. No language-specific parsers needed. Editable manifest before generation. Heuristics: package files, 3+ source files + tests, standard dirs (src/, lib/), exclude (node_modules/, .git/).

### Decision 3: Agent Parallelization

**Choice**: Spawn all agents in parallel (single message with multiple Task tool calls)

**Rationale**: Performance requirement (<5 minutes for 100 modules). Claude Code supports parallel spawning. Agent isolation per spec. Manifest tracks failures for retry. Estimated time: ~60 sec (40 sec longest agent + 20 sec orchestration).

### Decision 4: Manifest Format

**Choice**: JSON (`.sdd/module-manifest.json`)

**Rationale**: Easier programmatic parsing/updates. Spec explicitly defines JSON schema. Idempotent updates require reliable parsing. Standard configuration format. Acceptable deviation from markdown-only `.sdd/` given technical requirements.

### Decision 5: CLAUDE.md Conciseness

**Choice**: Agent validates ≤400 lines; if over, condense and retry once

**Rationale**: Spec success criterion #1 is measurable (≤400 lines). Context efficiency requirement (≤5% budget). Agent self-corrects by removing redundant examples, shortening descriptions, collapsing similar sections. User override if still over after retry (rare).

### Decision 6: Drift Detection Approach

**Choice**: Test suite comparison (not AST parsing)

**Rationale**: Language-agnostic. Tests reflect actual behavior. Acceptance tests map to implementation tests. Simple implementation via Grep + Read. <5% false positive rate achievable with semantic matching (tokenize spec criteria, flexible keyword search, confidence scores).

### Decision 7: SDD Integration Phase

**Choice**: Agent generates pure CLAUDE.md, command adds `**Origin**` in Phase 3

**Rationale**: Agent reusability (no SDD knowledge). Separation of concerns. Spec acceptance test #6 validates standalone usage. Minimal overhead (one line insertion). Future extensibility for non-SDD orchestrators.

## Data Model

### Module Manifest
**File**: `.sdd/module-manifest.json`

```typescript
interface ModuleManifest {
  generated_at: string;        // ISO-8601
  project_root: string;         // Absolute path
  modules: ModuleEntry[];
}

interface ModuleEntry {
  path: string;                 // Relative from project root
  status: "pending" | "completed" | "failed";
  claude_md_path: string;       // Relative
  error?: string;               // If failed
}
```

### CLAUDE.md Schema
Required sections: Title, Origin (optional), Purpose, Key Components, Public API, Integration Points, Common Operations, Testing, Hand-edited.

Constraints: ≤400 lines, valid markdown, hand-edited sections in `<!-- BEGIN/END: HAND-EDITED -->` markers.

### Drift Analysis Report
Output: Categorized drift (Missing/Extra/Modified), drift percentage, specific examples, recommendations.

Thresholds: <10% minor, 10-20% moderate, >20% significant (recommend `/spec-writing`).

## Integration Points

### Internal Spiral Grove
- **Commands**: New `synthesize-docs.md` (uses `module-doc-synthesizer` agent), extended `review.md`
- **Agents**: New `module-doc-synthesizer.md` (invoked via Task tool by `synthesize-docs` command)
- **Artifacts**: `.sdd/module-manifest.json`, CLAUDE.md files throughout codebase
- **Workflows**: After `/implementation` → `/synthesize-docs` (spawns agents); Before `/spec-writing` → `/review spec-vs-code`

### External Systems
- **Git**: Manifest and CLAUDE.md files committed manually (no auto-commits)
- **CI/CD**: Future integration for drift detection (not MVP)
- **MCPs**: No dependencies

## Error Handling, Performance, Security

### Error Handling
- **No modules detected**: Guide user to manual manifest or specific directory synthesis
- **Agent spawn failures**: Update manifest to "failed", continue other modules, report at end
- **Over 400 lines**: Agent condenses and retries; if still over, return with warning
- **Drift false positives**: Semantic matching with confidence scores (<5% target)
- **Missing spec**: Skip `**Origin**` addition, warn user

### Performance
- **Target**: 100 modules in <5 minutes via parallel spawning
- **Analysis**: 100 agents simultaneously, ~40 sec longest agent + 20 sec orchestration = ~60 sec
- **Mitigation**: Batch spawning (50 at a time) if over 5 min; resumability via manifest
- **Context efficiency**: 400 lines ≈ 2K tokens; 5 files = 10K tokens (≤5% of 200K budget)

### Security
- **CLAUDE.md content**: No API keys, credentials, or secrets in examples (sanitize if present)
- **Manifest safety**: Only stores paths and status (no sensitive data)
- **User control**: Can add manifest to `.gitignore` if desired

## Testing Strategy

### Agent Testing
1. Generate CLAUDE.md for simple module (3 files) - validate structure, ≤400 lines
2. Preserve hand-edited sections during update - verify verbatim preservation
3. Handle over-400-line module - verify condensation or warning

### Command Testing
4. Full project synthesis (10 modules) - validate 3 phases, <1 min, manifest saved
5. Resumability after interruption - skip completed, process pending only
6. Spec-code drift detection - categorize drift correctly, calculate percentage, no auto-updates

### Integration Testing
7. Development-Maintenance-Development cycle - synthesize → drift detection → spec update

### Manual Validation
- CLAUDE.md quality: readability, completeness, accuracy, conciseness
- Drift detection: <5% false positive rate, correct categorization

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent parallelization exceeds limits | Medium | High | Batch spawning fallback; resumability |
| Module detection misses boundaries | Medium | Medium | User approval; editable manifest |
| CLAUDE.md exceeds 400 lines | Low | Medium | Agent condensing; validation with retry |
| Drift detection false positives | Medium | Medium | Semantic matching; confidence scores |
| SDD integration breaks non-SDD usage | Low | High | Test standalone agent separately |

## Dependencies

### Technical
- Claude Code platform (agent system, Task tool, parallel execution)
- No new external dependencies (pure markdown agents/commands)
- Filesystem write access

### Team
None (solo developer: Ronald Roy)

## Deployment

### Plugin Structure
**New files:**
- `spiral-grove/agents/module-doc-synthesizer.md`
- `spiral-grove/commands/synthesize-docs.md`
- `spiral-grove/docs/claude-md-format.md`

**Modified files:**
- `spiral-grove/commands/review.md` (add `spec-vs-code` mode)
- `spiral-grove/.claude-plugin/plugin.json` (version 0.2.0 → 0.3.0)

### Versioning
Version bump: 0.2.0 → 0.3.0 (minor, new features)

Changelog:
- Added: `/synthesize-docs` command, `module-doc-synthesizer` agent, `/review spec-vs-code` mode, manifest, format spec
- Changed: Extended `/review` command
- Performance: 100+ module support (<5 min)

### Rollback
Revert git commits; checkout v0.2.0; no data corruption risk (markdown/JSON only); existing `.sdd/` unaffected.

## Validation Checklist

- [x] All spec requirements addressed
- [x] Existing codebase patterns analyzed
- [x] Technical decisions have rationales (7 decisions)
- [x] Integration points defined
- [x] Security and performance addressed
- [x] Testing strategy defined (7 test cases)
- [x] Risks identified with mitigations
- [x] Data model supports use cases
- [x] Parent plan context incorporated
- [x] Child spec fully planned

## Next Steps

Once approved, use `/spiral-grove:task-breakdown` to decompose into implementable tasks:
1. Create `agents/module-doc-synthesizer.md`
2. Create `commands/synthesize-docs.md`
3. Extend `commands/review.md` with `spec-vs-code` mode
4. Create `docs/claude-md-format.md`
5. Testing and validation
6. Plugin metadata updates and release
