---
name: spec-writing
description: This skill should be used when the user asks to "write a spec", "create a specification", "start a new feature", "define requirements", "document what to build", or invokes /spiral-grove:spec-writing. Executes SDD Phase 1 to create feature specifications defining WHAT to build (not HOW).
allowed-tools: Skill(spiral-grove:sdd-templates), Skill(spiral-grove:sdd-metadata)
---

# Specification Writing

Execute SDD Phase 1: Create comprehensive, actionable specifications for development projects.

## Focus Areas

- **Requirements gathering**: Understand the feature from user and business perspectives
- **Stakeholder analysis**: Identify who is impacted and what success looks like
- **Constraint definition**: Be explicit about what NOT to build
- **Acceptance criteria**: Define measurable, testable outcomes
- **Context discovery**: Understand existing systems and integration points

## Argument Handling

If arguments provided (e.g., feature brief or parent spec context):
- Use as starting context for the specification
- If referencing parent spec, read parent first and inherit constraints

If no arguments:
- Ask clarifying questions to understand the feature

## Behavior Guidelines

### Anti-Verbosity Principle

This skill prompt is detailed to guide behavior. Do NOT mirror this verbosity in output. Specifications should be:
- Concise: Every line adds unique value
- Scannable: Clear section headers, bulleted lists
- Actionable: Focused on decisions and criteria, not exposition

Target: "What is the minimum needed for someone to build this correctly?"

### Core Behaviors

1. **Ask clarifying questions** before assuming:
   - "Who are the primary users of this feature?"
   - "What does success look like in measurable terms?"
   - "What existing systems will this integrate with?"
   - "What should this explicitly NOT do?"

2. **Push for measurability** by converting vague requirements:
   - "Fast" → "95th percentile response time under 200ms"
   - "Reliable" → "99.9% uptime with automated failover"
   - "User-friendly" → "Complete workflow in under 3 clicks"

3. **Identify constraints early**:
   - Compliance requirements (GDPR, SOC2)
   - Performance targets
   - Security considerations
   - Budget or timeline constraints
   - Technology stack limitations

4. **Work incrementally**: Create spec in sections, save after major sections to avoid timeouts

5. **Number all requirements** for traceability:
   - Functional: **REQ-F-1**, **REQ-F-2**, etc.
   - Non-functional: **REQ-NF-1**, **REQ-NF-2**, etc.
   - Format: `**REQ-F-1**: Description of requirement`

6. **Conciseness checkpoint**:
   - Target: 10-15 pages for typical features
   - If approaching 20+ pages, consider parent/child split
   - One requirement, one bullet (not paragraphs)

7. **Remove duplication** before marking complete:
   - Scan for repetition
   - Consolidate similar acceptance tests
   - Every line should add new information

8. **Stay at WHAT, not HOW**:

   Ask about capabilities needed:
   - "Does the system need to support tool/function calling?"
   - "What is the acceptable latency for responses?"
   - "System must support 10,000 concurrent users"

   Do NOT ask about implementation choices:
   - "Which cloud service? Claude vs GPT-4?" (HOW)
   - "Should we use Redis for session management?" (HOW)
   - "React or Vue for the frontend?" (HOW)

   Distinction: If multiple technologies could satisfy a requirement, it belongs in planning, not spec.

## Parent/Child Hierarchies

For large projects (3+ related sub-features), organize hierarchically:

**Structure**: `.sdd/specs/parent.md` with children at `.sdd/specs/parent/child-a.md`

**Mirror across phases**: Plans, tasks, and progress follow same hierarchy.

**Evolution**: Can start flat and convert to parent when second related feature emerges.

## Output Format

Create specification in `.sdd/specs/[feature-name].md`

Filename format: `YYYY-MM-DD-[feature-name].md`

For parent/child hierarchies:
- Parent: `.sdd/specs/parent-feature.md`
- Children: `.sdd/specs/parent-feature/child-a.md`

### Template and Metadata

1. Invoke `Skill(spiral-grove:sdd-templates)` to read `templates/spec-template.md`
2. Invoke `Skill(spiral-grove:sdd-metadata)` to populate frontmatter:
   - `created`: Follow skill instructions for date generation
   - `authored_by`: Follow skill instructions for author detection
   - `last_updated`: Same as created for new specs

## Workflow

### New Specifications

1. **Explore**: Ask questions to understand the feature
2. **Check hierarchy**: If child spec, read parent first; inherit constraints with "(Inherited)" note
3. **Draft**: Create spec in sections, save periodically
4. **Review & iterate**: Present for feedback, refine
5. **Approve**: Update status when ready for planning

### Revising Existing Specifications

When testing or implementation reveals spec gaps:

1. Read existing spec to understand current requirements and version
2. Identify gaps: What was wrong, missing, or needs changing?
3. Determine revision type:
   - **Minor** (1.0.0 → 1.1.0): Add missing requirements, clarify existing ones
   - **Major** (1.0.0 → 2.0.0): Fundamental changes to scope or approach
4. Update spec in place
5. Update version and last_updated date
6. Add "## Revision History" section for major changes

**Cascading to plans**:
- Minor spec changes → Update existing plan, note "Revised per spec v1.1.0"
- Major spec changes → Archive old plan (mark "Archived - Superseded by v2"), create new plan with "-v2" suffix

## Validation

Before marking spec complete, verify:

- [ ] Success criteria are measurable and testable
- [ ] All stakeholders identified
- [ ] Constraints and DO NOTs explicit
- [ ] Integration points documented
- [ ] Acceptance tests cover happy path and edge cases
- [ ] Non-functional requirements quantified
- [ ] Open questions documented or resolved
- [ ] **Spec validator spawned and passed**

### Validator Agent

After drafting, ALWAYS spawn the spec-validator agent:

```
Task(
  description: "Validate specification",
  prompt: "Validate the spec at [path]",
  subagent_type: "spiral-grove:spec-validator"
)
```

Address any issues before marking complete.

## Key Reminders

- No implementation details (save for `/spiral-grove:plan-generation`)
- Ask about capabilities, not specific vendors/tools
- Document unknowns in "Open Questions"
- Check for parent/child hierarchies
- Specs evolve (version control them)

## Next Phase

Once specification approved, invoke `/spiral-grove:plan-generation` to create technical architecture.
