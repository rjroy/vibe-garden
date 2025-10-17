# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**Vibe Garden** is a research and development repository focused on AI agent design patterns, cognitive architectures, and Spec-Driven Development (SDD) methodology. The repository contains:

- **Research notes** on emerging AI agent theories and patterns
- **Agent type taxonomy** documenting 30+ agent types across 6 categories
- **Agent design patterns** (8 major patterns documented)
- **Spiral Grove** - A Claude Code plugin implementing Spec-Driven Development workflow

## Repository Structure

```
vibe-garden/
├── seeds/                       # Research materials and brainstorming
│   ├── brainstorm/
│   │   ├── agents/             # Agent type documentation (30+ types)
│   │   └── patterns/           # Agent design patterns (8 patterns)
│   ├── notes/                  # Research papers and theory
│   └── scripts/                # Utility scripts (PDF conversion, etc.)
├── spiral-grove/               # Claude Code plugin for SDD
│   ├── .claude-plugin/         # Plugin configuration
│   └── commands/               # SDD command implementations
│       ├── spec-writing.md     # Specification phase
│       ├── plan-generation.md  # Planning phase
│       ├── task-breakdown.md   # Task decomposition phase
│       └── implementation.md   # Implementation tracking phase
└── .sdd/                       # SDD artifacts (created during workflow)
    ├── specs/                  # Feature specifications
    ├── plans/                  # Technical plans
    ├── tasks/                  # Task breakdowns
    └── progress/               # Implementation progress
```

## Spec-Driven Development (SDD) Workflow

This repository implements a structured development methodology via the **Spiral Grove** plugin. When working on features, follow this four-phase workflow:

### Phase 1: Specification (`/spec-writing`)
- Define WHAT to build (not HOW)
- Create measurable success criteria
- Identify stakeholders and constraints
- Output: `.sdd/specs/[feature-name].md`

### Phase 2: Planning (`/plan-generation`)
- Design technical architecture
- Make and document technical decisions with rationale
- Map integration points and dependencies
- Analyze existing codebase patterns
- Output: `.sdd/plans/[feature-name]-plan.md`

### Phase 3: Task Breakdown (`/task-breakdown`)
- Decompose plan into discrete, implementable tasks
- Map dependencies and execution order
- Define acceptance criteria per task
- Output: `.sdd/tasks/[feature-name]-tasks.md`

### Phase 4: Implementation (`/implementation`)
- Execute tasks one at a time
- Validate against specification
- Track progress and deviations
- Output: Code + `.sdd/progress/[feature-name]-progress.md`

## Key Principles

### Agent Design Philosophy

The research in this repository emphasizes:

1. **Functional abstraction over job titles** - Define agents by computational functions (planner, critic, memory manager) rather than human roles (developer, tester)

2. **Modular architectures** - Break monolithic systems into specialized, interacting components

3. **Feedback-rich loops** - Enable self-reflection, self-correction, and iterative improvement

4. **Epistemic delegation** - Delegate knowledge-intensive tasks to specialized components

5. **Deviation detection** - Include dedicated error monitoring and quality assurance mechanisms

### SDD Principles

1. **Specs define success** - The specification is the source of truth, not assumptions
2. **Document trade-offs** - Always explain WHY decisions were made, not just WHAT
3. **Stay in phase** - Don't jump between phases; complete one before moving to next
4. **Validate continuously** - Map implementation back to spec acceptance criteria
5. **Track deviations** - Document when and why implementation differs from plan

## Working with Research Materials

### Agent Categories

Located in `seeds/brainstorm/agents/`:
- **Cognitive Planning Agents** - Planning and decision-making (MAP, Tree-of-Thoughts)
- **Memory Management Agents** - Context retention and knowledge synthesis
- **Self-Reflective Agents** - Self-critique and iterative improvement (Reflexion)
- **Multi-Agent Collaboration** - Specialized teams with orchestration
- **Software Development Agents** - Traditional SDLC agents (reference only)
- **Neural-Symbolic Integration** - Hybrid neural-symbolic systems

### Design Patterns

Located in `seeds/brainstorm/patterns/`:
- Assembly Line Pattern - Sequential specialized pipeline
- Complementary Pair Pattern - Balanced dual perspectives
- Self-Reflective Loop Pattern - Iterative refinement
- Modular Cognitive Architecture - Specialized cognitive modules
- Adversarial Debate Pattern - Truth-seeking through competition
- Epistemic Delegation Pattern - Task delegation to specialists
- Active Memory Management - Context curation and persistence
- Multi-Agent Collaboration - Cooperative specialist teams

## Common Commands

### SDD Workflow Commands
```bash
# Start a new feature specification
/spec-writing

# Create technical plan from approved spec
/plan-generation

# Break down plan into tasks
/task-breakdown

# Begin implementation with tracking
/implementation
```

### Utility Scripts
```bash
# Convert PDF research papers to markdown
python seeds/scripts/convert_pdf.py <pdf_file> [output_file]
```

## Document Conventions

### File Naming
- Use kebab-case for all files: `feature-name.md`
- Specs: `[feature-name].md`
- Plans: `[feature-name]-plan.md`
- Tasks: `[feature-name]-tasks.md`
- Progress: `[feature-name]-progress.md`

### Cross-References
Documents should reference each other:
- Plans reference their spec
- Tasks reference their plan
- Progress references tasks

### Status Values
**Specifications**: Draft | Under Review | Approved | Superseded
**Plans**: Draft | Under Review | Approved | Updated
**Tasks**: Draft | Ready for Implementation | In Progress | Complete

## Development Workflow

### Starting a New Feature

1. Begin with specification phase:
   ```
   /spec-writing
   ```

2. Once spec approved, create technical plan:
   ```
   /plan-generation
   ```
   Claude will explore codebase and design architecture

3. Break down into tasks:
   ```
   /task-breakdown
   ```

4. Execute with tracking:
   ```
   /implementation
   ```

### Working on Existing Features

Jump into any phase as needed:
- Update specs when requirements change
- Revise plans when architecture needs adjustment
- Refine tasks when scope changes
- Continue implementation tracking

## Anti-Patterns to Avoid

- **Skipping phases** - Each phase builds on the previous
- **Silent deviations** - Always document why implementation differs from spec/plan
- **Implementation in spec** - Keep specs focused on WHAT, not HOW
- **Monolithic agents** - Prefer specialized, modular components
- **Job title analogies** - Use computational function abstractions instead

## Research Integration

When designing new agents or systems:

1. Review agent taxonomy in `seeds/brainstorm/agents/README.md`
2. Check applicable patterns in `seeds/brainstorm/patterns/README.md`
3. Reference theoretical foundations in `seeds/notes/Emerging-Theory-for-Agents.md`
4. Apply SDD methodology for structured development

## Notes

- This repository is primarily research and methodology focused
- The Spiral Grove plugin is the main executable artifact
- Research materials in `seeds/` are documentation and reference
- Active development artifacts go in `.sdd/` directory
