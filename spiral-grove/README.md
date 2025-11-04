# Spiral Grove

<img src="spiral-grove-logo.png" align="right" width="128" height="128" alt="Spiral Grove Logo">

**A Spec-Driven Development (SDD) methodology plugin for Claude Code**

Spiral Grove transforms AI-assisted development by providing a structured four-phase workflow: Specification → Planning → Task Breakdown → Implementation. Build production-ready features with clarity, consistency, and comprehensive documentation.

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/rjroy/vibe-garden/releases)
[![Claude Code](https://img.shields.io/badge/platform-Claude%20Code-purple.svg)](https://claude.ai/code)

---

## Features

- 📋 **Specification Phase** - Define WHAT to build with measurable success criteria
- 🏗️ **Planning Phase** - Design HOW to build with architectural decisions and rationale
- 📝 **Task Breakdown** - Decompose plans into discrete, testable tasks with t-shirt sizing
- ⚙️ **Implementation Tracking** - Execute tasks with progress monitoring and technical discovery tracking
- ✅ **Mandatory Validation** - Automatic validator agents ensure quality gates between phases
- 📚 **Documentation Synthesis** - Generate operational CLAUDE.md docs from implementation
- 🔄 **Spec Synthesis** - Reverse-engineer specifications from existing codebases
- 🎯 **Claude Code Plugin** - Install via `/plugin` menu (see Quick Start below)
- 🧩 **Parent/Child Hierarchies** - Organize complex projects without context overload
- 📖 **Integrated Guidance** - Built-in skills provide methodology help and templates

---

## Quick Start (5 Minutes)

### 1. Install Plugin

1. Open Claude Code
2. Type: `/plugin`
3. Follow the prompts to **'add marketplace'**
4. Enter: `https://github.com/rjroy/vibe-garden.git`
5. Follow the prompts and make sure **"Spiral Grove"** is installed

### 2. Start Your First Feature

```
You: I want to build a user authentication system

Claude: [Invokes /spec-writing command]
Let's start with the specification phase through Spiral Grove...
```

### 3. Follow the Workflow

```
/spec-writing    → Define requirements
/plan-generation → Design architecture
/task-breakdown  → Create task list
/implementation  → Build and track progress
```

---

## Use Cases

### Production Feature Development

```
You: /spec-writing
# Creates .sdd/specs/user-auth.md with:
# - Requirements and constraints
# - Measurable success criteria
# - Stakeholder needs
# - Acceptance tests

You: /plan-generation
# Creates .sdd/plans/user-auth-plan.md with:
# - Architectural decisions
# - Integration points
# - Database schema
# - Error handling strategy

You: /task-breakdown
# Creates .sdd/tasks/user-auth-tasks.md with:
# - 15 discrete tasks
# - Dependencies mapped
# - Acceptance criteria per task

You: /implementation
# Executes tasks and creates .sdd/progress/user-auth-progress.md
```

### Complex Multi-Module Projects

```
You: I need to build a complete dashboard system with widgets, data binding, and real-time sync

Claude: This is a large project. Let's use parent/child specs to organize it.

# Creates parent spec: .sdd/specs/dashboard-system.md
# Creates child specs:
#   - .sdd/specs/dashboard-system/widgets.md
#   - .sdd/specs/dashboard-system/data-binding.md
#   - .sdd/specs/dashboard-system/realtime-sync.md

# Each child follows full workflow independently
# Reduces context load, maintains traceability
```

### Validating Before Progression

```
You: /spec-writing
# Automatically invokes validator agent
# Checks for:
# - No HOW details in spec (tech stack choices)
# - Measurable success criteria
# - Explicit constraints (DO NOTs)
# - All requirements numbered (REQ-F-N, REQ-NF-N)

You: /plan-generation
# Automatically invokes validator agent
# Checks for:
# - Technical decisions have rationale
# - Integration points documented
# - Error handling strategy defined
# - Maps to spec requirements

You: /task-breakdown
# Automatically invokes validator agent
# Checks for:
# - All spec acceptance criteria mapped
# - Tasks sized appropriately (prefer S/M/L)
# - Dependencies documented

# Manual validation also available:
You: /review [spec|plan|tasks|progress]
```

### Post-Implementation Documentation

```
You: /synthesize-docs auth
# Analyzes implementation and generates/updates:
# - auth/CLAUDE.md (module documentation)
# - Operational knowledge extracted from code
# - Integration patterns documented
# - Framework-agnostic structure
```

### Reverse-Engineering Specs from Existing Code

```
You: /synthesize-specs payment
# Analyzes existing code and generates:
# - .sdd/specs/payment.md (reverse-engineered spec)
# - Requirements extracted from implementation
# - Test cases derived from test code
# - Enables SDD adoption on legacy codebases
```

---

## Commands Available

### Core Workflow Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/spec-writing` | Define requirements and success criteria | `.sdd/specs/[feature].md` |
| `/plan-generation` | Design architecture and technical approach | `.sdd/plans/[feature]-plan.md` |
| `/task-breakdown` | Break plan into discrete, testable tasks | `.sdd/tasks/[feature]-tasks.md` |
| `/implementation` | Execute tasks with progress tracking | Code + `.sdd/progress/[feature]-progress.md` |

### Meta Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/review [spec\|plan\|tasks\|progress]` | Validate phase documents (auto-invoked by workflow commands) | Validation findings + approval checkpoint |
| `/synthesize-docs [module]` | Generate operational CLAUDE.md documentation | `[module]/CLAUDE.md` (≤400 lines) |
| `/synthesize-specs [module]` | Reverse-engineer specs from existing code | `.sdd/specs/[module].md` |

---

## When to Use SDD

### ✅ Use SDD for:
- Production features requiring multiple files/components
- Long-running development spanning multiple sessions
- Team projects requiring consistency and documentation
- Features with compliance, security, or strict requirements
- Complex integrations with existing systems
- Mission-critical applications

### ⚡ Use Quick Prompts for:
- Bug fixes with clear, isolated solutions
- Simple utility functions or scripts
- UI tweaks and minor styling changes
- Prototypes and experiments
- One-off scripts or automation
- Learning and exploration tasks

**Decision Rule:** If a task requires 3+ distinct steps, involves multiple files, or needs consistency with existing patterns, use SDD.

---

## Key Principles

### Specification Phase
- Focus on **requirements**, not solutions
- Make success criteria **measurable** (e.g., "95% of requests < 200ms")
- Be explicit about **constraints** (DO NOTs)
- Define **stakeholders** and **acceptance tests**

### Planning Phase
- **Explore the codebase** before designing
- Document **technical decisions** with rationale
- Consider **integration points** and **risks**
- Design for the **whole system** (data, errors, security, testing)

### Task Breakdown Phase
- Create **independent, testable** tasks
- Use **t-shirt sizing** (XS/S/M/L/XL/XXL) - prefer S/M/L, break down XL/XXL
- Map tasks to **spec acceptance criteria**
- Identify **dependencies** clearly
- Tasks sized XL+ must be broken down further

### Implementation Phase
- Work **one task at a time**
- **Refer to the spec** constantly
- **Update progress** frequently (in `.sdd/progress/` only)
- **Test everything**
- **Track technical discoveries** immediately
- **Mandatory validation** ensures quality gates between phases

---

## Project Structure

After using Spiral Grove, your project will have:

```
your-project/
├── .sdd/
│   ├── specs/                     # Feature specifications
│   │   ├── feature-name.md
│   │   └── parent-feature/        # Optional: child specs
│   │       ├── child-a.md
│   │       └── child-b.md
│   ├── plans/                     # Technical plans
│   │   ├── feature-name-plan.md
│   │   └── parent-feature/
│   │       ├── child-a-plan.md
│   │       └── child-b-plan.md
│   ├── tasks/                     # Task breakdowns
│   │   ├── feature-name-tasks.md
│   │   └── parent-feature/
│   │       ├── child-a-tasks.md
│   │       └── child-b-tasks.md
│   └── progress/                  # Implementation tracking
│       ├── feature-name-progress.md
│       └── parent-feature/
│           ├── child-a-progress.md
│           └── child-b-progress.md
└── src/
    ├── auth/                      # Implemented modules
    │   ├── CLAUDE.md              # Module documentation (from /synthesize-docs)
    │   └── ...
    └── ...
```

---

## Configuration

### Plugin Settings

Located in `spiral-grove/.claude-plugin/plugin.json`:

```json
{
  "name": "spiral-grove",
  "description": "A Spec Driven Development (SDD) set of Claude commands.",
  "version": "2.1.0",
  "author": {
    "name": "Ronald Roy",
    "email": "gsdwig@gmail.com"
  },
  "repository": "https://github.com/rjroy/vibe-garden.git"
}
```

### Directory Structure

Spiral Grove expects the following structure (created automatically):
- `.sdd/specs/` - Specifications
- `.sdd/plans/` - Technical plans
- `.sdd/tasks/` - Task breakdowns
- `.sdd/progress/` - Implementation tracking
- `.sdd/module-manifest.json` - Documentation synthesis state
- `.sdd/spec-manifest.json` - Spec synthesis state

---

## Documentation

### Reference Guides

- **[SDD Foundations](skills/spiral-grove-guide/references/SDD-FOUNDATIONS.md)** - Core methodology principles and academic background
- **[Quick Reference](skills/spiral-grove-guide/references/SDD-QUICK-REFERENCE.md)** - Commands and workflows cheat sheet
- **[Charter](skills/spiral-grove-guide/references/CHARTER.md)** - Spiral Grove's philosophical approach and principles
- **[Implementation Detail](skills/spiral-grove-guide/references/SPIRAL-GROVE-IMPLEMENTATION-DETAIL.md)** - Technical architecture and requirement mappings
- **[Synthesis Reference](skills/spiral-grove-guide/references/SYNTHESIZE-REFERENCE.md)** - Documentation and spec synthesis guidance
- **[CLAUDE.md Format](skills/sdd-format-docs/docs/claude-md-format.md)** - Documentation synthesis format
- **[Module Manifest Schema](skills/sdd-format-docs/docs/module-manifest-schema.md)** - Module tracking schema
- **[Spec Manifest Schema](skills/sdd-format-docs/docs/spec-manifest-schema.md)** - Spec synthesis tracking schema

### Skills

- **spiral-grove-guide** - Methodology guidance and decision support
  - When to use SDD vs quick prompts
  - Phase principles and best practices
  - Troubleshooting and workflow navigation
- **sdd-templates** - Document templates (spec, plan, tasks, progress)
- **sdd-metadata** - Automatic author detection and version tracking
- **sdd-format-docs** - Format specifications and schemas

---

## Example Workflow

### 1. Start with Specification

```
You: /spec-writing

Claude: Let's create a specification for your feature.
        What are you trying to build?

You: A rate limiting system for our API

Claude: [Creates .sdd/specs/api-rate-limiter.md with:]
        - Requirements (prevent abuse, fair usage)
        - Success criteria (99.9% accuracy, <10ms overhead)
        - Constraints (Redis only, no database changes)
        - Acceptance tests (burst handling, quota enforcement)

        Status: Draft → Ready for Review
```

### 2. Create Technical Plan

```
You: /plan-generation

Claude: [Analyzes codebase, then creates .sdd/plans/api-rate-limiter-plan.md with:]
        - Architecture: Token bucket algorithm
        - Data storage: Redis sorted sets (ZSET)
        - Integration: Middleware in Express router
        - Decision: Token bucket vs sliding window (rationale included)
        - Error handling: Graceful degradation if Redis down
        - Testing: Unit + integration + load tests

        Status: Draft → Approved
```

### 3. Break Down Tasks

```
You: /task-breakdown

Claude: [Creates .sdd/tasks/api-rate-limiter-tasks.md with 12 tasks:]

        TASK-001: Redis client configuration
        TASK-002: Token bucket core logic
        TASK-003: Rate limit middleware
        TASK-004: Error handling wrapper
        ...
        TASK-012: Load testing (1000 req/sec)

        Dependencies mapped, acceptance criteria defined
        Status: Ready for Implementation
```

### 4. Implement with Tracking

```
You: /implementation

Claude: [Executes TASK-001, updates .sdd/progress/api-rate-limiter-progress.md:]

        Completed: TASK-001 (Redis client)
        In Progress: TASK-002 (Token bucket)

        Deviations:
        - Used ioredis instead of redis (better TypeScript support)

        Next: TASK-003 after TASK-002 complete
```

### 5. Validate Along the Way

```
You: /review plan

Claude: ✅ Plan validation passed:
        - All technical decisions have rationale
        - Integration points documented
        - Spec acceptance criteria mapped

        Ready to proceed to task breakdown
```

---

## Philosophy

Spiral Grove treats Claude as a **literal-minded but highly capable pair programmer** who excels when given explicit, detailed instructions. The methodology ensures:

1. **Clarity** - Unambiguous requirements prevent implementation drift
2. **Consistency** - Structured phases maintain coherence across sessions
3. **Completeness** - Nothing falls through the cracks (mandatory validation gates)
4. **Traceability** - Every implementation maps back to requirements
5. **Adaptability** - Phases can be revisited when requirements change
6. **Fresh Context** - Agent delegation prevents context bloat
7. **Objective Review** - Validator agents provide "fresh eyes" on work

By separating WHAT (spec), HOW (plan), and STEPS (tasks), and using specialized agents for validation and synthesis, Spiral Grove enables complex features to be built reliably over multiple sessions with full context preservation and quality assurance.

---

## Anti-Patterns to Avoid

- ❌ **Skipping phases** - Each phase builds on the previous
- ❌ **Skipping validation** - Let validator agents catch issues early
- ❌ **Silent discoveries** - Always document technical findings in progress docs
- ❌ **Implementation in spec** - Keep specs focused on WHAT, not HOW
- ❌ **Vague success criteria** - "Fast" is not measurable, "95th percentile < 200ms" is
- ❌ **Missing rationale** - Document WHY decisions were made, not just WHAT
- ❌ **Time-based estimates** - Use t-shirt sizes (S/M/L), not hours/days
- ❌ **XL/XXL tasks** - Break down large tasks into S/M/L chunks
- ❌ **Tracking status in task documents** - Use `.sdd/progress/` only

---

## Contributing

Contributions are welcome! Please see the main repository's [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/rjroy/vibe-garden/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rjroy/vibe-garden/discussions)
- **Documentation**: [Epic Claude Code Plugins](https://github.com/rjroy/vibe-garden)

---

## Architecture

### Agent Delegation Pattern

Spiral Grove uses a modular architecture where:

**Commands** orchestrate workflows → **Agents** execute discrete work → **Skills** serve resources

### Components

**8 Specialized Agents**:
- **Validators** (automatically invoked): `spec-validator`, `plan-validator`, `tasks-validator`, `progress-validator`, `spec-acceptance-validator`
- **Synthesizers** (spawned by commands): `module-discovery-agent`, `module-doc-synthesizer`, `module-spec-synthesizer`

**4 Built-in Skills**:
- `spiral-grove-guide` - Methodology guidance
- `sdd-templates` - Document templates
- `sdd-metadata` - Auto-detection of author info
- `sdd-format-docs` - Format specifications

### Key Design Decisions

**Fresh context per agent**: Prevents context bloat during long workflows

**Objective review**: Agents provide "fresh eyes" - work is validated by separate agents

**Composability**: Agents can be chained (e.g., spec-synthesizer uses spec-writing command)

**Mandatory validation**: Phase commands automatically invoke validator agents

**T-shirt sizing**: Complexity ratings (XS/S/M/L/XL/XXL) instead of time estimates

**Technical discoveries**: Lightweight tracking replaces formal deviation analysis

**Template externalization**: Skills provide templates, reducing command size

**Metadata automation**: Auto-detection of author info and version management

---

## Acknowledgments

Spiral Grove implements research on AI agent design patterns and cognitive architectures for structured software development.

**Built with** ❤️ **for structured, thoughtful development**
