# Spiral Grove Project Charter

**Version**: 1.0.0
**Created**: 2025-10-30
**Status**: Living Document

---

## Mission

Spiral Grove addresses the **"vibe coding" problem** in AI-assisted development—where ad hoc prompts produce inconsistent, scope-creeping implementations that drift from intent. Language models excel at pattern completion, not mind reading. Without explicit specifications, AI agents interpret ambiguity based on statistical patterns, leading to iterative "vibe checks" without objective criteria, inconsistency across sessions, and difficulty maintaining coherence in large codebases.

**Our Mission**: Provide a structured, four-phase methodology where **specifications serve as the source of truth** for AI-assisted development, enabling predictable, validatable, and coherent outcomes through explicit requirements, living documents, and phase-gated validation.

---

## Core Pillars

### 1. Specifications as Source of Truth

Requirements define correctness, not code execution. Implementation that deviates without approval is "wrong" even if it "works." Specifications create contracts between stakeholders, developers, AI agents, and future teams.

**In Practice**: The `/review` command enforces spec compliance through validation gates. Code that passes tests but violates spec criteria fails validation.

---

### 2. Explicit Over Implicit Knowledge

Make all assumptions, constraints, and requirements explicit in writing. This reduces interpretation variance in AI agents, prevents context loss across sessions, and enables team transitions without tribal knowledge.

**In Practice**: Frontmatter metadata (author, dates, version) is auto-populated with zero friction. No silent assumptions—if it matters, it's documented.

---

### 3. Living Documents with Phase-Gated Evolution

Specifications evolve through managed updates, not frozen Waterfall artifacts. Four distinct phases—Spec (WHAT) → Plan (HOW) → Tasks (STEPS) → Implementation (BUILD)—with validation gates between phases prevent building on shaky foundations.

**In Practice**: `/review [phase]` validates completeness before progression. Deviation tracking makes changes explicit and approved, not silent drift.

---

### 4. Delegation Over Inline Execution

**Commands orchestrate**: Provide user guidance, spawn agents, coordinate validation, maintain context across workflows.
**Agents do discrete work**: Analysis, validation, synthesis in fresh context with objective review.
**Skills serve resources**: Bundle templates, schemas, reference docs that commands/agents access.

**In Practice**: Commands reduced by 14-67% through agent delegation in v2.0.0. Fresh context per agent prevents bloat and enables "review with fresh eyes." This is the universal architectural principle proven through implementation.

---

### 5. Composability and Context Isolation

Agents are stateless, focused (100-200 lines), reusable across commands. Three invocation modes enable flexible use: verbose (full report), silent (inline suggestions), gate (pass/fail). Parallel execution supports 100+ agents for large codebases.

**In Practice**: `spec-validator` is reused by `/spec-writing`, `/review spec`, and `/implementation`. Synthesis commands spawn multiple agents concurrently for performance.

---

## Design Philosophy

These principles guide architectural decisions and emerged from v2.0.0 implementation:

### 1. Templates = Scaffolding, Not Documentation

Templates provide minimal structure (section headers + essential placeholders). Commands provide comprehensive guidance. Users customize, don't fight templates.

**Evidence**: Plan template reduced from 204 to 63 lines (69%). Kept essential structure, removed verbose guidance that duplicated command instructions.

---

### 2. Commands ARE Orchestrators

Never create orchestrator agents—commands maintain context and coordinate workflows. Agents are for discrete, specialized tasks that benefit from fresh context. Commands have unique value: persistent context across multiple agent invocations and user interactions.

**Evidence**: Deleted orchestrator agents in v2.0.0 after recognizing they defeated command purpose. Orchestration belongs in commands, not transient agents.

---

### 3. Validate Continuously with Fresh Eyes

Agent implements → Command reviews objectively → Validators check. Fresh context per task prevents accumulation and enables critical review. Quality through multiple perspectives, not just a final gate.

**Evidence**: Implementation command now spawns a general-purpose agent per task. Command reviews agent's work before validators run, providing objective oversight.

---

### 4. T-Shirt Sizes Over Time Estimates

LLMs lack training data to rationally estimate implementation time. Complexity ratings (XS/S/M/L/XL/XXL) provide best-guess assessments users can judge against their own experience. Point system (S=2, M=3, L=5) enables complexity-weighted progress tracking.

**Evidence**: Replaced all time-based estimates (2-8 hours, <1 day) with t-shirt sizes across 8 files in v2.0.0. More honest than false precision.

---

### 5. Stay in Phase

Complete and validate current phase before moving to next. Each phase builds on previous—shaky foundations cause expensive rework. The `/review` command acts as a quality gate between phases.

**Evidence**: Validation made mandatory in `spec-writing`, `plan-generation`, and `task-breakdown` commands. "Always spawn" language replaces "optional verification."

---

### 6. Declarative Requirements (WHAT, Not HOW)

Specify desired outcomes and constraints, not implementation steps. Allows AI agents to apply expertise in choosing optimal strategies. Phase boundary enforcement ensures specs don't contain tech choices.

**Evidence**: `spec-validator` checks for HOW details like "use PostgreSQL" or "deploy on AWS" and flags them as violations.

---

### 7. Document Trade-offs with Rationale

