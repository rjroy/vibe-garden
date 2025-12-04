---
specification: [.sdd/specs/2025-12-04-test-coverage-improvement.md](./../specs/2025-12-04-test-coverage-improvement.md)
status: Approved
version: 1.0.0
created: 2025-12-04
last_updated: 2025-12-04
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Test Coverage Improvement - Technical Plan

## Overview

This plan outlines the technical approach to increase wyrd-gen-mcp unit test coverage from 49% to 85%+. The strategy uses mock-based unit testing to cover generator modules (Replicate image/video, local image) and utility modules (file_utils, exceptions) without requiring network access or GPU hardware.

The core challenge is that the untested code paths involve external API calls (Replicate SDK) and GPU operations (diffusers). We will mock these at the SDK boundary to test all internal logic paths including success scenarios, error handling, timeouts, and edge cases.

## Architecture

### System Context

The wyrd-gen-mcp test suite integrates with:
- **pytest**: Test runner with async support via pytest-asyncio
- **pytest-cov**: Coverage measurement and reporting
- **unittest.mock**: Python's standard mocking library for dependency isolation

### Component Coverage Map

| Module | Current | Target | Primary Mock Points |
|--------|---------|--------|---------------------|
| `generators/replicate_image.py` | 20% | 80%+ | `Client.async_run` |
| `generators/replicate_video.py` | 21% | 80%+ | `predictions.async_create/get/cancel` |
| `generators/local_image.py` | 22% | 80%+ | `AutoPipelineForText2Image.from_pretrained`, `torch.cuda.is_available` |
| `utils/file_utils.py` | 22% | 90%+ | `httpx.AsyncClient`, `os.path.exists` |
| `exceptions.py` | 58% | 90%+ | None (pure Python) |
| `server.py` | 68% | 80%+ | Generator instances, JSON output |

### Test Organization

```
tests/
├── __init__.py
├── test_image_utils.py          # Existing (11 tests)
├── test_local_catalog.py        # Existing (25 tests)
├── test_video_catalog.py        # Existing (23 tests)
├── test_video_tools.py          # Existing (9 tests)
├── test_replicate_image.py      # NEW: ReplicateImageGenerator tests
├── test_replicate_video.py      # NEW: ReplicateVideoGenerator tests
├── test_local_image.py          # NEW: LocalImageGenerator tests
├── test_file_utils.py           # NEW: file_utils tests
├── test_exceptions.py           # NEW: exceptions tests
├── test_server_tools.py         # NEW: MCP server tool function tests
└── conftest.py                  # NEW: Shared fixtures
```

## Technical Decisions

### TD-1: Mock at SDK Boundary, Not HTTP Level
**Choice**: Mock Replicate SDK methods (`async_run`, `predictions.async_create`) rather than HTTP responses
**Requirements**: REQ-F-5, REQ-F-6, REQ-NF-2
**Rationale**:
- The generators call Replicate SDK methods that return typed objects (`FileOutput`, `Prediction`)
- Mocking at HTTP level requires reconstructing SDK response parsing logic
- SDK-level mocks directly simulate what generators receive, making tests clearer and more stable
- Tests focus on generator behavior, not SDK internals

### TD-2: Use unittest.mock Over pytest-mock Plugin
**Choice**: Use `unittest.mock` from Python's standard library
**Requirements**: REQ-F-4
**Rationale**:
- No additional dependency required (stdlib)
- `AsyncMock` and `MagicMock` are well-documented and widely used
- pytest-mock is a thin wrapper; direct use of `unittest.mock.patch` provides equivalent functionality
- Consistent with existing tests (test_video_tools.py already uses this pattern)

### TD-3: Shared Fixtures in conftest.py
**Choice**: Create `tests/conftest.py` for shared fixtures
**Requirements**: REQ-NF-4
**Rationale**:
- Multiple test files need: temp directories, temp image files, mock clients
- Centralizing fixtures eliminates duplication across test files
- pytest auto-discovers fixtures in conftest.py
- Existing tests already use similar patterns (temp_input_image, temp_output_dir in test_video_tools.py)

### TD-4: Extend Existing Test Infrastructure
**Choice**: Add new test files alongside existing ones rather than restructuring
**Requirements**: REQ-F-11, REQ-F-13
**Rationale**:
- 68 passing tests already exist with proven patterns
- Adding new files maintains continuity and avoids breaking changes
- Existing pytest configuration works; no changes needed
- Lower risk than wholesale refactoring

