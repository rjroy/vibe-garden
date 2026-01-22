---
argument-hint: "[optional: spec context]"
description: Generate SDD plan documentation for a feature based on an existing spec
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata)
---
# Plan Generation Mode

You are now in **Plan-Generation Mode**. Your role is to create comprehensive technical plans that bridge the gap between specifications (the "what") and implementation (the "how"). 

## Your Focus

- **Architecture design**: Structure the solution at a high level
- **Codebase integration**: Understand existing patterns and conventions
- **Technical decisions**: Choose technologies, patterns, and approaches
- **Dependency mapping**: Identify what touches what
- **Risk identification**: Surface potential technical challenges

$ARGUMENTS

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

**Conciseness Principle**:
This command prompt is intentionally detailed to guide you. **Do NOT mirror this verbosity in your output**. Your plan should be:
- **Complete**: All HOW (technical approach) and WHY (rationale) for decisions
- **Concise**: Remove redundant prose, not essential information
- **Scannable**: Clear section headers, bulleted lists over paragraphs
- **Actionable**: Focused on decisions and rationale, not general exposition

**What to keep**:
- ✅ All technical decisions with full rationale (the HOW and WHY)
- ✅ Architecture details needed for implementation
- ✅ Integration points, data models, API designs
- ✅ Context that explains why choices were made

**What to remove**:
- ❌ Redundant explanations of the same concept
- ❌ Verbose prose when bullets suffice
- ❌ Repeated examples showing the same pattern
- ❌ General background information covered in the spec

Think: "Have I explained HOW to build this and WHY clearly enough that someone could implement it without guessing?"

1. **Deeply analyze the existing codebase and spec**:
   - Read the spec to identify all numbered requirements (REQ-F-1, REQ-NF-1, etc.)
   - Use Glob and Grep to find similar patterns
   - Identify existing services, models, utilities to reuse
   - Understand the current architecture and conventions
   - Find integration points mentioned in the spec

2. **Design with context**:
   - Respect existing patterns (don't reinvent the wheel)
   - Match the project's architectural style
   - Consider team familiarity with technologies
   - Think about operational maintenance

3. **Make trade-offs explicit and map to requirements**:
   - "We'll use PostgreSQL instead of MongoDB because the rest of the system uses PostgreSQL (REQ-NF-1)"
   - "We'll embed in the monolith rather than create a microservice to reduce operational complexity (REQ-NF-3)"
   - Document WHY decisions were made
   - **Reference spec requirements** when explaining how plan items satisfy them

4. **Think about the whole system**:
   - Data flows
   - State management
   - Error handling strategy
   - Monitoring and observability
   - Testing strategy

5. **Stay at architecture level**:
   - DO explain HOW to structure the solution (components, flow, integration)
   - DO explain WHY you chose this approach over alternatives
   - DON'T write actual implementation code (no function bodies, no line-by-line logic)
   - DON'T break down into granular tasks yet (that's `/task-breakdown`)

6. **Work incrementally and save often**:
   - Create the plan in sections rather than all at once
   - Save after completing major sections (e.g., after Architecture, after Technical Decisions, etc.)
   - This avoids API timeouts and allows for refinement as design evolves
   - You can always edit and improve earlier sections as you work through later ones

7. **Balance conciseness with completeness**:
   - Target: 15-25 pages for typical features (not 40+)
   - Each Technical Decision: Enough rationale to understand WHY (typically 1-3 paragraphs)
   - If rationale is complex, keep the complexity - don't artificially shorten
   - API Design: Describe the approach and key endpoints (not every parameter)
   - Data Model: Show key entities and relationships (not exhaustive field lists)
   - **If a section feels repetitive or redundant, consolidate - but don't cut essential HOW/WHY**

8. **Final step - Remove redundancies**:
   - Before saving, review what you wrote
   - Look for repeated concepts across sections (consolidate duplicates)
   - Consolidate similar examples (keep 1-2 representative ones)
   - Convert long prose paragraphs to bulleted lists where possible
   - Ask: "Is every technical decision clear with its WHY? Would an implementer have questions?"
   - If the answer is yes, add clarity - don't remove it

## Output Format

Create a plan document in `.sdd/plans/[feature-name]-plan.md` with filename format: `YYYY-MM-DD-[feature-name]-plan.md`.

**For parent/child hierarchies**: Mirror the spec directory structure:
- Parent plan: `.sdd/plans/parent-feature-plan.md`
- Child plans: `.sdd/plans/parent-feature/child-a-plan.md`, `.sdd/plans/parent-feature/child-b-plan.md`

**Template Structure**:
Use the `sdd-templates` skill to read `templates/plan-template.md` for the complete document structure. Follow the template exactly for section organization and frontmatter YAML format.

**Metadata Auto-Population**:
Invoke `Skill(spiral-grove:sdd-metadata)` to populate frontmatter fields:
- `created`: Follow skill instructions for date generation
- `authored_by`: Follow skill instructions for author detection
- `last_updated`: Same as created for new plans

## Workflow

### Creating New Plans
1. **Read spec**: Understand requirements thoroughly
2. **Check hierarchy**: If child, read parent spec/plan first for context
3. **Explore codebase**: Use Glob/Grep to find existing patterns
4. **Draft architecture**: Create in sections, save periodically
5. **Document decisions**: Key choices with rationale
6. **Review & iterate**: Present for feedback, refine
7. **Approve**: Mark ready for task breakdown

### Updating Plans for Revised Specs
When a spec is revised, determine if plan needs minor update or major revision:

**Minor spec changes (v1.0.0 → v1.1.0)**:
- Add/clarify requirements without fundamental scope change
- **Update existing plan in place**
- Add note at top: "Updated to reflect spec v1.1.0"
- Add/revise sections as needed to address new requirements
- Update "Last Updated" date

**Major spec changes (v1.0.0 → v2.0.0)**:
- Fundamental scope or approach changes
- **Archive old plan**: Mark "**Status**: Archived - Superseded by v2 plan"
- **Create new plan** with "-v2" suffix in filename
- Example: `.sdd/plans/feature-plan.md` (archived) → `.sdd/plans/feature-plan-v2.md` (active)
- Start fresh with new architecture based on revised spec

## Key Reminders

- Plans explain HOW to build (architecture) with WHY (rationale), not WHAT to build (that's the spec)
- Stay at architecture level (NOT granular tasks yet)
- Explore codebase extensively - don't design in a vacuum
- Every technical decision needs clear WHY with enough detail to justify it
- Think whole system: data, errors, security, testing, deployment
- Make risks explicit
- Conciseness means removing redundancy, not removing essential HOW/WHY
- Respect hierarchy - plans mirror spec structure

## Validation

Before marking a plan as complete:
- [ ] All spec requirements are addressed in the plan
- [ ] Existing codebase patterns have been analyzed
- [ ] Technical decisions have documented rationales
- [ ] Integration points are clearly defined
- [ ] Security and performance are addressed
- [ ] Testing strategy is defined
- [ ] Risks are identified with mitigations
- [ ] Data model supports all use cases
- [ ] **Plan validator spawned and passed**

### Validator Agent (Always Run)

After drafting the plan, ALWAYS spawn the plan-validator agent in silent mode. This provides a second set of eyes (fresh context) to catch issues:

```markdown
Spawning plan-validator for validation...

[Use Task tool with subagent_type=plan-validator, mode=silent]
```

Address any issues the validator identifies before marking the plan complete.

## Next Phase

Once the plan is approved, use `/task-breakdown` to decompose the architecture into implementable tasks.
