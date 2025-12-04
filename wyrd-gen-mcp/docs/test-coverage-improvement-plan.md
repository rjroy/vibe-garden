# Test Coverage Improvement Plan: wyrd-gen-mcp

## Executive Summary

This document outlines a plan to improve unit test coverage for the wyrd-gen-mcp project from the current **49%** to a target of **85%+** using mock-based testing strategies. Integration tests requiring real API calls are explicitly out of scope due to cost constraints.

## Current State Analysis

### Coverage by Module (as of 2025-12-04)

| Module | Statements | Missed | Coverage | Priority |
|--------|------------|--------|----------|----------|
| `generators/replicate_image.py` | 91 | 73 | 20% | **HIGH** |
| `generators/replicate_video.py` | 213 | 168 | 21% | **HIGH** |
| `generators/local_image.py` | 79 | 62 | 22% | **HIGH** |
| `utils/file_utils.py` | 46 | 36 | 22% | **HIGH** |
| `exceptions.py` | 57 | 24 | 58% | MEDIUM |
| `server.py` | 79 | 25 | 68% | MEDIUM |
| `data/__init__.py` | 229 | 61 | 73% | LOW |
| `utils/logging_utils.py` | 58 | 14 | 76% | LOW |
| `utils/image_utils.py` | 29 | 3 | 90% | LOW |
| `generators/base.py` | 21 | 0 | 100% | DONE |

### Root Cause of Low Coverage

The three generator modules account for **303 missed statements** (65% of all missed code). These modules contain:
1. Replicate API client calls (`async_run`, `predictions.async_create`)
2. Local GPU pipeline initialization (diffusers)
3. Async polling loops for video generation
4. File download operations via httpx

Testing these requires mocking external dependencies rather than making real API calls.

## Constraints

1. **No integration tests with real APIs** - Replicate API calls cost money
2. **No GPU-dependent tests** - Local generation requires specific hardware
3. **Tests must be deterministic** - No network calls, no time dependencies
4. **Tests must be fast** - Target < 5 seconds total runtime

## Testing Strategy

### Mocking Approach

Each generator has external dependencies that must be mocked:

```
ReplicateImageGenerator
  └── self._client.async_run() -> Mock returns FileOutput or iterable

ReplicateVideoGenerator
  └── self._client.predictions.async_create() -> Mock returns Prediction
  └── replicate.predictions.async_get() -> Mock returns Prediction with status

LocalImageGenerator
  └── diffusers.StableDiffusionPipeline.from_pretrained() -> Mock returns Pipeline
  └── pipeline() call -> Mock returns PIL Image
```

### Test File Organization

```
tests/
├── test_image_utils.py          # Existing - 90% coverage
├── test_local_catalog.py        # Existing - tests data validation
├── test_video_catalog.py        # Existing - tests data validation
├── test_video_tools.py          # Existing - tests server tools
├── test_replicate_image_generator.py   # NEW
├── test_replicate_video_generator.py   # NEW
├── test_local_image_generator.py       # NEW
├── test_file_utils.py                  # NEW
├── test_exceptions.py                  # NEW
└── test_server_tools.py                # NEW (image tools)
```

## Detailed Test Specifications

### 1. ReplicateImageGenerator Tests (`test_replicate_image_generator.py`)

**Target Coverage:** 90%+

#### 1.1 Input Validation Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_missing_model_raises_validation_error` | Empty model string raises ValidationError | None |
| `test_missing_output_file_raises_validation_error` | Empty output_file_name raises ValidationError | None |

#### 1.2 API Call Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_successful_generation_single_file` | Normal generation returns GenerationResult | `_client.async_run` |
| `test_api_error_raises_generation_error` | API exception is wrapped in GenerationError | `_client.async_run` raises |
| `test_prompt_truncation_in_logs` | Prompts > 100 chars are truncated for logging | `_client.async_run` |

