---
specification: [.sdd/specs/wyrd-gen-image-to-video.md](../specs/wyrd-gen-image-to-video.md)
plan: [.sdd/plans/wyrd-gen-image-to-video-plan.md](../plans/wyrd-gen-image-to-video-plan.md)
status: Draft
version: 1.0.0
created: 2025-12-02
last_updated: 2025-12-02
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Wyrd-Gen Image-to-Video Extension - Task Breakdown

## Task Summary
Total: 12 tasks | Complexity Distribution: 4×S, 6×M, 2×L

## Foundation

### TASK-001: Create Video Model Catalog
**Priority**: Critical | **Complexity**: M | **Dependencies**: None

**Description**: Create `video_model_catalog.json` with the curated video model list, organized by use case with cost/quality metadata and parameter schemas.

**Acceptance Criteria**:
- [ ] JSON file follows schema from plan (metadata, models array, parameters object)
- [ ] Models include: Wan 2.2-i2v-fast (iteration), MiniMax video-01-live (animation), PixVerse v4 (stylized), Hailuo 02 & Kling v2.5-pro (photorealistic), Kling v2.1-master (premium)
- [ ] Each model has: model ID, description, use_case, cost_per_video, duration_seconds (5), resolution (720p), fps, vendor
- [ ] Parameter schemas defined for each model

**Files**: Create: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/data/video_model_catalog.json`

**Testing**: JSON loads without errors; manual schema inspection

---

### TASK-002: Add Video Catalog Loader and Validation
**Priority**: Critical | **Complexity**: M | **Dependencies**: TASK-001

**Description**: Extend `data/__init__.py` with video catalog loading and validation function following the existing pattern.

**Acceptance Criteria**:
- [ ] `validate_video_model_catalog()` validates video-specific required fields
- [ ] `load_video_model_catalog()` loads and validates at import time
- [ ] Exports `VIDEO_MODELS`, `VIDEO_PARAMETERS`, `VIDEO_METADATA` constants
- [ ] Raises `ValueError` on schema violations with descriptive messages

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/data/__init__.py`

**Testing**: Unit tests for validation success/failure cases; import succeeds with valid catalog

---

## Core Tools

### TASK-003: Add Image-to-Data-URI Helper
**Priority**: Critical | **Complexity**: M | **Dependencies**: None

**Description**: Create helper function to convert local image files to base64 data URIs for Replicate API submission.

**Acceptance Criteria**:
- [ ] Validates file exists and is supported format (PNG, JPG, JPEG, WebP)
- [ ] Returns data URI: `data:image/{format};base64,{encoded_data}`
- [ ] Raises `FileNotFoundError` when image doesn't exist
- [ ] Raises `ValueError` for unsupported formats with clear message

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/server.py`

**Testing**: Unit tests with valid PNG/JPG, missing file, unsupported format

---

### TASK-004: Implement generate_video_replicate Tool
**Priority**: Critical | **Complexity**: L | **Dependencies**: TASK-002, TASK-003

**Description**: Implement the main video generation tool handler following the existing `generate_image_replicate` pattern.

**Acceptance Criteria**:
- [ ] Tool registered in `TOOLS` list with correct input schema
- [ ] Handler converts input image to data URI via helper
- [ ] Calls Replicate API with model, prompt, image, and fixed constraints (5s, 720p)
- [ ] Saves output to specified path using `get_next_available_path()` for collision detection
- [ ] Returns success response with model, prompt, input_image, saved_files, duration_seconds, resolution
- [ ] Returns structured error on failure (input validation, API error, file write)
- [ ] Logs all operations at same detail level as image generation

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/server.py`

**Testing**: Integration test with mock Replicate; manual test with real API

---

### TASK-005: Implement list_video_models_replicate Tool
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-002

**Description**: Implement the video model listing tool that returns catalog models with use-case categorization and cost.

**Acceptance Criteria**:
- [ ] Tool registered in `TOOLS` list with empty input schema
- [ ] Handler returns `VIDEO_MODELS` from catalog
- [ ] Response includes model, description, use_case, cost_per_video, vendor for each model

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/server.py`

**Testing**: Verify all catalog models returned with expected fields

---

### TASK-006: Implement get_video_model_parameters_replicate Tool
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-002

**Description**: Implement the video parameter introspection tool following the existing image pattern.

**Acceptance Criteria**:
- [ ] Tool registered in `TOOLS` list with model parameter required
- [ ] Handler looks up model in `VIDEO_PARAMETERS`
- [ ] Returns parameter schema for known model
- [ ] Returns error with available_models list for unknown model

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/server.py`

**Testing**: Test known model returns schema; unknown model returns error

---

### TASK-007: Add Tool Router Cases
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-004, TASK-005, TASK-006

**Description**: Add routing cases in `call_tool()` handler for the three new video tools.

**Acceptance Criteria**:
- [ ] `generate_video_replicate` routes to handler
- [ ] `list_video_models_replicate` routes to handler
- [ ] `get_video_model_parameters_replicate` routes to handler

**Files**: Modify: `wyrd-gen-mcp/server/src/wyrd_gen_mcp/server.py`

**Testing**: Each tool name routes to correct handler

---

## Testing

### TASK-008: Unit Tests for Video Catalog Validation
**Priority**: High | **Complexity**: M | **Dependencies**: TASK-002

