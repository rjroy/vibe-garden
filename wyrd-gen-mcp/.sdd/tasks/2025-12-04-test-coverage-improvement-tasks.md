---
specification: [.sdd/specs/2025-12-04-test-coverage-improvement.md](./../specs/2025-12-04-test-coverage-improvement.md)
plan: [.sdd/plans/2025-12-04-test-coverage-improvement-plan.md](./../plans/2025-12-04-test-coverage-improvement-plan.md)
status: Ready for Implementation
version: 1.0.0
created: 2025-12-04
last_updated: 2025-12-04
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Test Coverage Improvement - Task Breakdown

## Task Summary
Total: 8 tasks | Complexity Distribution: 1×S, 5×M, 1×L, 1×S

## Phase 1: Infrastructure

### TASK-001: Set up test infrastructure and shared fixtures
**Priority**: Critical | **Complexity**: S | **Dependencies**: None

**Description**: Add pytest-cov to dev dependencies and create shared fixtures in conftest.py for use across all new test files.

**Acceptance Criteria**:
- [ ] pytest-cov>=4.0.0 added to `[project.optional-dependencies].dev` in pyproject.toml
- [ ] `tests/conftest.py` created with shared fixtures
- [ ] Fixtures include: temp directory, temp image file, mock Replicate client
- [ ] Running `pytest --cov=src/wyrd_gen_mcp` produces coverage report

**Files**:
- Modify: `server/pyproject.toml`
- Create: `server/tests/conftest.py`

**Testing**: Run `pip install -e ".[dev]"` then `pytest --cov=src/wyrd_gen_mcp --cov-report=term` - should show coverage percentages

---

## Phase 2: Utility Module Tests

### TASK-002: Test exceptions module
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-001

**Description**: Add unit tests for all exception classes in `exceptions.py`. These are pure Python tests requiring no mocks.

**Acceptance Criteria**:
- [ ] `test_exceptions.py` created with 8 test cases
- [ ] Tests cover: `WyrdGenError` message formatting and `to_dict()`
- [ ] Tests cover: `ValidationError` with parameter context and value truncation
- [ ] Tests cover: `GenerationError` cause chaining and prompt truncation
- [ ] Tests cover: `FileError` context (path, operation)
- [ ] Tests cover: `TimeoutError` inherits from `GenerationError`
- [ ] All tests pass

**Files**:
- Create: `server/tests/test_exceptions.py`

**Testing**: `pytest tests/test_exceptions.py -v` - all 8 tests pass

---

### TASK-003: Test file_utils module
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Add unit tests for file utilities covering path resolution, collision avoidance, and async file downloads.

**Acceptance Criteria**:
- [ ] `test_file_utils.py` created with 10 test cases
- [ ] Tests cover: `get_next_available_path` (no collision, with collision)
- [ ] Tests cover: `resolve_output_path` (relative, absolute paths)
- [ ] Tests cover: `download_file` (success, HTTP error, network error, timeout, write error)
- [ ] Mock `httpx.AsyncClient` for download tests
- [ ] Mock `os.path.exists` for collision tests
- [ ] All tests pass

**Files**:
- Create: `server/tests/test_file_utils.py`

**Testing**: `pytest tests/test_file_utils.py -v` - all 10 tests pass

---

## Phase 3: Generator Tests

### TASK-004: Test ReplicateImageGenerator
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Add unit tests for the Replicate image generator covering success paths, error handling, and output processing.

**Acceptance Criteria**:
- [ ] `test_replicate_image.py` created with 7 test cases
- [ ] Tests cover: successful single file generation (FileOutput with read())
- [ ] Tests cover: successful multiple file generation (iterable output)
- [ ] Tests cover: API error handling (SDK raises exception)
- [ ] Tests cover: validation failures (missing model, missing output)
- [ ] Tests cover: unknown output format handling
- [ ] Tests cover: file collision avoidance
- [ ] Mock `replicate.Client.async_run` at SDK boundary
- [ ] All tests pass without network access

**Files**:
- Create: `server/tests/test_replicate_image.py`

**Testing**: `pytest tests/test_replicate_image.py -v` - all 7 tests pass

---

### TASK-005: Test ReplicateVideoGenerator
**Priority**: High | **Complexity**: L | **Dependencies**: TASK-001, TASK-003

**Description**: Add unit tests for the Replicate video generator covering the complex async polling loop, timeout handling, and video download.