#### 1.3 Output Processing Tests (`_process_output`)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_process_single_file_output` | FileOutput with `read()` method saves correctly | Temp file system |
| `test_process_iterable_file_outputs` | Multiple FileOutput objects save with indices | Temp file system |
| `test_process_iterable_bytes` | Raw bytes iterable saves correctly | Temp file system |
| `test_process_unknown_output_type` | Logs warning, returns empty list | Temp file system |
| `test_empty_output_handling` | Empty iterable returns empty saved_files | Temp file system |

#### 1.4 File Naming Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_find_start_offset_no_existing_files` | Returns 0 when no files exist | Temp directory |
| `test_find_start_offset_with_existing_files` | Returns next available index | Temp directory with files |
| `test_make_indexed_path_with_extension` | `output.png` + 3 -> `output_3.png` | None |
| `test_make_indexed_path_without_extension` | `output` + 3 -> `output_3` | None |

#### Mock Fixtures Required

```python
class MockFileOutput:
    """Mock Replicate FileOutput with read() method."""
    def __init__(self, content: bytes):
        self.content = content
    def read(self) -> bytes:
        return self.content

class MockReplicateClient:
    """Mock Replicate client for testing."""
    async def async_run(self, model: str, input: dict) -> Any:
        # Configurable return value
        pass
```

---

### 2. ReplicateVideoGenerator Tests (`test_replicate_video_generator.py`)

**Target Coverage:** 85%+

#### 2.1 Input Validation Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_missing_image_file_raises_file_error` | Non-existent image path raises FileError | None |
| `test_unsupported_image_format_raises_validation_error` | `.bmp` extension raises ValidationError | Temp file |
| `test_missing_model_raises_validation_error` | Empty model raises ValidationError | None |
| `test_unknown_model_raises_validation_error` | Model not in catalog raises ValidationError | None |

#### 2.2 Prediction Creation Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_successful_prediction_creation` | Creates prediction with correct input | `predictions.async_create` |
| `test_prediction_creation_failure` | API error wrapped in GenerationError | `predictions.async_create` raises |
| `test_image_data_uri_included_in_input` | Image converted to data URI correctly | `predictions.async_create` |

#### 2.3 Polling Loop Tests (`_poll_for_completion`)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_poll_succeeds_on_first_check` | Immediate success returns result | `predictions.async_get` |
| `test_poll_succeeds_after_retries` | Success after N polling iterations | `predictions.async_get` (sequence) |
| `test_poll_timeout_raises_timeout_error` | Exceeds max time raises TimeoutError | `predictions.async_get` + time mock |
| `test_poll_prediction_failed_raises_generation_error` | Failed status raises GenerationError | `predictions.async_get` |
| `test_poll_prediction_canceled_raises_generation_error` | Canceled status raises GenerationError | `predictions.async_get` |
| `test_progress_callback_invoked` | Progress callback called during polling | `predictions.async_get` |

#### 2.4 Output Download Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_download_video_success` | Video URL downloaded and saved | `httpx.AsyncClient.get` |
| `test_download_video_failure` | Download error wrapped correctly | `httpx.AsyncClient.get` raises |
| `test_output_path_collision_avoidance` | Existing file triggers index increment | Temp directory with files |

#### Mock Fixtures Required

```python
class MockPrediction:
    """Mock Replicate Prediction object."""
    def __init__(self, id: str, status: str, output: str | None = None, error: str | None = None):
        self.id = id
        self.status = status
        self.output = output
        self.error = error

class MockPredictionsNamespace:
    """Mock for client.predictions namespace."""
    async def async_create(self, model: str, input: dict) -> MockPrediction:
        pass
    async def async_get(self, id: str) -> MockPrediction:
        pass
```

---

### 3. LocalImageGenerator Tests (`test_local_image_generator.py`)

**Target Coverage:** 80%+

#### 3.1 Input Validation Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_missing_model_raises_validation_error` | Empty model raises ValidationError | None |
| `test_unknown_model_raises_validation_error` | Model not in catalog raises ValidationError | None |

