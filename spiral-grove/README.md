# Spiral Grove

<img src="spiral-grove-logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

**A Spec-Driven Development (SDD) methodology plugin for Claude Code**

Spiral Grove transforms AI-assisted development by providing a structured four-phase workflow: Specification → Planning → Task Breakdown → Implementation. Build production-ready features with clarity, consistency, and comprehensive documentation.

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/rjroy/vibe-garden/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/platform-Claude%20Code-purple.svg)](https://claude.ai/code)

---

## Features

- 📋 **Specification Phase** - Define WHAT to build with measurable success criteria
- 🏗️ **Planning Phase** - Design HOW to build with architectural decisions and rationale
- 📝 **Task Breakdown** - Decompose plans into discrete, testable tasks
- ⚙️ **Implementation Tracking** - Execute tasks with progress monitoring and deviation tracking
- ✅ **Validation Command** - Review phase documents before progression
- 📚 **Documentation Synthesis** - Generate operational CLAUDE.md docs from implementation
- 🔄 **Specification Synthesis** - Reverse-engineer specs from existing code with drift detection
- 🎯 **Claude Code Plugin** - Install via `/plugin install spiral-grove@vibe-garden`
- 🔄 **Parent/Child Hierarchies** - Organize complex projects without context overload
- 📖 **Integrated Guidance** - Built-in skill provides methodology help when stuck

---

## Quick Start (5 Minutes)

### 1. Install Plugin

```bash
# In Claude Code, run:
/plugin install spiral-grove@vibe-garden
```

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
You: /review spec
# Checks for:
# - No HOW details in spec (tech stack choices)
# - Measurable success criteria
# - Explicit constraints (DO NOTs)

You: /review plan
# Checks for:
# - Technical decisions have rationale
# - Integration points documented
# - Error handling strategy defined

You: /review tasks
# Checks for:
# - All spec acceptance criteria mapped
# - Tasks sized appropriately
# - Dependencies documented
```

### Post-Implementation Documentation

```
You: /synthesize-docs
# Analyzes implementation and generates/updates:
# - auth/CLAUDE.md (module documentation)
# - Operational knowledge extracted from code
# - Integration patterns documented
# - Framework-agnostic structure
```

### Legacy Codebase Adoption

```
You: /synthesize-specs
# Reverse-engineers specifications from implementation:
# - .sdd/specs/auth.md (requirements from code)
# - Functional/non-functional requirements extracted
# - Acceptance tests from actual test files
# - Drift detection if existing specs present
# - Bootstraps SDD workflow on legacy code
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
| `/review [spec\|plan\|tasks\|progress]` | Validate phase documents before progression | Validation findings + approval checkpoint |
| `/synthesize-docs [module]` | Generate operational CLAUDE.md documentation | `[module]/CLAUDE.md` (≤400 lines) |
| `/synthesize-specs [module]` | Reverse-engineer specs from code with drift detection | `.sdd/specs/[module].md` |

### Guidance Skill

```
You: When should I use SDD vs quick prompts?

Claude: [Invokes spiral-grove-guide skill]
# Provides decision rules and methodology guidance
```

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
- Keep tasks **small** (< 1 day each)
- Map tasks to **spec acceptance criteria**
- Identify **dependencies** clearly

### Implementation Phase
- Work **one task at a time**
- **Refer to the spec** constantly
- **Update progress** frequently
- **Test everything**
- **Document deviations** immediately

---

## Project Structure

After using Spiral Grove, your project will have:

```
your-project/
├── .sdd/
│   ├── specs/                     # Feature specifications
│   │   ├── feature-name.md        # Manual or reverse-engineered
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
│   ├── progress/                  # Implementation tracking
│   │   ├── feature-name-progress.md
│   │   └── parent-feature/
│   │       ├── child-a-progress.md
│   │       └── child-b-progress.md
│   ├── spec-manifest.json         # Spec synthesis tracking (from /synthesize-specs)
│   └── module-manifest.json       # Doc synthesis tracking (from /synthesize-docs)
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
  "version": "0.1.1",
  "author": {
    "name": "Ronald Roy",
    "email": "gsdwig@gmail.com"
  },
  "repository": "https://github.com/rjroy/vibe-garden.git",
  "license": "MIT"
}
```

### Directory Structure

Spiral Grove expects the following structure (created automatically):
- `.sdd/specs/` - Specifications
- `.sdd/plans/` - Technical plans
- `.sdd/tasks/` - Task breakdowns
- `.sdd/progress/` - Implementation tracking

---

## Documentation

### Reference Guides

- **[SDD Foundations](skills/spiral-grove-guide/references/SDD-FOUNDATIONS.md)** - Core methodology principles
- **[Quick Reference](skills/spiral-grove-guide/references/SDD-QUICK-REFERENCE.md)** - Commands and workflows
- **[CLAUDE.md Format](docs/claude-md-format.md)** - Documentation synthesis format
- **[Module Manifest Schema](docs/module-manifest-schema.md)** - Module tracking schema

### Skills

- **spiral-grove-guide** - Methodology guidance and decision support
  - When to use SDD vs quick prompts
  - Phase principles and best practices
  - Troubleshooting and workflow navigation

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
3. **Completeness** - Nothing falls through the cracks
4. **Traceability** - Every implementation maps back to requirements
5. **Adaptability** - Phases can be revisited when requirements change

By separating WHAT (spec), HOW (plan), and STEPS (tasks), SDD enables complex features to be built reliably over multiple sessions with full context preservation.

---

## Anti-Patterns to Avoid

- ❌ **Skipping phases** - Each phase builds on the previous
- ❌ **Silent deviations** - Always document why implementation differs from plan
- ❌ **Implementation in spec** - Keep specs focused on WHAT, not HOW
- ❌ **Vague success criteria** - "Fast" is not measurable, "95th percentile < 200ms" is
- ❌ **Missing rationale** - Document WHY decisions were made, not just WHAT

---

## Contributing

Contributions are welcome! Please see the main repository's [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](../LICENSE) for details

---

## Support

- **Issues**: [GitHub Issues](https://github.com/rjroy/vibe-garden/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rjroy/vibe-garden/discussions)
- **Documentation**: [Vibe Garden Docs](https://github.com/rjroy/vibe-garden)

---

## Acknowledgments

Spiral Grove implements research on AI agent design patterns and cognitive architectures from the Vibe Garden research repository. See `seeds/brainstorm/` for the theoretical foundations.

**Built with** ❤️ **for structured, thoughtful development**
