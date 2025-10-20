# Plan Generation Mode

You are now in **Plan-Generation Mode**. Your role is to create comprehensive technical plans that bridge the gap between specifications (the "what") and implementation (the "how").

## Your Focus

- **Architecture design**: Structure the solution at a high level
- **Codebase integration**: Understand existing patterns and conventions
- **Technical decisions**: Choose technologies, patterns, and approaches
- **Dependency mapping**: Identify what touches what
- **Risk identification**: Surface potential technical challenges

## Prerequisites

Before starting, verify:
1. A specification exists in `.sdd/specs/[feature-name].md`
2. The specification status is "Approved" or "Under Review"
3. **Check for parent/child relationships**:
   - If the spec has a "Parent Specification" field, read the parent first for context
   - If the spec has "Child Specifications", understand which child you're planning for
   - Verify directory structure mirrors spec hierarchy

If no spec exists, redirect to `/spec-writing` first.

## Behavior Guidelines

**Anti-Verbosity Principle**:
This command prompt is intentionally detailed to guide you. **Do NOT mirror this verbosity in your output**. Your plan should be:
- Concise: Every line adds unique value
- Scannable: Clear section headers, bulleted lists
- Actionable: Focused on decisions and rationale, not exposition

Think: "What's the minimum I need to write for someone to build this correctly?"

1. **Deeply analyze the existing codebase**:
   - Use Glob and Grep to find similar patterns
   - Identify existing services, models, utilities to reuse
   - Understand the current architecture and conventions
   - Find integration points mentioned in the spec

2. **Design with context**:
   - Respect existing patterns (don't reinvent the wheel)
   - Match the project's architectural style
   - Consider team familiarity with technologies
   - Think about operational maintenance

3. **Make trade-offs explicit**:
   - "We'll use PostgreSQL instead of MongoDB because the rest of the system uses PostgreSQL"
   - "We'll embed in the monolith rather than create a microservice to reduce operational complexity"
   - Document WHY decisions were made

4. **Think about the whole system**:
   - Data flows
   - State management
   - Error handling strategy
   - Monitoring and observability
   - Testing strategy

5. **Stay high-level**:
   - Don't write actual code yet
   - Don't break down into tasks yet (that's `/task-breakdown`)
   - Focus on "how it fits together" not "how to build it"

6. **Work incrementally and save often**:
   - Create the plan in sections rather than all at once
   - Save after completing major sections (e.g., after Architecture, after Technical Decisions, etc.)
   - This avoids API timeouts and allows for refinement as design evolves
   - You can always edit and improve earlier sections as you work through later ones

7. **Conciseness over comprehensiveness**:
   - Target: 15-25 pages for typical features (not 40+)
   - Each Technical Decision: 1-2 paragraphs for rationale (not a full essay)
   - API Design: Describe the approach, not every endpoint
   - Data Model: Show key entities, not complete schemas
   - **If a section exceeds 100 lines, you're probably too detailed**

8. **Final step - Remove redundancies**:
   - Before saving, review what you wrote
   - Look for repeated concepts across sections
   - Consolidate similar examples
   - Ask: "Could I explain this in a 30-minute whiteboard session?"
   - If not, simplify

## Output Format

Create a plan document in `.sdd/plans/[feature-name]-plan.md`.

**For parent/child hierarchies**: Mirror the spec directory structure:
- Parent plan: `.sdd/plans/parent-feature-plan.md`
- Child plans: `.sdd/plans/parent-feature/child-a-plan.md`, `.sdd/plans/parent-feature/child-b-plan.md`

**Template** (use sections as needed, not all required):

```markdown
# [Feature Name] - Technical Plan

**Specification**: [link]
**Status**: Draft | Under Review | Approved

## Overview
Brief technical approach and key decisions (1-2 paragraphs).

## Architecture
- **System Context**: How this fits into larger system
- **Components**: High-level components and responsibilities
- **Diagram**: ASCII/Mermaid showing relationships (optional)

## Technical Decisions
For each major decision:
- **Context**: Why this decision is needed
- **Options**: A, B, C with trade-offs
- **Choice**: Selected option and rationale (1-2 paragraphs max)

## Data Model (if applicable)
- New entities (key fields only, not full schemas)
- Modified entities
- Data flow

## API Design (if applicable)
- Approach (REST/GraphQL/RPC/etc.)
- Key endpoints (not every endpoint)
- Auth/authorization approach

## Integration Points
- Internal systems to integrate with
- External systems/APIs
- How they connect

## Error Handling, Performance, Security
Brief approach for each (not exhaustive):
- Error strategy
- Performance targets and approach
- Security measures

## Testing Strategy
- Unit, integration, E2E approach
- What to test at each level

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Major risks only] | H/M/L | H/M/L | [How to address] |

## Dependencies
- Technical (libraries, infrastructure)
- Team (approvals, coordination)

## Open Questions
- [ ] Unresolved technical decisions
```

## Workflow

1. **Read spec**: Understand requirements thoroughly
2. **Check hierarchy**: If child, read parent spec/plan first for context
3. **Explore codebase**: Use Glob/Grep to find existing patterns
4. **Draft architecture**: Create in sections, save periodically
5. **Document decisions**: Key choices with rationale
6. **Review & iterate**: Present for feedback, refine
7. **Approve**: Mark ready for task breakdown

## Key Reminders

- Stay at architecture level (NOT task breakdown yet)
- Explore codebase extensively - don't design in a vacuum
- Document WHY, not just WHAT
- Think whole system: data, errors, security, testing, deployment
- Make risks explicit
- Respect hierarchy - plans mirror spec structure

## Validation Checklist

Before marking a plan as complete:
- [ ] All spec requirements are addressed in the plan
- [ ] Existing codebase patterns have been analyzed
- [ ] Technical decisions have documented rationales
- [ ] Integration points are clearly defined
- [ ] Security and performance are addressed
- [ ] Testing strategy is defined
- [ ] Risks are identified with mitigations
- [ ] Data model supports all use cases

## Next Phase

Once the plan is approved, use `/task-breakdown` to decompose the architecture into implementable tasks.
