---
version: 1.0.0
status: Draft
created: 2025-12-04
last_updated: 2025-12-04
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Test Coverage Improvement Specification

## Executive Summary

The wyrd-gen-mcp project currently has 49% unit test coverage, with critical modules (generators, file utilities) at 20-22%. This specification defines requirements for improving test coverage to 85%+ using mock-based unit testing, without incurring API costs or requiring GPU hardware.

The primary challenge is that the untested code makes external API calls (Replicate) and GPU operations (diffusers). These must be tested via mocks that simulate success, failure, and edge-case scenarios.

## User Story

As a **developer maintaining wyrd-gen-mcp**, I want **comprehensive unit test coverage**, so that **I can refactor and extend the codebase with confidence that regressions will be caught**.

## Stakeholders

- **Primary**: Developers maintaining and extending wyrd-gen-mcp
- **Secondary**: Users of the MCP server who benefit from stable releases

## Success Criteria

1. Overall test coverage reaches 85% or higher (measured by pytest-cov)
2. All generator modules (`replicate_image.py`, `replicate_video.py`, `local_image.py`) reach 80%+ coverage
3. All utility modules (`file_utils.py`, `exceptions.py`) reach 90%+ coverage
4. Test suite executes in under 5 seconds total
5. All tests pass without network access or GPU hardware
6. Single unified test system (no parallel test frameworks)

**Escalation Note**: If coverage targets prove difficult due to untestable code paths (e.g., deeply nested error handling), implementer should flag this for discussion rather than force artificial coverage.

## Functional Requirements

### Test Infrastructure

- **REQ-F-1**: Test suite must use pytest as the test runner (existing configuration)
- **REQ-F-2**: Test suite must use pytest-cov for coverage measurement
- **REQ-F-3**: pytest-cov must be added to core dev dependencies in `pyproject.toml`
- **REQ-F-4**: All tests must use Python's standard `unittest.mock` library or pytest-compatible mocking (no custom mock frameworks)

### Generator Testing

- **REQ-F-5**: ReplicateImageGenerator must have unit tests covering: successful generation, API errors, input validation failures, and output processing (single file, multiple files, unknown formats)
- **REQ-F-6**: ReplicateVideoGenerator must have unit tests covering: successful generation, API errors, input validation failures, polling loop (immediate success, success after retries, timeout, prediction failure), and video download
- **REQ-F-7**: LocalImageGenerator must have unit tests covering: successful generation, pipeline load failures, input validation failures, and GPU/CPU fallback behavior

### Utility Testing

- **REQ-F-8**: File utilities must have unit tests covering: path resolution (absolute, relative, tilde expansion), collision avoidance, and file download (success, HTTP errors, network errors)
- **REQ-F-9**: Exception classes must have unit tests covering: message formatting, context inclusion, cause chaining, and JSON serialization (`to_dict()`)

### Server Tool Testing

- **REQ-F-10**: MCP tool functions must have unit tests covering: successful responses, error responses for unknown models, and parameter validation

### Test Organization

- **REQ-F-11**: Tests must be organized in the existing `tests/` directory structure
- **REQ-F-12**: New test files must follow naming convention `test_[module].py`
- **REQ-F-13**: Test organization must either extend existing tests or replace them entirely (one unified system)

## Non-Functional Requirements

- **REQ-NF-1** (Performance): Full test suite must complete in under 5 seconds. If this proves difficult, implementer should flag for discussion.
- **REQ-NF-2** (Isolation): Tests must not make real network calls or require GPU hardware
- **REQ-NF-3** (Determinism): Tests must be deterministic - no time dependencies (mock time where needed), no random behavior
- **REQ-NF-4** (Maintainability): Mock setups must be reusable via pytest fixtures, not duplicated across tests
- **REQ-NF-5** (Readability): Each test must test one specific scenario with a descriptive name (e.g., `test_poll_timeout_raises_timeout_error`)

## Explicit Constraints (DO NOT)

- Do NOT make real API calls to Replicate (costs money)
- Do NOT require GPU hardware for test execution
- Do NOT create a custom mocking framework (use established libraries)
- Do NOT create a parallel test system (integrate with or replace existing)
- Do NOT add integration tests that require external resources
- Do NOT test private implementation details that may change (test behavior, not internals)

## Technical Context

- **Existing Stack**: Python 3.10+, pytest, pytest-asyncio, FastMCP, Replicate SDK, diffusers
- **Current Coverage**: 49% overall, 20-22% for generators, 22% for file_utils, 58% for exceptions
- **Existing Tests**: 4 test files with 68 passing tests covering image_utils, catalog validation, and some video tools
- **Async Patterns**: Most generator methods are async, requiring pytest-asyncio
- **Integration Points**: Tests must work with existing `pyproject.toml` pytest configuration

## Acceptance Tests

### Coverage Targets

1. **AT-1**: Running `pytest --cov=src/wyrd_gen_mcp --cov-report=term` shows overall coverage >= 85%
2. **AT-2**: Generator modules each show >= 80% coverage in report
3. **AT-3**: Exception module shows >= 90% coverage
4. **AT-4**: File utils module shows >= 90% coverage

### Test Behavior

5. **AT-5**: Running `pytest tests/` with no network access completes successfully (all tests pass)
6. **AT-6**: Test suite completes in under 5 seconds on standard hardware
7. **AT-7**: Running tests on a machine without GPU completes successfully

### Scenario Coverage

8. **AT-8**: Image generator tests cover: success path, API failure, validation failure, multi-file output
9. **AT-9**: Video generator tests cover: immediate success, success after polling, timeout, prediction failure, download failure
10. **AT-10**: Local generator tests cover: success path, pipeline load failure, CPU fallback
11. **AT-11**: Exception tests cover: all exception types, `to_dict()` serialization, cause chaining

### Infrastructure

12. **AT-12**: `pytest-cov` is listed in `[project.optional-dependencies].dev` in pyproject.toml
13. **AT-13**: All new tests use `unittest.mock` or `pytest-mock` for mocking

## Open Questions

- [x] Should tests extend existing structure or rewrite? **Answer: Either, but unified system**
- [x] Is pytest-cov required in dependencies? **Answer: Yes, add to dev dependencies**
- [x] Mock fidelity level? **Answer: Scenario-based (success, failure midway, unreachable)**

## Out of Scope

- Integration tests with real Replicate API
- Performance benchmarking beyond runtime constraint
- Code refactoring to improve testability (test existing code as-is)
- CI/CD pipeline integration
- Test coverage for third-party dependencies

---

**Next Phase**: Once approved, use `/spiral-grove:plan-generation` to create technical implementation plan.
