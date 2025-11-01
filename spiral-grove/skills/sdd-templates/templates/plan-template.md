---
specification: [.sdd/specs/YYYY-MM-DD-feature-name.md](./../specs/YYYY-MM-DD-feature-name.md)
status: Draft
version: 1.0.0
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
authored_by:
  - Name <email>
---

# [Feature Name] - Technical Plan

## Overview
Brief technical approach and key strategies (1-2 paragraphs).

## Architecture
- **System Context**: How this fits into the larger system
- **Components**: High-level components and responsibilities
- **Diagram**: ASCII/Mermaid showing relationships (optional)

## Technical Decisions

### TD-1: [Decision Name]
**Choice**: [What was decided]
**Requirements**: REQ-F-X, REQ-NF-Y
**Rationale**: [Why this choice over alternatives with supporting evidence]

## Data Model
<!-- Optional: Include only if feature involves data structures, schemas, or entities -->

- **[Entity Name]**: Key fields and relationships

## API Design
<!-- Optional: Include only if feature exposes external APIs, interfaces, or contracts -->

- **[Endpoint/Interface]**: Request/response format, error handling

## Integration Points
- **[System/Service]**: Integration type, purpose, data flow, dependencies

## Error Handling, Performance, Security
- **Error Strategy**: [Approach to error handling]
- **Performance Targets**: [Specific goals and how to achieve them]
- **Security Measures**: [Key security considerations and mitigations]

## Testing Strategy
- **Unit**: [Approach and coverage target]
- **Integration**: [Key test scenarios]
- **Performance**: [Validation approach]

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Major risks only] | H/M/L | H/M/L | [How to address] |

## Dependencies
- **Technical**: [Libraries, infrastructure]
- **Team**: [Approvals, coordination needed]

## Open Questions
- [ ] [Unresolved technical decisions]
