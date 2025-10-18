# Spiral Grove: Spec-Driven Development Plugin - Technical Plan

**Specification**: `.sdd/specs/spiral-grove.md`
**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-18
**Last Updated**: 2025-10-18

## Overview

Spiral Grove is a Claude Code plugin that transforms AI-assisted development from ad-hoc prompting into a structured four-phase workflow. The technical approach centers on **markdown-based command prompts** that guide Claude's behavior through distinct cognitive modes (specification writing, planning, task breakdown, and implementation), with **filesystem-based state management** using `.sdd/` directory artifacts for session persistence and resumability.

The architecture is intentionally **execution-free** (no code except validation scripts) to maximize portability, maintainability, and flexibility across project types.

## Current State & Gaps

### What Exists
- ✅ Four core phase commands: `spec-writing.md`, `plan-generation.md`, `task-breakdown.md`, `implementation.md`
- ✅ Complete skill system with `spiral-grove-guide` and reference materials
- ✅ Plugin metadata and registration (`plugin.json`)
- ✅ Well-structured command prompt patterns with templates and checklists

### What's Missing
- ❌ **`/review [phase]` command** - Meta phase for validating documents (specified in spec but not implemented)
- ❌ **Parent/child specification hierarchy** - Designed in spec (lines 131-137) but not implemented in commands
- ⚠️ **`implementation.md` exceeds 300-line limit** - Currently 364 lines vs. 300 max (needs refactoring)

