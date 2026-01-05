# Copilot Code Review Instructions

## Confidence Threshold

Only comment when confidence exceeds 80%. If you are uncertain whether something is an issue, do not comment.

## Response Format

- Problem statement (one sentence)
- Why it matters (one sentence)
- Suggested fix with code snippet (if applicable)

Be concise. One sentence per comment when possible.

## Do NOT Comment On

### Language Semantics You Frequently Misread
- Python conditional expressions (`x if condition else y` evaluates condition first)
- Python's `zip(strict=True)` already validates length; don't suggest redundant checks
- Truthiness checks in conditional expressions happen before the truthy branch executes

### Redundant Suggestions
- Adding validation before built-in safety mechanisms
- Explicit checks that duplicate what a parameter/flag already does
- Error handling for conditions that cannot occur by construction

### Style and Formatting
- These are handled by ruff (Python) and eslint (TypeScript)
- Do not comment on import ordering, line length, or formatting

### Preference Items
- Parameter tuning suggestions that are subjective, not defects
- "Consider using X instead of Y" when both are valid approaches
- Refactoring suggestions not related to correctness

### Documentation
- Missing docstrings or type hints (unless obviously wrong)
- Comments that restate what code already expresses

## DO Comment On

### Security (High Priority)
- Injection risks (SQL, command, template)
- Credential exposure or hardcoded secrets
- Missing input validation at system boundaries
- Unsafe deserialization

### Correctness (High Priority)
- Logic errors with clear evidence
- Race conditions
- Resource leaks (unclosed files, connections)
- Off-by-one errors
- Null/None dereference risks

### Error Handling
- Missing error handling at external boundaries (API calls, file I/O)
- Swallowed exceptions that hide failures
- Error messages that leak sensitive information

### Architecture
- Code that violates patterns established elsewhere in the codebase
- Breaking changes to public APIs without deprecation

## Project Context

This repository contains:
- Python scripts (use ruff for linting)
- TypeScript/JavaScript (use eslint for linting)
- Claude Code plugins (markdown-based)
- Research documentation

Testing is done with pytest (Python) and bun test (TypeScript).

## CI Already Checks

Do not duplicate warnings for:
- ruff check, ruff format
- eslint
- pytest, bun test
- Type checking (pyright, tsc)
