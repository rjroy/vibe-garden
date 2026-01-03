---
title: Project Quality Rules
thresholds:
  max_function_lines: 100
  max_file_lines: 800
  max_class_lines: 500
  coverage_target: 80
  max_cyclomatic_complexity: 10
---

# Project Quality Rules

This file defines quality standards for this project. Place in `docs/rules/` to enable project-specific auditing.

## Code Structure

### Size Limits

Functions should remain under 100 lines. If a function exceeds this:
- Consider extracting helper functions
- If size is justified, add a comment explaining why

Files should remain under 800 lines. If a file exceeds this:
- Consider splitting into modules by responsibility
- Data-only files (constants, config) can exceed with justification

### Complexity

Cyclomatic complexity should not exceed 10. High complexity indicates:
- Too many branches (if/else chains)
- Consider refactoring to strategy pattern or lookup tables

## Testing

### Coverage Targets

- Unit test coverage: 80% minimum
- All public APIs must have tests
- All error paths must have tests

### Test Quality

Tests should verify behavior, not implementation:
- Test what the function returns, not what it calls internally
- Avoid excessive mocking that obscures real behavior
- Integration tests cover the golden path

## Documentation

### Required Documentation

- All public functions must have doc comments
- Complex algorithms must have explanatory comments
- Non-obvious business logic must be documented

### Naming Conventions

- Functions: verb + noun (getUserById, validateInput)
- Booleans: is/has/can prefix (isValid, hasAccess)
- Constants: SCREAMING_SNAKE_CASE

## Security

### Secrets

- No hardcoded credentials
- Use environment variables for sensitive values
- Never log secrets or tokens

### Input Validation

- Validate all external input
- Use parameterized queries for database access
- Sanitize output to prevent XSS

## Error Handling

### Requirements

- All errors must be logged
- User-facing errors must be sanitized (no stack traces)
- Error handling must match documented API failure modes

### Anti-patterns

- No empty catch blocks
- No swallowing errors silently
- No generic "Something went wrong" without logging details

## Build and Dependencies

### Dependency Management

- All dependencies must be pinned to exact versions
- Lock files must be committed
- Document any system-level dependencies in README

### Build Process

- Build must be reproducible
- CI must pass before merge
- All build steps documented in README