### Implementation Priority
1. `/review` command - Blocks full workflow validation
2. Parent/child hierarchy - Enables large project scalability (spec acceptance test #5)
3. `implementation.md` refactoring - Required for spec compliance

## Architecture

### System Context

Spiral Grove operates entirely within the Claude Code plugin ecosystem:

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code CLI                       │
│  ┌───────────────────────────────────────────────────┐  │
│  │            Spiral Grove Plugin                    │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │  │
│  │  │  Commands   │  │   Skills    │  │ Metadata │ │  │
│  │  │  (/spec-*)  │  │  (guide)    │  │ (plugin  │ │  │
│  │  │             │  │             │  │  .json)  │ │  │
│  │  └─────────────┘  └─────────────┘  └──────────┘ │  │
│  └───────────────────────────────────────────────────┘  │
│                          ↓                               │
│              Reads/writes to filesystem                  │
└──────────────────────────┬──────────────────────────────┘
                           ↓
                  ┌────────────────┐
                  │  .sdd/ directory│
                  │  ├── specs/     │
                  │  ├── plans/     │
                  │  ├── tasks/     │
                  │  └── progress/  │
                  └────────────────┘
```

**External interactions:**
- **No runtime dependencies**: Pure markdown prompts, no npm packages or Python libraries
- **Project-agnostic**: Works with any programming language or framework
- **User direction for integrations**: Can be directed to use project-specific MCPs (e.g., issue trackers, deployment tools) without hardcoding dependencies
- **Version control friendly**: All artifacts are markdown files suitable for git commits

### Component Overview

#### 1. Command Prompts (Primary Implementation)

**Location**: `spiral-grove/commands/`

**Existing commands:**
- `spec-writing.md` (159 lines) - Guides specification creation
- `plan-generation.md` (248 lines) - Drives architectural planning
- `task-breakdown.md` (281 lines) - Facilitates task decomposition
- `implementation.md` (364 lines) - Manages implementation execution

**Missing command** (per spec Meta Phase):
- `review.md` - Validates phase documents before progression

**Architecture pattern**: Each command is a self-contained behavioral prompt that:
1. Sets Claude's cognitive mode ("You are now in X mode")
2. Defines focus areas and responsibilities
3. Establishes behavioral guidelines and constraints
4. Provides output format templates
5. Includes validation checklists
6. Guides workflow progression

**Key constraint**: Commands must stay ≤300 lines (excluding reference materials) per spec NFR

#### 2. Skills System

**Location**: `spiral-grove/skills/spiral-grove-guide/`

**Purpose**: Provide methodology guidance and theoretical foundations

**Components**:
- `SKILL.md` - Main skill interface with usage guidance
- `references/SDD-QUICK-REFERENCE.md` - Operational quick lookup
- `references/SDD-FOUNDATIONS.md` - Theoretical and academic grounding

**Usage pattern**: Invoked via Claude Code's skill system when users need SDD methodology guidance

#### 3. Artifact Storage

**Location**: `.sdd/` (created in user's project root)

**Directory structure**:
```
.sdd/
├── specs/
│   ├── feature-name.md           # Single-level specs
│   └── parent-name/              # Parent-child hierarchy
│       ├── ../parent-name.md     # Parent spec (one level up)
│       ├── child-feature-a.md    # Child specs
│       └── child-feature-b.md
├── plans/
│   ├── feature-name-plan.md
│   └── parent-name/
│       ├── child-feature-a-plan.md
│       └── child-feature-b-plan.md
├── tasks/
│   ├── feature-name-tasks.md
│   └── parent-name/
│       └── [mirrors spec structure]
└── progress/
    ├── feature-name-progress.md
    └── parent-name/
        └── [mirrors spec structure]
```

**State management approach**: Filesystem as database
- No runtime state - all state persists in markdown
- Human-readable and git-friendly
- Searchable via standard tools (grep, Glob, Read)
- Enables session resumption by reading artifacts

#### 4. Plugin Metadata

**Location**: `spiral-grove/.claude-plugin/plugin.json`

**Current configuration**:
```json
{
  "name": "spiral-grove",
  "description": "A Spec Driven Development (SDD) set of Claude commands.",
  "version": "0.1.1",
  "author": { "name": "Ronald Roy", "email": "gsdwig@gmail.com" },
  "repository": "https://github.com/rjroy/vibe-garden.git",
  "license": "MIT"
}
```

**Discovery mechanism**: Commands auto-discovered from `commands/` directory, skills from `skills/` directory

## Technical Decisions

### Decision 1: Markdown Prompts vs. Executable Code

**Context**: Plugin could be implemented as executable scripts (Python/Node.js) that generate artifacts, or as prompt templates that guide Claude's behavior.

**Options Considered**:
- **Option A**: Python/Node.js scripts with code generation libraries
  - Pros: Programmatic validation, templating engines, faster execution
  - Cons: Language-specific dependencies, harder to customize, opaque to users
- **Option B**: Markdown prompt templates (chosen)
  - Pros: Language-agnostic, transparent, easy to customize, no runtime dependencies
  - Cons: Validation requires Claude execution, potentially less consistent

**Decision**: Use markdown prompt templates exclusively

**Rationale**:
1. **Universality**: Works with any project type without language-specific tooling
2. **Transparency**: Users can read and understand exactly what each command does
3. **Customizability**: Projects can fork and modify prompts for domain-specific needs
4. **Maintainability**: Editing markdown is accessible to non-programmers
5. **Aligns with spec NFR**: "No executable code in plugin (except test/validation scripts)"

### Decision 2: Filesystem-Based State vs. Database

**Context**: Need to persist workflow state (specs, plans, tasks, progress) across sessions.

**Options Considered**:
- **Option A**: SQLite database or JSON files
  - Pros: Queryable, structured data, relational integrity
  - Cons: Opaque to version control, requires parsing tools, not human-readable
- **Option B**: Markdown files in `.sdd/` directory (chosen)
  - Pros: Human-readable, git-friendly, searchable with standard tools, resumable
  - Cons: No enforced schema, requires parsing for validation

**Decision**: Store all artifacts as structured markdown in `.sdd/` directory

**Rationale**:
1. **Git integration**: Markdown files diff/merge cleanly, enabling team collaboration
2. **Resumability**: Developers can read `.sdd/progress/feature-progress.md` and understand state without tooling
3. **Tooling-free**: No special parsers or viewers required
4. **Spec alignment**: Spec explicitly requires "human-readable markdown with consistent formatting"

### Decision 3: Parent-Child Hierarchy via Directory Structure

**Context**: Large projects need to manage multiple related features without loading all context.

**Options Considered**:
- **Option A**: Flat structure with references via metadata fields
  - Pros: Simple directory layout, no nesting
  - Cons: Hard to navigate, no visual hierarchy, difficult to scope work
- **Option B**: Directory-based hierarchy with `.sdd/specs/parent/child.md` (chosen)
  - Pros: Visual grouping, easy to scope, mirrors mental model
  - Cons: Requires careful path management, parent spec lives outside child directory

**Decision**: Use directory structure with parent spec at `.sdd/specs/parent.md` and children at `.sdd/specs/parent/child-*.md`

**Rationale**:
1. **Cognitive alignment**: Directory structure mirrors feature decomposition mental model
2. **Scoped context**: Can work on single child feature without loading sibling specs
3. **Existing patterns**: Matches common file organization conventions (e.g., `components/Button/` with index file and sub-components)
4. **Spec requirement**: Explicitly specified in spec lines 131-137

### Decision 4: Validation Approach

**Context**: Need to ensure specs don't contain implementation details, plans reference specs, etc.

**Options Considered**:
- **Option A**: Automated validation scripts (Python/JS)
  - Pros: Fast, consistent, CI-integrable
  - Cons: Hard to detect nuance (e.g., "use PostgreSQL" vs. "need ACID transactions")
- **Option B**: Checklist-based validation within prompts (chosen)
  - Pros: Nuanced, educational, flexible
  - Cons: Relies on Claude execution, not automated
- **Option C**: Hybrid (Option B + future validation scripts)
  - Pros: Best of both worlds
  - Cons: Deferred complexity

**Decision**: Start with checklist-based validation (Option B), allow for future automation

**Rationale**:
1. **Nuance required**: Distinguishing WHAT from HOW requires semantic understanding (e.g., "need sub-100ms latency" is a valid spec constraint, not implementation)
2. **Educational value**: Checklists teach users SDD principles
3. **Spec constraint**: "No executable code except test/validation scripts" - validation scripts are explicitly allowed for future
4. **Pragmatic start**: Ship working plugin now, add automation later if needed

### Decision 5: Review Command Design

**Context**: Spec requires Phase 5 `/review [phase]` command but it doesn't exist yet.

**Options Considered**:
- **Option A**: Separate `/review-spec`, `/review-plan`, `/review-tasks`, `/review-progress` commands
  - Pros: Simpler prompts, command-specific validation
  - Cons: Command proliferation (4 new commands), inconsistent with spec
- **Option B**: Single `/review [phase]` command with branching logic (chosen)
  - Pros: Matches spec, single command to learn, centralized validation logic
  - Cons: More complex prompt, requires argument parsing

**Decision**: Implement single `/review` command with argument hint `[spec|plan|tasks|progress]`

**Rationale**:
1. **Spec compliance**: Lines 100-122 explicitly define `/review [phase]` with phase argument
2. **User simplicity**: One command to remember, not four
3. **Consistency**: Other commands don't branch by argument, so this establishes the pattern for parameterized commands
4. **Future extensibility**: Sets precedent for other parameterized commands if needed

## Data Model

### Specification Document

**Path**: `.sdd/specs/[feature-name].md`

**Schema** (enforced via prompt template):
```yaml
metadata:
  version: semver string
  status: "Draft" | "Under Review" | "Approved" | "Superseded"
  created: ISO date
  last_updated: ISO date
  parent_specification: path (for child specs)

sections:
  executive_summary: 2-3 sentence overview
  user_story: As-a/I-want/So-that format
  stakeholders:
    primary: list
    secondary: list
    tertiary: list
  success_criteria: measurable outcomes (numbered list)
  functional_requirements: categorized capabilities
  non_functional_requirements:
    performance: targets
    security: requirements
    compliance: regulations
  explicit_constraints: DO NOT items
  technical_context: existing stack, integration points
  acceptance_tests: testable scenarios
  open_questions: unresolved items (checkbox list)
  out_of_scope: deferred features

child_specifications: list of child spec paths (for parent specs)
```

### Plan Document

**Path**: `.sdd/plans/[feature-name]-plan.md`

**Key relationships**:
- References specification path in header
- Technical decisions reference spec constraints
- Integration points map to spec's technical context
- Risk mitigations address spec requirements

### Task Breakdown Document

**Path**: `.sdd/tasks/[feature-name]-tasks.md`

**Key relationships**:
- References both spec and plan paths
- Task acceptance criteria map to spec acceptance criteria
- Dependency graph derives from plan architecture
- Task categories align with plan components

### Progress Document

**Path**: `.sdd/progress/[feature-name]-progress.md`

**Key relationships**:
- Tracks task completion status from task breakdown
- Deviations reference spec/plan sections
- Test coverage maps to spec acceptance tests
- Performance metrics validate against spec NFRs

## Integration Points

### Internal Claude Code Systems

**Slash command system**:
- Commands auto-discovered from `commands/` directory
- Naming convention: `command-name.md` becomes `/spiral-grove:command-name`
- Current namespace: `/spiral-grove:spec-writing`, `/spiral-grove:plan-generation`, etc.
- Missing: `/spiral-grove:review` command

**Skill system**:
- Skills registered from `skills/[skill-name]/SKILL.md`
- Current: `spiral-grove:spiral-grove-guide` skill
- Provides methodology guidance separate from operational commands

**Tool integration (via user direction)**:
- Commands can direct Claude to use project-specific MCPs
- Example: "Use the issue-tracker MCP to create tasks" during `/task-breakdown`
- No hardcoded MCP dependencies - maintains plugin portability

### External Systems (No Direct Integration)

**Version control (Git)**:
- Plugin doesn't execute git commands
- Artifacts are designed to be committed (markdown format)
- Users manually commit `.sdd/` directory

**CI/CD pipelines**:
- No direct integration
- Future: Validation scripts could run in CI to check spec compliance
- Plans inform deployment strategy but don't execute it

**Issue trackers (Jira, GitHub Issues)**:
- No direct integration
- Tasks can be manually copied to issue trackers
- Commands can be directed to use issue-tracker MCPs if available

## State Management

### Session Persistence Strategy

**Problem**: Claude sessions are stateless; need to maintain context across interruptions.

**Solution**: Comprehensive progress documents that capture:
1. **Current state**: Which task is in progress, what's next
2. **Completed work**: Task history with PR links and notes
3. **Discovered issues**: Blockers, deviations, technical discoveries
4. **Decision log**: Approved changes to spec/plan
5. **Test coverage**: Mapping to spec acceptance criteria

**Resumption workflow**:
1. User returns to project after interruption
2. Runs `/implementation` (or relevant phase command)
3. Command prompts Claude to read `.sdd/progress/[feature]-progress.md`
4. Claude reconstructs context from progress document
5. Continues work from exact stopping point

**Validation**: Spec acceptance test #3 (lines 213-220) requires session resumption without re-explanation

### Document Status Flow

**Specifications**:
```
Draft → Under Review → Approved → [Superseded when replaced]
```

**Plans**:
```
Draft → Under Review → Approved → [Updated when revised]
```

**Tasks**:
```
Draft → Ready for Implementation → In Progress → Complete
```

**Progress**:
- Continuously updated during implementation (no discrete status)

## Error Handling Strategy

### Validation Errors

**Scenario**: User runs `/plan-generation` without approved spec

**Approach**: Command prompt includes prerequisite checks:
```markdown
## Prerequisites
Before starting, verify:
1. A specification exists in `.sdd/specs/[feature-name].md`
2. The specification status is "Approved" or "Under Review"

If no spec exists, redirect to `/spec-writing` first.
```

**Implementation**: Claude checks filesystem, provides helpful error message with next action

### Spec Deviations During Implementation

**Scenario**: Implementation discovers spec requirement is impossible/impractical

**Approach** (from `implementation.md` lines 227-252):
1. Stop implementation immediately
2. Document conflict in progress document
3. Propose alternatives with trade-offs
4. Wait for user approval
5. Once approved, update spec/plan/tasks before continuing

**Example** (from implementation.md):
```
🚨 SPEC DEVIATION DETECTED

**Task**: TASK-005 SMS Provider
**Issue**: Spec requires quiet hours 10 PM - 8 AM, but plan uses UTC timezone
**Problem**: Users in different timezones will have wrong quiet hours
**Proposal**: Store timezone in user preferences, calculate quiet hours per user
**Impact**: Adds timezone field, requires migration, +2 hours to estimate

Waiting for approval before proceeding.
```

### Missing Command Errors

**Scenario**: User invokes `/review` command before it exists

**Approach**: Claude Code returns "command not found" error (system-level)

**Mitigation**: Implement `/review` command as part of this plan

## Performance Considerations

### Context Window Efficiency

**Constraint**: Each command prompt ≤ 300 lines (spec NFR line 147)

**Current status**:
- `spec-writing.md`: 159 lines ✅
- `plan-generation.md`: 248 lines ✅
- `task-breakdown.md`: 281 lines ✅
- `implementation.md`: 364 lines ❌ **EXCEEDS LIMIT**

**Action required**: Refactor `implementation.md` to move reference material to skill system

**Strategy**:
1. Move error handling examples to `SDD-QUICK-REFERENCE.md`
2. Move session management checklists to `SDD-QUICK-REFERENCE.md`
3. Keep core behavioral guidance in command prompt
4. Reference skill for detailed examples: "See `spiral-grove:spiral-grove-guide` for examples"

### Workflow Efficiency

**Target** (spec success criterion #6, line 29): 70%+ of user cognitive effort during spec/plan phases

**Design approach**:
- `/spec-writing`: Highly interactive, asks clarifying questions
- `/plan-generation`: Deep codebase exploration, architectural decisions
- `/task-breakdown`: Mostly automated decomposition from plan
- `/implementation`: Autonomous execution with validation checkpoints

**Measurement**: Track ratio of user messages in each phase (future telemetry)

## Security Design

### No Sensitive Data in Plugin

**Approach**: Plugin contains no credentials, API keys, or secrets

**Artifacts**: `.sdd/` documents may reference systems (e.g., "integrates with Stripe API") but should not contain credentials

**User responsibility**: Developers manage secrets via environment variables or config files (outside `.sdd/`)

### Artifact Permissions

**Approach**: Plugin writes markdown files with standard filesystem permissions

**No elevation**: Commands don't require sudo or special permissions

**Git safety**: Users control what gets committed; plugin doesn't auto-commit

## Testing Strategy

### Validation Scripts (Future Enhancement)

**Purpose**: Automated checks for common issues

**Examples**:
- `validate-spec.py`: Check for implementation details in specs (keyword detection)
- `validate-plan.py`: Ensure plan references existing spec
- `validate-tasks.py`: Verify all spec acceptance criteria mapped to tasks

**Constraint**: Spec allows "test/validation scripts" as exception to no-code rule (line 160)

**Status**: Not part of MVP; can be added later

### Manual Testing Approach (MVP)

**Test 1**: Single-feature workflow (spec line 196-203)
- Run `/spec-writing` → create "user notification preferences" spec
- Verify no technology choices in spec
- Run `/plan-generation` → verify codebase exploration, pattern reuse
- Run `/task-breakdown` → verify tasks are appropriately sized
- Run `/implementation` → verify autonomous completion

**Test 2**: Spec-to-code alignment (spec line 205-212)
- Create spec with 5 acceptance criteria
- Complete implementation
- Verify all 5 criteria have passing tests
- Verify no scope creep beyond spec

**Test 3**: Session resumption (spec line 213-220)
- Start implementation, complete 50% of tasks
- Save progress document
- Clear Claude context (simulate interruption)
- Resume by reading progress doc
- Verify continuation without re-explanation

**Test 4**: Phase boundary enforcement (spec line 222-228)
- Run `/spec-writing`
- Attempt to include technology choices
- Verify prompt prevents it and validation checklist flags it

**Test 5**: Parent-child hierarchy (spec line 230-238)
- Create parent spec `dashboard-controller.md`
- Create children `dashboard-controller/feature-a.md`, `dashboard-controller/feature-b.md`
- Verify directory structure mirrors spec
- Verify can work on single child without loading siblings

### Integration Testing

**Approach**: Real-world usage on vibe-garden repository

**Test case**: Use Spiral Grove to implement the `/review` command itself (dogfooding)
1. Create `.sdd/specs/review-command.md`
2. Generate `.sdd/plans/review-command-plan.md`
3. Break down into `.sdd/tasks/review-command-tasks.md`
4. Implement via `.sdd/progress/review-command-progress.md`

**Success criteria**: Process works end-to-end, artifacts are useful for resumption

## Deployment Considerations

### Distribution Mechanism

**Current**: Git repository (`https://github.com/rjroy/vibe-garden.git`)

**Installation**: Users clone repository and link `spiral-grove/` directory as Claude Code plugin

**Future**: Claude Code plugin registry (when available)

### Versioning Strategy

**Semantic versioning**: `major.minor.patch`
- **Major**: Breaking changes to command interfaces or artifact schemas
- **Minor**: New commands or backward-compatible enhancements
- **Patch**: Bug fixes, documentation updates, prompt refinements

**Current version**: 0.1.1 (from `plugin.json`)

**Upgrade path**: Users pull latest changes from git repository

### Rollback Plan

**Problem**: Command prompt changes might degrade behavior

**Approach**: Git-based rollback
1. Tag stable versions: `git tag v0.1.1`
2. If new version has issues, checkout previous tag
3. No database migrations or schema changes to worry about (markdown-only)

**User safety**: Artifacts (`.sdd/`) are versioned separately from plugin, so rollback doesn't corrupt project state

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Implementation.md exceeds 300-line limit** | High | Medium | Refactor to move examples to skill references; create condensed version with pointers to detailed docs |
| **Review command complexity** | Medium | Medium | Start with simple validation (document exists, status field present); iterative enhancement for semantic checks |
| **Parent-child hierarchy not yet implemented** | High | Medium | Add parent/child support to all command prompts; include clear path examples; validate structure in review command |
| **Prompt drift over time** | Low | High | Version control prompts; test with real projects; maintain changelog for prompt changes |
| **Claude interpretation variance** | Medium | Medium | Use explicit checklists and templates; validate with multiple test cases; document edge cases in skill references |
| **User confusion about when to use SDD** | High | Low | Enhance skill guide with decision tree; add examples of SDD vs. quick prompts |

## Dependencies

### Technical Dependencies

**Claude Code platform**:
- Version: Any (plugin system is stable)
- Features used: Slash commands, skill system, filesystem access

**No npm/pip packages**: Plugin is pure markdown

**System requirements**:
- Filesystem access for `.sdd/` directory creation
- Markdown rendering (for human readability, not required for execution)

### Team Dependencies

**None**: Solo developer project (Ronald Roy)

**Future community**:
- GitHub issues for bug reports
- PRs for community contributions
- Documentation improvements

## Timeline Estimate

### Phase 1: Missing Command Implementation (2-4 hours)
- Create `commands/review.md` command prompt
- Implement argument parsing logic (via prompt instructions)
- Add phase-specific validation criteria (spec/plan/tasks/progress)
- Test with existing Spiral Grove artifacts

### Phase 1.5: Parent/Child Hierarchy Support (2-3 hours)
- Update all command prompts to support directory-based hierarchy
- Add instructions for creating parent specs with "Child Specifications" section
- Add instructions for creating child specs with "Parent Specification" field
- Update path handling examples in templates
- Add validation for parent/child references in `/review` command

### Phase 2: Implementation.md Refactoring (1-2 hours)
- Extract examples to `SDD-QUICK-REFERENCE.md`
- Condense core behavioral guidance
- Add references to skill documentation
- Verify ≤300 lines

### Phase 3: Plugin Metadata Updates (30 minutes)
- Update `plugin.json` version to 0.2.0
- Add `/review` command to documentation
- Update changelog

### Phase 4: Integration Testing (2-3 hours)
- Run spec acceptance tests 1-5
- Dogfood `/review` command on its own development
- Fix any discovered issues

### Phase 5: Documentation Updates (1-2 hours)
- Update CLAUDE.md with `/review` command
- Update skill guide with review workflow
- Create example `.sdd/` artifacts for demonstration

**Total estimate**: 9-15 hours (approximately 1.5-2 development days)

## Open Questions

- [ ] Should `/review` command automatically update document status fields, or only present findings for manual approval?
  - **Recommendation**: Present findings, wait for explicit user approval before updating status (safer, aligns with human-in-loop principle)

- [ ] Should validation checks be strict (block progression) or advisory (warn but allow)?
  - **Recommendation**: Advisory for MVP (warnings + user judgment), strict validation can be added later

- [ ] Should parent specs be stored at `.sdd/specs/parent.md` or `.sdd/specs/parent/parent.md`?
  - **Current approach**: `.sdd/specs/parent.md` (parent outside child directory)
  - **Alternative**: `.sdd/specs/parent/_parent.md` (parent inside directory with special prefix)
  - **Recommendation**: Keep current approach per spec lines 184-186

## Appendix

### Existing Code Analysis

**Command prompt patterns** (from existing commands):
1. **Header structure**: Title → "You are now in X Mode" → Role definition
2. **Sections**: Your Focus → Prerequisites → Behavior Guidelines → Output Format → Workflow → Validation Checklist → Next Phase
3. **Behavioral constraints**: Explicit DO/DON'T lists with examples
4. **Template provision**: Full markdown templates for output artifacts
5. **Navigation guidance**: "Use /X to do Y" for phase transitions

**Reusable utilities**:
- Validation checklist pattern (used in all commands)
- Markdown template blocks (consistent across artifacts)
- Status field enumerations (consistent values across phases)
- File naming conventions (kebab-case, `-plan`/`-tasks`/`-progress` suffixes)

**Anti-patterns to avoid**:
- Don't embed large reference materials in command prompts (use skills)
- Don't create parallel file structures (keep `.sdd/` mirroring across artifacts)
- Don't assume execution environment (remain language-agnostic)

### Codebase Conventions

**File organization**:
- Commands: `spiral-grove/commands/[command-name].md`
- Skills: `spiral-grove/skills/[skill-name]/SKILL.md`
- References: `spiral-grove/skills/[skill-name]/references/[reference-name].md`
- Artifacts: `.sdd/[phase]/[feature-name][-suffix].md`

**Naming**:
- Features: `kebab-case`
- Commands: `kebab-case.md`
- Artifacts: `feature-name.md`, `feature-name-plan.md`, `feature-name-tasks.md`, `feature-name-progress.md`

**Status values**:
- Specs: Draft | Under Review | Approved | Superseded
- Plans: Draft | Under Review | Approved | Updated
- Tasks: Draft | Ready for Implementation | In Progress | Complete
- Progress: (no status field, continuously updated)

### Similar Patterns in Ecosystem

**Claude Code plugin patterns**:
- Commands as markdown prompts (standard approach)
- Skills for reference material (standard approach)
- `.claude-plugin/plugin.json` for metadata (required by Claude Code)

**Industry precedents**:
- GitHub Spec Kit (specification-driven development)
- Kiro IDE (structured AI coding workflow)
- Design by Contract (formal specification methodology)

**Academic foundations** (from `SDD-FOUNDATIONS.md`):
- Ostroff et al. 2004: Specification-driven development for component-based systems
- Formal methods: Z notation, VDM (specification languages)
- Test-Driven Development: Red-Green-Refactor (specification via tests)

---

## Validation Checklist

Before marking this plan as approved:
- [x] All spec requirements are addressed in the plan
- [x] Existing codebase patterns have been analyzed
- [x] Technical decisions have documented rationales
- [x] Integration points are clearly defined
- [x] Security and performance are addressed
- [x] Testing strategy is defined
- [x] Risks are identified with mitigations
- [x] Data model supports all use cases
- [ ] User has reviewed and approved the plan

## Next Steps

Once this plan is approved, use `/task-breakdown` to decompose the architecture into implementable tasks for:
1. Creating `commands/review.md`
2. Refactoring `commands/implementation.md`
3. Updating plugin metadata
4. Testing and validation
5. Documentation updates
