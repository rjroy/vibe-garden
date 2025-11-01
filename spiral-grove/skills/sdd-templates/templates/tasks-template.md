---
specification: [.sdd/specs/YYYY-MM-DD-feature-name.md](./../specs/YYYY-MM-DD-feature-name.md)
plan: [.sdd/plans/YYYY-MM-DD-feature-name-plan.md](./../plans/YYYY-MM-DD-feature-name-plan.md)
status: Draft
version: 1.0.0
created: YYYY-MM-DD
last_updated: YYYY-MM-DD
authored_by:
  - Name <email>
---

# [Feature Name] - Task Breakdown

## Task Summary
Total: [N] tasks | Complexity Distribution: [X×S, Y×M, Z×L]

## [Phase/Category Name]

### TASK-001: [Task Name]
**Priority**: Critical/High/Medium/Low | **Complexity**: [S|M|L] | **Dependencies**: [TASK-XXX or None]

<!--
Complexity Sizing Guide (for AI):
- S (Small, 2pts): Single file, straightforward logic, clear approach
- M (Medium, 3pts): Multiple files or moderate complexity, well-understood domain
- L (Large, 5pts): Complex logic, cross-cutting concerns, or new patterns
- XS (1pt): Too atomic for task tracking - combine with related work
- XL/XXL (8+pts): Must be broken down into smaller S/M/L tasks
-->

**Description**: [What needs to be done]

**Acceptance Criteria**:
- [ ] [Specific, testable criterion]
- [ ] [Specific, testable criterion]

**Files**: Create: `path/to/file.ext` | Modify: `path/to/file.ext`

**Testing**: [How to validate completion]

---

## Dependency Graph
```
[Visual representation of dependencies]
TASK-001 ──┬─> TASK-003
           └─> TASK-004
```

## Implementation Order
**Phase 1** ([Complexity]): TASK-001, TASK-002
**Phase 2** ([Complexity]): TASK-003, TASK-004

## Notes
- **Parallelization**: [Concurrent tasks]
- **Critical path**: [Longest dependency chain]