**Acceptance Criteria**:
- [ ] `test_replicate_video.py` created with 10 test cases
- [ ] Tests cover: immediate success (prediction succeeds first poll)
- [ ] Tests cover: success after multiple polls
- [ ] Tests cover: timeout (exceeds limit, prediction canceled)
- [ ] Tests cover: prediction failure (status == "failed")
- [ ] Tests cover: prediction cancellation (status == "canceled")
- [ ] Tests cover: validation failures (missing image, missing model)
- [ ] Tests cover: URL output processing
- [ ] Tests cover: FileOutput processing
- [ ] Tests cover: progress callback invocation
- [ ] Mock `predictions.async_create/get/cancel` and time functions
- [ ] All tests pass without network access

**Files**:
- Create: `server/tests/test_replicate_video.py`

**Testing**: `pytest tests/test_replicate_video.py -v` - all 10 tests pass

---

### TASK-006: Test LocalImageGenerator
**Priority**: Medium | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Add unit tests for the local image generator covering GPU detection, pipeline loading, and CPU fallback.

**Acceptance Criteria**:
- [ ] `test_local_image.py` created with 6 test cases
- [ ] Tests cover: successful CUDA generation
- [ ] Tests cover: CPU fallback when CUDA unavailable
- [ ] Tests cover: pipeline load failure
- [ ] Tests cover: validation failures (missing model)
- [ ] Tests cover: optimizations applied (VAE tiling, attention slicing)
- [ ] Tests cover: optimization method not supported (no crash)
- [ ] Mock `torch.cuda.is_available` and `AutoPipelineForText2Image.from_pretrained`
- [ ] All tests pass without GPU hardware

**Files**:
- Create: `server/tests/test_local_image.py`

**Testing**: `pytest tests/test_local_image.py -v` - all 6 tests pass

---

## Phase 4: Server Tool Tests

### TASK-007: Test MCP server tool functions
**Priority**: Medium | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Add unit tests for MCP tool functions (`generate_image_replicate`, `list_image_models_replicate`, etc.) by mocking generator instances.

**Acceptance Criteria**:
- [ ] `test_server_tools.py` created with 8 test cases
- [ ] Tests cover: `generate_image_replicate` success and validation error
- [ ] Tests cover: `list_image_models_replicate` returns catalog as JSON
- [ ] Tests cover: `get_model_parameters_replicate` (known and unknown model)
- [ ] Tests cover: `generate_image_local` success
- [ ] Tests cover: `list_image_models_local` returns catalog
- [ ] Tests cover: `get_model_parameters_local` unknown model error
- [ ] Mock module-level generator instances (`patch("wyrd_gen_mcp.server.replicate_image_generator")`)
- [ ] All tests pass

**Files**:
- Create: `server/tests/test_server_tools.py`

**Testing**: `pytest tests/test_server_tools.py -v` - all 8 tests pass

---

## Phase 5: Validation

### TASK-008: Coverage validation and gap analysis
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-002 through TASK-007

**Description**: Run full coverage report, verify targets met, and document any gaps that couldn't be covered.

**Acceptance Criteria**:
- [ ] Run `pytest --cov=src/wyrd_gen_mcp --cov-report=term-missing`
- [ ] Overall coverage >= 85%
- [ ] Generator modules each >= 80%
- [ ] Utility modules (file_utils, exceptions) each >= 90%
- [ ] Full test suite completes in < 5 seconds
- [ ] If targets not met: document unreachable code paths and rationale
- [ ] All 68 existing tests + ~49 new tests pass

**Files**:
- None (validation only)

**Testing**: Coverage report shows all thresholds met; `pytest tests/` completes successfully in < 5s

---

## Dependency Graph
```
TASK-001 ──┬─> TASK-002 ────────────────────────┐
           ├─> TASK-003 ──┐                     │
           ├─> TASK-004 ──┼─> TASK-008 (final)  │
           ├─> TASK-005 ──┤                     │
           ├─> TASK-006 ──┘                     │
           └─> TASK-007 ────────────────────────┘
```

## Implementation Order

**Phase 1** (Infrastructure): TASK-001
**Phase 2** (Utilities): TASK-002, TASK-003 (parallel)
**Phase 3** (Generators): TASK-004, TASK-005, TASK-006 (parallel after Phase 2)
**Phase 4** (Server): TASK-007 (parallel with Phase 3)
**Phase 5** (Validation): TASK-008 (after all others)

## Notes

- **Parallelization**: TASK-002/003 can run in parallel; TASK-004/005/006/007 can run in parallel
- **Critical path**: TASK-001 → TASK-005 → TASK-008 (video generator is most complex)
- **Test count**: ~49 new tests across 6 new test files (plan specifies exact scenarios)
- **Escalation**: If coverage targets prove difficult due to untestable code, document rather than force artificial coverage