**Description**: Create unit tests for `validate_video_model_catalog()` covering success and failure cases.

**Acceptance Criteria**:
- [ ] Test valid catalog passes validation
- [ ] Test missing required model fields raises ValueError
- [ ] Test invalid use_case value raises ValueError
- [ ] Test missing metadata fields raises ValueError
- [ ] Tests don't require external resources

**Files**: Create: `wyrd-gen-mcp/server/tests/test_video_catalog.py`

**Testing**: `pytest tests/test_video_catalog.py` passes

---

### TASK-009: Unit Tests for Image-to-Data-URI Helper
**Priority**: High | **Complexity**: S | **Dependencies**: TASK-003

**Description**: Create unit tests for the image-to-data-URI conversion helper.

**Acceptance Criteria**:
- [ ] Test valid PNG returns correct data URI prefix
- [ ] Test valid JPG returns correct data URI prefix
- [ ] Test missing file raises FileNotFoundError
- [ ] Test unsupported format raises ValueError
- [ ] Tests use mock files (no external dependencies)

**Files**: Create or extend: `wyrd-gen-mcp/server/tests/test_image_utils.py`

**Testing**: `pytest tests/test_image_utils.py` passes

---

### TASK-010: Integration Tests for Video Tools
**Priority**: Medium | **Complexity**: L | **Dependencies**: TASK-007

**Description**: Create integration tests covering the spec acceptance tests (AT-1 through AT-8).

**Acceptance Criteria**:
- [ ] AT-1: Basic video generation with mocked API returns success response
- [ ] AT-2: Model listing returns all catalog models with use_case and cost
- [ ] AT-3: Parameter discovery returns schema for known model, error for unknown
- [ ] AT-4: Iteration model has lowest cost in catalog
- [ ] AT-5: Missing input image returns structured error
- [ ] AT-6: Output collision handling returns incremented filename
- [ ] AT-7: Cost display present in model listing
- [ ] AT-8: API error handling returns structured error with type
- [ ] Tests use mock Replicate client (no real API calls)

**Files**: Create: `wyrd-gen-mcp/server/tests/test_video_tools.py`

**Testing**: `pytest tests/test_video_tools.py` passes

---

## Documentation

### TASK-011: Update README with Video Tools
**Priority**: Medium | **Complexity**: M | **Dependencies**: TASK-007

**Description**: Update the wyrd-gen-mcp README to document the new video generation tools.

**Acceptance Criteria**:
- [ ] Document `generate_video_replicate` tool with parameters and example
- [ ] Document `list_video_models_replicate` tool
- [ ] Document `get_video_model_parameters_replicate` tool
- [ ] Explain use-case categories and cost considerations
- [ ] Note fixed constraints (720p, 5s, MP4)

**Files**: Modify: `wyrd-gen-mcp/README.md`

**Testing**: Documentation review; examples match actual API

---

### TASK-012: Manual Verification with Real API
**Priority**: Medium | **Complexity**: M | **Dependencies**: TASK-007

**Description**: Manually test video generation with the real Replicate API using each use-case category model.

**Acceptance Criteria**:
- [ ] Generate video from sample image with iteration model (Wan)
- [ ] Generate video from sample image with one photorealistic model
- [ ] Verify output is playable MP4
- [ ] Verify duration approximately 5 seconds
- [ ] Verify resolution is 720p
- [ ] Document any model-specific quirks discovered

**Files**: None (verification only)

**Testing**: Manual execution and output inspection

---

## Dependency Graph
```
TASK-001 (Catalog JSON)
    │
    └──> TASK-002 (Catalog Loader) ──┬──> TASK-005 (list_video_models)
                                     │
                                     ├──> TASK-006 (get_video_model_params)
                                     │
TASK-003 (Image-to-URI) ─────────────┴──> TASK-004 (generate_video) ──┐
                                                                       │
                                         TASK-005, TASK-006 ───────────┼──> TASK-007 (Router)
                                                                       │
                         TASK-002 ────────────────────────────────────>│──> TASK-008 (Catalog Tests)
                                                                       │
                         TASK-003 ────────────────────────────────────>│──> TASK-009 (URI Tests)
                                                                       │
                                         TASK-007 ────────────────────>├──> TASK-010 (Integration Tests)
                                                                       │
                                         TASK-007 ────────────────────>├──> TASK-011 (README)
                                                                       │
                                         TASK-007 ────────────────────>└──> TASK-012 (Manual Verification)
```

## Implementation Order
**Phase 1** (Foundation): TASK-001, TASK-003 (parallel, no dependencies)
**Phase 2** (Data Layer): TASK-002
**Phase 3** (Tools): TASK-004, TASK-005, TASK-006 (TASK-005/006 can parallel)
**Phase 4** (Integration): TASK-007
**Phase 5** (Validation): TASK-008, TASK-009, TASK-010, TASK-011 (parallel)
**Phase 6** (Final): TASK-012

## Notes
- **Parallelization**: TASK-001 + TASK-003 can run in parallel; TASK-005 + TASK-006 can run in parallel; Phase 5 tasks can all run in parallel
- **Critical path**: TASK-001 → TASK-002 → TASK-004 → TASK-007 → TASK-010
- **Risk mitigation**: TASK-012 (manual verification) should catch any model-specific issues not covered by mocked tests