#### 3.2 Pipeline Loading Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_pipeline_loads_successfully` | Pipeline loaded from HuggingFace | `StableDiffusionPipeline.from_pretrained` |
| `test_pipeline_load_failure_raises_generation_error` | Load error wrapped correctly | `from_pretrained` raises |
| `test_pipeline_moved_to_cuda` | Pipeline uses GPU when available | `torch.cuda.is_available` + pipeline mock |
| `test_pipeline_uses_cpu_fallback` | Pipeline uses CPU when no GPU | `torch.cuda.is_available` returns False |

#### 3.3 Generation Tests

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_successful_local_generation` | Image generated and saved | Pipeline mock |
| `test_generation_with_custom_parameters` | Parameters passed to pipeline | Pipeline mock |
| `test_generation_failure_raises_error` | Pipeline error wrapped correctly | Pipeline mock raises |

#### Mock Fixtures Required

```python
class MockPipeline:
    """Mock diffusers pipeline."""
    def __init__(self):
        self.device = "cpu"

    def to(self, device: str) -> "MockPipeline":
        self.device = device
        return self

    def __call__(self, prompt: str, **kwargs) -> MockPipelineOutput:
        return MockPipelineOutput()

class MockPipelineOutput:
    """Mock pipeline output with images attribute."""
    def __init__(self):
        self.images = [MockPILImage()]

class MockPILImage:
    """Mock PIL Image."""
    def save(self, path: str) -> None:
        Path(path).write_bytes(b"fake png data")
```

---

### 4. File Utils Tests (`test_file_utils.py`)

**Target Coverage:** 90%+

#### 4.1 Path Resolution Tests (`resolve_output_path`)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_absolute_path_unchanged` | `/abs/path.png` returned as-is | None |
| `test_relative_path_resolved_to_invoke_dir` | `output.png` -> `/invoke/dir/output.png` | None |
| `test_relative_path_with_subdirectory` | `subdir/output.png` resolved correctly | None |
| `test_tilde_expansion` | `~/output.png` expanded to home dir | None |

#### 4.2 Collision Avoidance Tests (`get_next_available_path`)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_no_collision_returns_original` | No existing file returns (path, 0) | Temp directory |
| `test_collision_increments_index` | Existing `output_0.png` returns `output_1.png` | Temp directory with file |
| `test_multiple_collisions_finds_gap` | Finds first available index | Temp directory with files |
| `test_handles_path_without_extension` | Works with extensionless files | Temp directory |

#### 4.3 Download Tests (`download_file`)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_successful_download` | URL content saved to file | `httpx.AsyncClient.get` |
| `test_download_http_error` | Non-200 status raises FileError | `httpx.AsyncClient.get` |
| `test_download_network_error` | Connection error raises FileError | `httpx.AsyncClient.get` raises |
| `test_download_creates_parent_directories` | Missing parent dirs created | `httpx.AsyncClient.get` + temp dir |

---

### 5. Exception Tests (`test_exceptions.py`)

**Target Coverage:** 95%+

#### 5.1 WyrdGenError Tests

| Test Case | Description |
|-----------|-------------|
| `test_message_only` | Simple message stored correctly |
| `test_message_with_context` | Context dict stored and formatted |
| `test_message_with_cause` | Cause exception chained correctly |
| `test_to_dict_basic` | JSON-serializable dict returned |
| `test_to_dict_with_context` | Context included in dict |
| `test_to_dict_with_cause` | Cause info included in dict |

#### 5.2 ValidationError Tests

| Test Case | Description |
|-----------|-------------|
| `test_parameter_included_in_context` | Parameter name in context |
| `test_value_truncation` | Long values truncated to 100 chars |

#### 5.3 GenerationError Tests

| Test Case | Description |
|-----------|-------------|
| `test_operation_included` | Operation name in context |
| `test_model_included` | Model ID in context |
| `test_prompt_truncation` | Prompts > 200 chars truncated |
| `test_prediction_id_included` | Prediction ID in context |

#### 5.4 FileError Tests

