---
name: plan-generation
description: This skill should be used when the user asks to "create a plan", "design architecture", "plan implementation", "decide how to build", or invokes /spiral-grove:plan-generation. Executes SDD Phase 2 to create technical plans that bridge specifications (WHAT) and implementation (HOW).
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata)
---

# Plan Generation

Execute SDD Phase 2: Create comprehensive technical plans designing HOW to build features.

## Focus Areas

- **Architecture design**: Structure the solution at high level
- **Codebase integration**: Understand existing patterns and conventions
- **Technical decisions**: Choose technologies, patterns, and approaches
- **Dependency mapping**: Identify what touches what
- **Risk identification**: Surface potential technical challenges

## Prerequisites

Before starting, verify:

1. Specification exists in `.sdd/specs/[feature-name].md`
2. Specification status is "Approved" or "Under Review"
3. **Check for parent/child relationships**:
   - If spec has "Parent Specification" field, read parent first
   - If spec has "Child Specifications", understand which child is being planned
   - Verify directory structure mirrors spec hierarchy

If no spec exists, redirect to `/spiral-grove:spec-writing` first.

## Argument Handling

If arguments provided (spec context):
- Use referenced spec as the source
- Skip spec discovery

If no arguments:
- List available specs in `.sdd/specs/`
- Ask user which spec to plan for

## Behavior Guidelines

### Conciseness Principle

Output plans should be:
- **Complete**: All HOW (technical approach) and WHY (rationale)
- **Concise**: Remove redundant prose, not essential information
- **Scannable**: Clear section headers, bulleted lists over paragraphs
- **Actionable**: Focused on decisions and rationale

**What to keep**:
- All technical decisions with full rationale
- Architecture details needed for implementation
- Integration points, data models, API designs
- Context explaining why choices were made

**What to remove**:
- Redundant explanations of the same concept
- Verbose prose when bullets suffice
- Repeated examples showing the same pattern
- General background covered in spec

Target: "Have I explained HOW and WHY clearly enough for implementation without guessing?"

### Core Behaviors

1. **Deeply analyze existing codebase and spec**:
   - Read spec to identify all numbered requirements (REQ-F-1, REQ-NF-1)
   - Use Glob and Grep to find similar patterns
   - Identify existing services, models, utilities to reuse
   - Understand current architecture and conventions
   - Find integration points mentioned in spec

2. **Design with context**:
   - Respect existing patterns (don't reinvent)
   - Match project's architectural style
   - Consider team familiarity with technologies
   - Think about operational maintenance

3. **Make trade-offs explicit and map to requirements**:
   - "Using PostgreSQL instead of MongoDB because rest of system uses PostgreSQL (REQ-NF-1)"
   - "Embedding in monolith rather than microservice to reduce operational complexity (REQ-NF-3)"
   - Document WHY decisions were made
   - Reference spec requirements when explaining how plan items satisfy them

4. **Think about whole system**:
   - Data flows
   - State management
   - Error handling strategy
   - Monitoring and observability
   - Testing strategy

5. **Stay at architecture level**:
   - DO explain HOW to structure the solution (components, flow, integration)
   - DO explain WHY this approach over alternatives
   - DON'T write actual implementation code
   - DON'T break down into granular tasks (that's task-breakdown)

6. **Work incrementally**: Save after completing major sections

7. **Balance conciseness with completeness**:
   - Target: 15-25 pages for typical features
   - Each Technical Decision: Enough rationale to understand WHY (1-3 paragraphs)
   - API Design: Describe approach and key endpoints (not every parameter)
   - Data Model: Show key entities and relationships (not exhaustive field lists)

8. **Remove redundancies** before saving:
   - Look for repeated concepts across sections (consolidate)
   - Consolidate similar examples (keep 1-2 representative)
   - Convert long prose to bulleted lists where possible

## Output Format

Create plan in `.sdd/plans/[feature-name]-plan.md`

Filename format: `YYYY-MM-DD-[feature-name]-plan.md`

For parent/child hierarchies:
- Parent: `.sdd/plans/parent-feature-plan.md`
- Children: `.sdd/plans/parent-feature/child-a-plan.md`

### Template and Metadata

1. Invoke `Skill(spiral-grove:sdd-templates)` to read `templates/plan-template.md`
2. Invoke `Skill(spiral-grove:sdd-metadata)` to populate frontmatter

## Workflow

### Creating New Plans

1. **Read spec**: Understand requirements thoroughly
2. **Check hierarchy**: If child, read parent spec/plan first
3. **Explore codebase**: Use Glob/Grep to find existing patterns
4. **Draft architecture**: Create in sections, save periodically
5. **Document decisions**: Key choices with rationale
6. **Review & iterate**: Present for feedback, refine
7. **Approve**: Mark ready for task breakdown

### Updating Plans for Revised Specs

**Minor spec changes (v1.0.0 → v1.1.0)**:
- Update existing plan in place
- Add note: "Updated to reflect spec v1.1.0"
- Update "Last Updated" date

**Major spec changes (v1.0.0 → v2.0.0)**:
- Archive old plan: Mark "**Status**: Archived - Superseded by v2 plan"
- Create new plan with "-v2" suffix
- Start fresh based on revised spec

## Validation

Before marking plan complete:

- [ ] All spec requirements addressed
- [ ] Existing codebase patterns analyzed
- [ ] Technical decisions have documented rationales
- [ ] Integration points clearly defined
- [ ] Security and performance addressed
- [ ] Testing strategy defined
- [ ] Risks identified with mitigations
- [ ] Data model supports all use cases
- [ ] **Plan validator spawned and passed**

### Validator Agent

After drafting, ALWAYS spawn the plan-validator agent:

```
Task(
  description: "Validate plan",
  prompt: "Validate the plan at [path]",
  subagent_type: "spiral-grove:plan-validator"
)
```

Address any issues before marking complete.

## Key Reminders

- Plans explain HOW (architecture) with WHY (rationale), not WHAT (that's spec)
- Stay at architecture level (NOT granular tasks)
- Explore codebase extensively (don't design in vacuum)
- Every technical decision needs clear WHY
- Think whole system: data, errors, security, testing, deployment
- Make risks explicit
- Conciseness = removing redundancy, not removing essential HOW/WHY
- Respect hierarchy (plans mirror spec structure)

## Next Phase

Once plan approved, invoke `/spiral-grove:task-breakdown` to decompose into implementable tasks.