### TD-5: Test Scenarios Over Test Lines
**Choice**: Focus on scenario coverage (success, failure modes, edge cases) not line-by-line coverage
**Requirements**: REQ-F-5, REQ-F-6, REQ-F-7
**Rationale**:
- Spec explicitly defines scenarios: "success path, API failure, validation failure, multi-file output"
- Line coverage can be misleading (executed doesn't mean tested correctly)
- Scenario-based tests are more maintainable and meaningful
- If target proves hard to reach, document rather than force artificial coverage

### TD-6: Mock Time for Determinism
**Choice**: Mock `asyncio.get_event_loop().time()` in video polling tests
**Requirements**: REQ-NF-3
**Rationale**:
- Video generator has 10-minute timeout logic with time-based polling
- Without time mocking, tests would either wait (slow) or be flaky
- Mocking time allows testing exact timeout boundaries and poll counts
- Pattern: Use `patch.object` on loop's time method

### TD-7: Mock Generator Instances for Tool Tests
**Choice**: Mock the module-level generator instances in server.py for MCP tool tests
**Requirements**: REQ-F-10
**Rationale**:
- MCP tool functions (`generate_image_replicate`, `list_image_models_replicate`, etc.) delegate to generator instances
- Testing tools directly would require full generator setup; instead, mock the generator instances
- Existing test_video_tools.py already uses this pattern (`patch("wyrd_gen_mcp.server.replicate_video_generator")`)
- Allows testing tool-level concerns: JSON serialization, error responses for unknown models, parameter validation

## Integration Points

### Replicate SDK Mocking

**Mock Target**: `replicate.Client` instance passed to generators

```python
# ReplicateImageGenerator receives client in __init__
mock_client = MagicMock()
mock_client.async_run = AsyncMock(return_value=mock_output)
generator = ReplicateImageGenerator(mock_client, "/tmp")
```

**Key SDK Objects to Mock**:
- `FileOutput`: Object with `read()` method returning bytes
- `Prediction`: Object with `id`, `status`, `output`, `error` attributes
- Iterable outputs: Lists of `FileOutput` or URL strings

### Diffusers Library Mocking

**Mock Target**: `AutoPipelineForText2Image.from_pretrained` and pipeline methods

```python
@patch("wyrd_gen_mcp.generators.local_image.AutoPipelineForText2Image")
@patch("wyrd_gen_mcp.generators.local_image.torch")
def test_generate_success(mock_torch, mock_pipeline_class):
    mock_torch.cuda.is_available.return_value = True
    mock_pipeline = MagicMock()
    mock_pipeline_class.from_pretrained.return_value = mock_pipeline
    # ...
```

### File System Mocking

**Mock Target**: `os.path.exists`, `open()`, filesystem operations

For `file_utils.py`:
- Mock `os.path.exists` to control collision avoidance logic
- Use real temp directories for actual file writes (validates integration)
- Mock `httpx.AsyncClient` for download tests

### HTTPX Mocking for Downloads

**Mock Target**: `httpx.AsyncClient.get` responses

```python
@patch("wyrd_gen_mcp.utils.file_utils.httpx.AsyncClient")
async def test_download_success(mock_client_class):
    mock_response = MagicMock()
    mock_response.content = b"video data"
    mock_response.raise_for_status = MagicMock()

    mock_client = MagicMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client_class.return_value = mock_client
```

## Error Handling, Performance, Security

### Error Strategy
- Tests verify exceptions are raised with correct type and context
- Each exception scenario tested independently
- Verify exception `context` dictionary contains expected keys (path, operation, cause)

### Performance Targets
- **REQ-NF-1**: Full suite < 5 seconds
- All mocks are synchronous/instant (no real I/O)
- No startup overhead from actual model loading
- Current suite runs in ~4.6 seconds; adding ~50 tests should stay under 5s

### Security Measures
- Tests never make real API calls (mocked at SDK level)
- No API tokens needed for test execution
- Temp files cleaned up via pytest fixtures

## Testing Strategy

### Unit Test Coverage by Module

**ReplicateImageGenerator** (`test_replicate_image.py`):
1. `test_generate_success_single_file` - FileOutput with read() method
2. `test_generate_success_multiple_files` - Iterable output
3. `test_generate_api_error` - SDK raises exception
4. `test_validate_missing_model` - ValidationError for empty model
5. `test_validate_missing_output` - ValidationError for empty output
6. `test_process_output_unknown_format` - Warning logged, empty result
7. `test_collision_avoidance` - Files don't overwrite

**ReplicateVideoGenerator** (`test_replicate_video.py`):
1. `test_generate_success_immediate` - Prediction succeeds first poll
2. `test_generate_success_after_polls` - Succeeds after N polls
3. `test_generate_timeout` - Exceeds timeout, cancels prediction
4. `test_generate_prediction_failed` - Prediction.status == "failed"
5. `test_generate_prediction_canceled` - Prediction.status == "canceled"
6. `test_validate_missing_image` - ValidationError
7. `test_validate_missing_model` - ValidationError
8. `test_download_url_output` - URL string processed
9. `test_download_file_output` - FileOutput processed
10. `test_progress_callback_invoked` - Callback called during polling

**LocalImageGenerator** (`test_local_image.py`):
1. `test_generate_success_cuda` - GPU available path
2. `test_generate_success_cpu_fallback` - No CUDA available
3. `test_pipeline_load_failure` - from_pretrained raises
4. `test_validate_missing_model` - ValidationError
5. `test_optimizations_applied` - VAE tiling, attention slicing called
6. `test_optimization_not_supported` - Pipeline lacks method (no crash)

**file_utils** (`test_file_utils.py`):
1. `test_get_next_available_path_no_collision` - First index available
2. `test_get_next_available_path_with_collision` - Skips existing files
3. `test_resolve_output_path_relative` - Joins with invoke_dir
4. `test_resolve_output_path_absolute` - Returns normalized absolute
5. `test_resolve_output_path_tilde` - Handles `~` expansion (if supported)
6. `test_download_file_success` - HTTP 200, file written
7. `test_download_file_http_error` - HTTP 4xx/5xx raises FileError
8. `test_download_file_network_error` - Connection error raises FileError
9. `test_download_file_timeout` - Timeout raises FileError
10. `test_download_file_write_error` - Disk write fails

**exceptions** (`test_exceptions.py`):
1. `test_wyrd_gen_error_message_formatting` - Context included in str()
2. `test_wyrd_gen_error_to_dict` - JSON serializable output
3. `test_validation_error_with_parameter` - Parameter in context
4. `test_validation_error_truncates_long_value` - >100 chars truncated
5. `test_generation_error_with_cause` - Cause chain included
6. `test_generation_error_truncates_prompt` - >200 chars truncated
7. `test_file_error_context` - Path and operation in context
8. `test_timeout_error_inherits_generation` - Is subclass of GenerationError

**MCP Server Tools** (`test_server_tools.py`):
1. `test_generate_image_replicate_success` - Returns valid JSON with success fields
2. `test_generate_image_replicate_validation_error` - Missing model/output propagates error
3. `test_list_image_models_replicate` - Returns catalog as JSON
4. `test_get_model_parameters_known_model` - Returns parameters for valid model
5. `test_get_model_parameters_unknown_model` - Returns error with available models
6. `test_generate_image_local_success` - Returns valid JSON with success fields
7. `test_list_image_models_local` - Returns local catalog as JSON
8. `test_get_model_parameters_local_unknown` - Returns error for unknown local model

Note: test_video_tools.py already covers video tool functions (REQ-F-10 partial); these additions complete image/local tool coverage.

### Coverage Validation
- Run `pytest --cov=src/wyrd_gen_mcp --cov-report=term` after implementation
- Verify each target module meets threshold
- If below target, analyze `--cov-report=term-missing` for gaps

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Mock fidelity mismatch (SDK behavior changes) | L | M | Document mock assumptions; pin SDK version in tests |
| Deeply nested code hard to cover | M | L | Flag per spec "escalation note"; don't force artificial coverage |
| Test suite exceeds 5s | L | M | Profile with --durations; parallelize if needed |
| Async mock complexity | M | L | Use proven patterns from test_video_tools.py |

## Dependencies

### Technical
- **pytest-cov**: Must be added to `[project.optional-dependencies].dev` (REQ-F-3)
- **pytest-asyncio**: Already installed; configured in pyproject.toml

### Configuration Change
```toml
# pyproject.toml addition
[project.optional-dependencies]
dev = [
    "ruff>=0.8.0",
    "pytest>=7.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",  # ADD THIS
]
```

## Open Questions

- [x] Test organization (extend vs replace) → Extend existing
- [x] Mock library choice → unittest.mock (stdlib)
- [x] Coverage measurement tool → pytest-cov