All technical decisions include: options considered, pros/cons, rationale, constraints. Creates decision audit trail, prevents repeating analysis, explains choices to future developers or AI agents.

**Evidence**: Plan validator checks for rationale presence. Implementation command prompts user for decisions when implementation differs from plan.

---

### 8. Track Discoveries and Changes

Changes from spec/plan must be made visible through documentation in progress files. Process: Detect → Document → Explain → Get approval → Update source documents if needed. Creates audit trail, prevents silent drift.

**Evidence**: Progress files include "Technical Discoveries" section where implementation learnings and decisions are captured in real-time during `/implementation`.

---

## Boundaries: What Spiral Grove Is NOT

Understanding what we're **not** building is as important as what we are:

- ❌ **Not Waterfall**: Requirements are living documents that evolve with managed updates, not frozen artifacts that resist change
- ❌ **Not Big Design Up Front**: Emphasis on managed iteration and phase-gated validation, not exhaustive upfront planning
- ❌ **Not Formal Methods**: Trades mathematical rigor for practical validation—markdown specs, not theorem provers
- ❌ **Not Anti-Agile**: Compatible with agile practices; can be used within sprint frameworks
- ❌ **Not a Replacement for Testing**: Specs complement tests; acceptance criteria enable TDD synergy (specs + tests = better than either alone)
- ❌ **Not for Simple Tasks**: Overhead exceeds benefit for bug fixes, UI tweaks, one-off scripts, prototypes
- ❌ **Not About Automation**: Commands orchestrate and guide, but human judgment drives decisions (no auto-migration, no forced workflows)
- ❌ **Not Time-Based Estimation**: LLMs cannot rationally predict time; uses complexity metaphors instead

---

## Key Differentiators

What makes Spiral Grove unique compared to industry implementations (GitHub Spec Kit, Kiro IDE):

1. **Explicit Status Tracking**: Formal lifecycle states (Draft → Under Review → Approved → Superseded/Updated)
2. **Progress Artifacts**: Separate `.sdd/progress/` documents for long-running features with session resumability
3. **Validation Command**: `/review [phase]` provides structured quality gates with semantic analysis (not keyword matching)
4. **Technical Discovery Logging**: Structured format captures learning during implementation for future reference
5. **Deep Codebase Exploration**: Planning phase mandate to use Glob/Grep extensively, find similar patterns
6. **Document Cross-Referencing**: Plans reference specs, tasks reference plans, progress references tasks (full traceability)
7. **Agent Delegation Architecture** (v2.0.0): 8 composable agents, 3 invocation modes, parallel execution support
8. **Template Externalization** (v2.0.0): Lightweight scaffolding, independent variation, hand-writing support
9. **Metadata Automation** (v2.0.0): Zero-friction author detection (Git → P4 → ENV → fallback); date-prefixed filenames for chronological sorting

---

## The Two-Minute Pitch

**Spiral Grove is a structured, four-phase methodology optimized for AI-assisted development where:**

1. **Specifications define success** (not code execution)—implementation that deviates is "wrong" even if it works
2. **Explicit beats implicit**—write down all assumptions, constraints, requirements to prevent LLM interpretation variance
3. **Living documents evolve**—through validation gates and deviation tracking, not frozen Waterfall artifacts
4. **Commands orchestrate, agents work, skills serve**—delegation maximizes context management and enables objective review
5. **Fresh context = better quality**—agents implement in isolation, commands review objectively, validators check systematically

**Key insight from v2.0.0**: The refactor revealed a fundamental architectural principle: **Delegation over inline execution**. This pattern maximizes Claude's effectiveness through careful context management and objective review at every step.

---

## Using This Charter

### For Architectural Decisions

Ask: "Does this align with our core pillars? Which design philosophy principle applies?"

**Example**: Considering adding a new feature to the implementation command?
- Check Pillar 4 (Delegation): Should this be an agent instead?
- Check Principle 2 (Commands ARE Orchestrators): Is this orchestration or discrete work?
- Check Principle 3 (Fresh Eyes): Would agent delegation enable better review?

---

### For Feature Design

Filter through boundaries: "Is this Spiral Grove's responsibility?"

**Example**: User requests automatic spec updates when code changes?
- Check Boundaries: "Not About Automation"—human judgment drives decisions
- Alternative: Provide tooling to detect drift, suggest updates, but require approval

---

### For Onboarding Contributors

Start here: Read Mission → Core Pillars → Boundaries → Skim Principles

**Then**: Review `.sdd/progress/2025-10-29-spiral-grove-v2-refactor-progress.md` for 9 discoveries that prove these principles through implementation experience.

---

### For Evolving the Charter

This is a living document. Update when:
- New architectural principles emerge from implementation
- Boundaries need clarification based on user feedback
- Differentiators change as industry evolves

Process: Propose change → Review against existing pillars → Update with rationale → Bump version

---

## Document History

**Version**: 1.0.0
**Created**: 2025-10-30
**Author**: Ronald Roy <gsdwig@gmail.com>
**Based On**: Spiral Grove v2.0.0 refactor (spec, plan, tasks, progress with 9 discoveries) + SDD-FOUNDATIONS.md analysis
**Status**: Approved

**Next Review**: After v2.1.0 or significant architectural changes

---

**End of Charter**