| Test Case | Description |
|-----------|-------------|
| `test_path_included` | File path in context |
| `test_operation_included` | Operation type in context |

#### 5.5 TimeoutError Tests

| Test Case | Description |
|-----------|-------------|
| `test_timeout_seconds_included` | Timeout limit in context |
| `test_elapsed_seconds_rounded` | Elapsed time rounded to 1 decimal |

---

### 6. Server Tools Tests (`test_server_tools.py`)

**Target Coverage:** 90%+

Extends existing `test_video_tools.py` pattern to cover image generation tools.

#### 6.1 Image Generation Tools (Replicate)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_generate_image_replicate_success` | Successful generation returns JSON | `replicate_image_generator.generate` |
| `test_list_image_models_returns_catalog` | Returns all models from MODELS | None |
| `test_get_parameters_known_model` | Returns parameters for valid model | None |
| `test_get_parameters_unknown_model` | Returns error with available models | None |

#### 6.2 Image Generation Tools (Local)

| Test Case | Description | Mock Required |
|-----------|-------------|---------------|
| `test_generate_image_local_success` | Successful generation returns JSON | `local_image_generator.generate` |
| `test_list_local_models_returns_catalog` | Returns all models from LOCAL_MODELS | None |
| `test_get_local_parameters_known_model` | Returns parameters for valid model | None |
| `test_get_local_parameters_unknown_model` | Returns error with available models | None |

---

## Implementation Order

### Phase 1: Foundation (High Impact, Low Complexity)
1. `test_exceptions.py` - Pure Python, no mocks needed
2. `test_file_utils.py` - Simple mocking, foundational utilities

### Phase 2: Core Generators (High Impact, Medium Complexity)
3. `test_replicate_image_generator.py` - Template for other generators
4. `test_local_image_generator.py` - Similar pattern, different mocks

### Phase 3: Complex Logic (High Impact, High Complexity)
5. `test_replicate_video_generator.py` - Polling loop, timeout handling

### Phase 4: Integration Layer (Medium Impact, Low Complexity)
6. `test_server_tools.py` - Completes MCP tool coverage

## Success Criteria

| Metric | Current | Target |
|--------|---------|--------|
| Overall Coverage | 49% | 85%+ |
| Generator Coverage | 20-22% | 80%+ |
| File Utils Coverage | 22% | 90%+ |
| Exception Coverage | 58% | 95%+ |
| All Tests Pass | Yes | Yes |
| Test Runtime | 2.8s | < 5s |

## Dependencies

### Python Packages (Already in dev dependencies)
- `pytest>=7.0.0`
- `pytest-asyncio>=0.23.0`
- `pytest-cov` (add to dev dependencies)

### Mock Libraries (Standard library)
- `unittest.mock.patch`
- `unittest.mock.AsyncMock`
- `unittest.mock.MagicMock`

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Mocks don't match real API behavior | Document mock assumptions, review Replicate API docs |
| Tests become brittle to implementation changes | Test behavior, not implementation details |
| Async testing complexity | Use `pytest-asyncio` with `auto` mode |
| Temp file cleanup failures | Use `pytest` `tmp_path` fixture |

## Appendix: Mock Response Examples

### Replicate FileOutput
```python
# Real response has read() method returning bytes
class FileOutput:
    def read(self) -> bytes:
        return b"\x89PNG\r\n..."  # PNG binary data
```

### Replicate Prediction
```python
# Real prediction object structure
prediction = {
    "id": "abc123",
    "status": "succeeded",  # or "processing", "failed", "canceled"
    "output": "https://replicate.delivery/...",  # URL when succeeded
    "error": None,  # Error message when failed
}
```

### Video Model Catalog Entry
```python
{
    "model": "wan-video/wan-2.2-i2v-fast",
    "description": "Fast video generation",
    "use_case": "iteration",
    "cost_per_video": 0.10,
    "duration_seconds": 5,
    "resolution": "720p",
    "fps": 30,
    "vendor": "Wan"
}
```
