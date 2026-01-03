---
name: Quality Project
description: This skill should be used when auditing code with project-specific quality requirements, when loading custom thresholds or rules from a project's configuration, when a project needs to override universal quality defaults, or when initializing quality configuration for a new project. Handles project-specific quality criteria.
version: 0.1.0
---

# Project-Specific Quality Criteria

This skill handles loading and applying project-specific quality rules that extend or override the universal baseline.

## Purpose

Projects have unique requirements:
- Different size thresholds based on domain complexity
- Framework-specific patterns to enforce
- Custom invariants (e.g., "all API routes must have rate limiting")
- Stricter or looser standards based on project maturity

## Configuration Location

Project quality rules live in `docs/rules/` as markdown files:

```
project/
└── docs/
    └── rules/
        ├── code-quality.md      # Size, naming, structure rules
        ├── testing.md           # Coverage targets, test patterns
        ├── security.md          # Security-specific requirements
        └── [domain].md          # Domain-specific rules
```

### Why Markdown?

- Human-readable and editable
- Can be loaded into AI context directly
- Version controlled with code
- Supports rich formatting for examples
- Same format as CLAUDE.md instructions

## Loading Rules

### Discovery

1. Check for `docs/rules/` directory
2. Read all `.md` files in that directory
3. Parse frontmatter for structured thresholds (optional)
4. Parse body for prose rules and examples

### File Format

Rules files can use optional YAML frontmatter for machine-readable thresholds:

```markdown
---
thresholds:
  max_function_lines: 150
  max_file_lines: 1000
  coverage_target: 85
---

# Code Quality Rules

[Prose explanation of rules and rationale...]
```

### Parsing Priority

1. **Frontmatter thresholds** - Override universal defaults directly
2. **Prose rules** - Provide context and examples for auditors
3. **Universal defaults** - Apply when project rules are silent

## When Configuration Is Missing

If `docs/rules/` does not exist:

1. **Notify the user** - Quality audit will use universal defaults
2. **Recommend setup** - Point to template for creating rules
3. **Proceed with audit** - Don't block on missing configuration
4. **Include in report** - Note that project-specific rules should be defined

### Initialization Template

When a project needs quality configuration, provide this template. See `examples/quality-template.md` for a complete starter template.

## Rule Categories

### Structural Rules

Size limits, complexity thresholds, file organization:

```yaml
thresholds:
  max_function_lines: 100
  max_file_lines: 800
  max_cyclomatic_complexity: 10
```

### Testing Rules

Coverage targets, test patterns, mocking policies:

```yaml
thresholds:
  coverage_target: 80
  integration_test_required: true
```

### Security Rules

Secret detection, input validation, output encoding:

```markdown
## Security Requirements

- No hardcoded credentials (use environment variables)
- All user input must be validated
- SQL queries must use parameterized statements
```

### Domain Rules

Project-specific invariants:

```markdown
## API Requirements

- All endpoints must have rate limiting
- All mutations must be idempotent
- All responses must include correlation IDs
```

## Merging with Universal Rules

Project rules extend (not replace) universal rules:

| Scenario | Behavior |
|----------|----------|
| Project defines threshold | Use project value |
| Project silent on threshold | Use universal default |
| Project explicitly disables rule | Skip that check |
| Project adds new rule | Add to checklist |

### Explicit Disabling

To skip a universal rule, set threshold to `null` or `disabled`:

```yaml
thresholds:
  max_file_lines: null  # Don't enforce file size limits
```

## Integration with Auditors

Auditors query this skill for applicable rules:

```
1. Auditor requests rules for file type (e.g., "typescript")
2. Skill loads docs/rules/*.md
3. Skill merges with universal defaults
4. Skill returns combined ruleset
```

### Rule Resolution Example

**Universal default:** `max_function_lines: 100`
**Project override:** `max_function_lines: 150`
**Applied:** `max_function_lines: 150`

**Universal default:** `coverage_target: 80`
**Project:** (not specified)
**Applied:** `coverage_target: 80`

## Validation

Before applying rules, validate:

1. **Thresholds are numeric** - Don't accept `max_lines: "big"`
2. **Values are reasonable** - Flag `coverage_target: 150`
3. **No contradictions** - Alert if rules conflict

## Additional Resources

### Example Files

- **`examples/quality-template.md`** - Starter template for project quality rules
- **`examples/strict-rules.md`** - Example of stricter configuration
- **`examples/relaxed-rules.md`** - Example of relaxed configuration for prototypes
