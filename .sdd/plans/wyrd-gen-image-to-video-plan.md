---
specification: [.sdd/specs/wyrd-gen-image-to-video.md](../specs/wyrd-gen-image-to-video.md)
status: Approved
version: 1.0.0
created: 2025-12-02
last_updated: 2025-12-02
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Wyrd-Gen Image-to-Video Extension - Technical Plan

## Overview

This plan extends wyrd-gen-mcp with image-to-video generation capabilities, adding three new MCP tools that mirror the existing image generation architecture. The implementation follows established patterns: hardcoded model catalog in JSON, tool handlers with `@server.call_tool()` decorator, structured JSON responses, and file path resolution using `WYRD_INVOKE_DIR`.

Key technical strategies:
- **Catalog-driven design**: New `video_model_catalog.json` with use-case categorization and cost/quality metadata
- **First-frame conditioning**: All models treat input image as the literal first frame of generated video
- **Fixed output constraints**: 720p/5s/MP4 hardcoded to simplify interface and ensure model compatibility
- **Image upload via base64**: Convert local images to data URIs for Replicate API compatibility

## Architecture

### System Context

The extension adds a parallel video generation path alongside existing image tools:

```
┌─────────────────┐        stdio (JSON-RPC)      ┌──────────────────────────────────┐
│ Claude Desktop  │◄──────────────────────────────►│       Wyrd-Gen MCP Server        │
│  or Claude Code │                                │                                  │
└─────────────────┘                                │  ┌────────────────────────────┐ │
                                                   │  │ Image Tools (existing)     │ │
                                                   │  │ - generate_image_replicate │ │
                                                   │  │ - list_image_models        │ │
                                                   │  │ - get_model_parameters     │ │
                                                   │  └────────────────────────────┘ │
                                                   │                                  │
                                                   │  ┌────────────────────────────┐ │
                                                   │  │ Video Tools (NEW)          │ │
                                                   │  │ - generate_video_replicate │ │
                                                   │  │ - list_video_models        │ │
                                                   │  │ - get_video_model_params   │ │
                                                   │  └────────────────────────────┘ │
                                                   └───────────────┬──────────────────┘
                                                                   │
                                                          HTTP API │
                                                                   │
                                                   ┌───────────────▼──────────────────┐
                                                   │         Replicate API            │
                                                   │  - Image models (existing)       │
                                                   │  - Video models (Kling, Hailuo,  │
                                                   │    Wan, MiniMax, etc.)           │
                                                   └───────────────┬──────────────────┘
                                                                   │
                                                   ┌───────────────▼──────────────────┐
                                                   │          File System             │
                                                   │  - Images (.png, .jpg, .webp)    │
                                                   │  - Videos (.mp4) NEW             │
                                                   └──────────────────────────────────┘
```

### Components

**New Components**:

1. **Video Model Catalog** (`data/video_model_catalog.json`)
   - Curated list of official vendor models organized by use case
   - Cost, quality ratings, and capability metadata per model
   - Parameter schemas for each model

2. **Video Catalog Loader** (`data/__init__.py` extension)
   - Load and validate video catalog at import time
   - Export `VIDEO_MODELS`, `VIDEO_PARAMETERS` constants
   - Separate validation function for video-specific schema

3. **Video Tool Handlers** (`server.py` additions)
   - `generate_video_replicate()`: Main generation handler
   - `list_video_models_replicate()`: Model discovery
   - `get_video_model_parameters_replicate()`: Parameter introspection

4. **Image Input Handler** (helper in `server.py`)
   - Validate input image exists and is supported format
   - Convert local image to base64 data URI for API submission

**Modified Components**:

1. **Tool Registry** (`TOOLS` list in `server.py`)
   - Add three new Tool definitions with JSON schemas

2. **Tool Router** (`call_tool()` handler)
   - Add routing for new video tool names

## Technical Decisions

### TD-1: Video Model Catalog as Separate JSON File

**Choice**: Create `video_model_catalog.json` alongside existing `model_catalog.json`

**Requirements**: REQ-F-5, REQ-F-6, REQ-F-7, REQ-NF-1

**Rationale**:
- Maintains separation between image and video concerns
- Follows established pattern from image catalog
- Enables independent validation schemas (video models have different required fields)
- Keeps each catalog focused and maintainable
- Alternative (single combined catalog) rejected: would require schema changes, increases complexity

### TD-2: Base64 Data URI for Image Upload

**Choice**: Convert local images to base64 data URIs before Replicate API submission

**Requirements**: REQ-F-12, REQ-F-13

**Rationale**:
- Replicate video models accept both URLs and base64 data URIs for input images
- Data URIs avoid need for external hosting or file transfer service
- Pattern: `data:image/png;base64,{base64_encoded_data}`
- Alternative (upload to temporary URL) rejected: adds complexity, requires cleanup, external dependency
- Alternative (Replicate file upload API) rejected: video models don't consistently support file handles like image models do

### TD-3: Fixed Output Constraints (720p/5s/MP4)

**Choice**: Hardcode resolution, duration, and format rather than exposing as parameters

**Requirements**: REQ-F-8, REQ-F-9, REQ-F-10, Explicit Constraints

**Rationale**:
- Spec explicitly mandates fixed constraints to simplify interface
- 720p and 5s are supported by all selected models (verified in research doc)
- Removes need for per-model capability checking
- Users wanting different settings can use Replicate directly
- Reduces API surface area and potential for invalid combinations

### TD-4: Model Selection by Replicate Model ID

**Choice**: Require exact Replicate model ID (e.g., `kuaishou/kling-v2.5-pro`)

**Requirements**: REQ-F-1, REQ-NF-1

**Rationale**:
- Matches existing image generation pattern (model parameter is Replicate ID)
- Provides consistency across image and video tools
- Alternative (use-case aliases) rejected: adds mapping layer, obscures actual model used
- `list_video_models_replicate` provides use-case categorization for discovery

### TD-5: Use-Case Categorization in Catalog

**Choice**: Tag each model with primary use case (iteration, animation, stylized, photorealistic, premium)

**Requirements**: REQ-F-5, REQ-F-6

**Rationale**:
- Enables users to select models by workflow rather than memorizing model names
- Cost and use-case together support budget-conscious iteration
- Categories derived from research document analysis:
  - **iteration**: Cheapest, fastest (Wan 2.2-i2v-fast)
  - **animation**: Live2D, anime optimized (MiniMax video-01-live)
  - **stylized**: Multiple style presets (PixVerse v4)
  - **photorealistic**: Live-action quality (Hailuo 02, Kling v2.5)
  - **premium**: Maximum quality (Kling v2.1-master)

### TD-6: Validation Schema for Video Catalog

**Choice**: Create `validate_video_model_catalog()` with video-specific required fields

**Requirements**: REQ-F-6, REQ-NF-1

**Rationale**:
- Video models have different attributes than image models (duration_seconds, resolution, fps vs photorealism/artistic_quality)
- Separate validation prevents schema drift between image and video catalogs
- Required fields: `model`, `description`, `use_case`, `cost_per_video`, `duration_seconds`, `resolution`, `fps`
- Reuse validation pattern from existing `validate_model_catalog()`

### TD-7: Error Response Structure

**Choice**: Match existing image tool error format: `{success: false, error: string}`

**Requirements**: REQ-NF-3, REQ-F-15, REQ-F-16

**Rationale**:
- Consistency with existing tools (REQ-NF-1)
- Structured JSON enables programmatic error handling by Claude
- Error messages should be actionable:
  - Input validation: "Input image not found: {path}"
  - Format validation: "Unsupported image format: {ext}. Supported: PNG, JPG, JPEG, WebP"
  - API errors: Include Replicate error message and suggestion

### TD-8: Logging Strategy

**Choice**: Reuse existing logging infrastructure with video-specific log messages

**Requirements**: REQ-NF-4

**Rationale**:
- Existing `logger` instance with `RotatingFileHandler` already configured
- Log same detail level as image generation:
  - Tool invocation with arguments
  - Input image path and validation result
  - Replicate API call (model, prompt, parameters)
  - Output file path(s)
  - Errors with full stack traces
- No new logging configuration needed; follow existing patterns in `generate_image_replicate()`

## Data Model

### Video Model Catalog Schema

```typescript
interface VideoModelCatalog {
  metadata: {
    last_updated: string;        // ISO date
    data_source: string;         // URL reference
    schema_version: string;      // e.g., "1.0"
  };
  models: VideoModel[];
  parameters: Record<string, VideoModelParameters>;
}

interface VideoModel {
  model: string;                 // Replicate model ID
  description: string;           // Use-case guidance
  use_case: "iteration" | "animation" | "stylized" | "photorealistic" | "premium";
  cost_per_video: number;        // USD for 5s 720p video
  duration_seconds: number;      // Fixed: 5
  resolution: string;            // Fixed: "720p"
  fps: number;                   // Model's native fps
  vendor: string;                // e.g., "Kuaishou", "MiniMax"
  notes?: string;                // Additional capability notes
}

interface VideoModelParameters {
  model: string;
  parameters: Record<string, ParameterDef>;
}
```

### Input/Output Data Flow

```typescript
// Input to generate_video_replicate
interface GenerateVideoRequest {
  image: string;              // Local file path to input image
  prompt: string;             // Motion/action description
  model: string;              // Replicate model ID
  output_file_name: string;   // Where to save .mp4
  parameters?: object;        // Model-specific overrides
}

// Output from generate_video_replicate
interface GenerateVideoResponse {
  success: true;
  model: string;
  prompt: string;
  input_image: string;        // Original input path
  saved_files: string[];      // Absolute paths to saved videos
  duration_seconds: number;   // Always 5
  resolution: string;         // Always "720p"
  parameters: object;
}

interface ErrorResponse {
  success: false;
  error: string;
  error_type?: "input_validation" | "api_error" | "file_error";
}
```

## API Design

*Implements REQ-F-1, REQ-F-2, REQ-F-3, REQ-F-4*

### Tool 1: generate_video_replicate (REQ-F-1, REQ-F-4)

```json
{
  "name": "generate_video_replicate",
  "description": "Generate a 5-second 720p MP4 video from an input image using AI models via Replicate. The input image becomes the first frame of the video.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "image": {
        "type": "string",
        "description": "Path to input image file (PNG, JPG, JPEG, or WebP)"
      },
      "prompt": {
        "type": "string",
        "description": "Description of motion/action to apply to the image"
      },
      "model": {
        "type": "string",
        "description": "Replicate model ID. Call list_video_models_replicate to see available models."
      },
      "output_file_name": {
        "type": "string",
        "description": "File name to save the generated video (e.g., 'output.mp4')"
      },
      "parameters": {
        "type": "object",
        "description": "Optional model-specific parameters",
        "default": {}
      }
    },
    "required": ["image", "prompt", "model", "output_file_name"]
  }
}
```

### Tool 2: list_video_models_replicate (REQ-F-2, REQ-NF-2)

```json
{
  "name": "list_video_models_replicate",
  "description": "List available video generation models on Replicate with use-case categorization and cost information",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

**Response format**:
```json
[
  {
    "model": "alibaba/wan-2.2-i2v-fast",
    "description": "Budget iteration model. Fastest and cheapest for rapid prototyping.",
    "use_case": "iteration",
    "cost_per_video": 0.02,
    "vendor": "Alibaba"
  },
  ...
]
```

### Tool 3: get_video_model_parameters_replicate (REQ-F-3)

```json
{
  "name": "get_video_model_parameters_replicate",
  "description": "Get available parameters for a specific video generation model",
  "inputSchema": {
    "type": "object",
    "properties": {
      "model": {
        "type": "string",
        "description": "The Replicate model ID (e.g., 'kuaishou/kling-v2.5-pro')"
      }
    },
    "required": ["model"]
  }
}
```

## Integration Points

### Replicate API Integration

**Pattern**: Same as existing image generation

```python
# Image upload conversion
def image_to_data_uri(file_path: str) -> str:
    """Convert local image to base64 data URI."""
    # Validate file exists and format
    # Read and base64 encode
    # Return data:image/{format};base64,{data}

# API call
model_input = {
    "image": image_to_data_uri(image_path),
    "prompt": prompt,
    # Fixed constraints
    "duration": 5,
    "aspect_ratio": "16:9",  # Most models default; ensures 720p
    **parameters
}
output = replicate_client.run(model, input=model_input)
```

**Output handling**: Video models return FileOutput with `.read()` method, same as image models.

### File System Integration

*Implements REQ-F-11 (collision detection), REQ-F-12, REQ-F-14 (input validation)*

**Patterns reused from image generation**:
- Path resolution via `INVOKE_DIR`
- Collision detection via `get_next_available_path()` (REQ-F-11)
- Parent directory creation: `os.makedirs(dirname, exist_ok=True)`

**New considerations**:
- Input image validation before API call (REQ-F-14): verify file exists, format supported
- Video files are larger (5-50MB typical) but same write pattern

### Catalog Data Integration

**Loading pattern**:
```python
# data/__init__.py additions
VIDEO_CATALOG = load_video_model_catalog()
VIDEO_MODELS = VIDEO_CATALOG["models"]
VIDEO_PARAMETERS = VIDEO_CATALOG["parameters"]
```

## Error Handling, Performance, Security

### Error Strategy

| Error Type | Detection Point | Response |
|-----------|-----------------|----------|
| Input image not found | Before API call | `{success: false, error: "Input image not found: {path}"}` |
| Unsupported format | Before API call | `{success: false, error: "Unsupported format: {ext}. Supported: PNG, JPG, JPEG, WebP"}` |
| Image read failure | Base64 conversion | `{success: false, error: "Failed to read image: {details}"}` |
| Replicate API error | API response | `{success: false, error: "Replicate API error: {message}", error_type: "api_error"}` |
| File write failure | After API success | `{success: false, error: "Failed to save video: {details}"}` |
| Unknown model | Parameter lookup | `{error: "Unknown model: {id}", available_models: [...]}` |

### Performance Targets

- **Input validation**: <100ms (local file check + format validation)
- **Base64 encoding**: <500ms for images up to 10MB
- **Replicate API**: 30-120 seconds depending on model (external, no SLA)
- **File write**: <2 seconds for videos up to 50MB
- **Tool overhead** (excluding API): <1 second total

### Security Measures

- **No credential logging**: Replicate token never in logs (existing pattern)
- **Input validation**: Verify file exists and extension matches content
- **Path resolution**: Use `os.path.abspath()` to resolve traversals (existing pattern)
- **No caching**: Per spec constraints, don't cache API responses

## Testing Strategy

### Unit Tests

**Functions to test**:

1. `image_to_data_uri(path: str) -> str`
   - Valid PNG → correct data URI prefix
   - Valid JPG → correct data URI prefix
   - File not found → raises FileNotFoundError
   - Unsupported format → raises ValueError

2. `validate_video_model_catalog(data: dict)`
   - Valid catalog → passes
   - Missing required model fields → raises ValueError
   - Invalid use_case value → raises ValueError

3. `get_next_available_path()` (existing, verify works for .mp4)
   - No collision → returns original
   - One existing → returns `_0.mp4`
   - Multiple existing → returns correct increment

### Integration Tests

**Critical flows** (map to spec acceptance tests):

| Test | Spec Reference | Validation |
|------|----------------|------------|
| Basic video generation | AT-1 | Generate video from valid image, verify MP4 saved |
| Model listing | AT-2 | All catalog models returned with use_case and cost |
| Parameter discovery | AT-3 | Known model returns schema, unknown returns error |
| Budget model check | AT-4 | Iteration model has lowest cost |
| Input validation | AT-5 | Missing image returns structured error |
| Output collision | AT-6 | Existing file → incremented filename |
| Cost display | AT-7 | cost_per_video in listing response |
| API error handling | AT-8 | Replicate failure returns structured error |

### Manual Verification

Test with real Replicate API:
1. Generate video from sample image
2. Verify video plays correctly
3. Verify duration ~5s, resolution 720p
4. Test with each use-case category model

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Model API parameter differences | Medium | High | Verify each model's actual API schema on Replicate before finalizing catalog |
| Base64 encoding performance for large images | Low | Medium | Most input images <5MB; can add size warning for >10MB |
| Model deprecation/removal on Replicate | Medium | Medium | Document "last verified" date in catalog; periodic verification |
| 720p/5s not supported by some models | Low | High | Pre-verified against research doc; exclude incompatible models |
| Video output larger than expected | Low | Low | Same file handling as images; no explicit size limits needed |

## Dependencies

### Technical Dependencies

**Existing** (no new packages):
- `replicate>=0.34.0`: Already handles video model outputs
- `mcp>=1.0.0`: Tool registration unchanged
- Python stdlib: `base64`, `mimetypes`, `os`, `json`

**New files**:
- `data/video_model_catalog.json`: New catalog file

### Infrastructure Needs

None - runs on existing infrastructure

## Open Questions

- [x] **Does Replicate require URL or accept base64 for video models?**
  - **Answer**: Both work; using base64 data URI to avoid external hosting

- [x] **Are there models that don't support 720p/5s?**
  - **Answer**: All selected models support these constraints per research doc

- [ ] **Which specific Replicate model IDs to include in initial catalog?**
  - **Pending**: Need to verify current availability on Replicate
  - **Candidates from research**:
    - Iteration: `alibaba/wan-2.2-i2v-fast`
    - Animation: `minimax/video-01-live`
    - Stylized: `pixverse/pixverse-v4`
    - Photorealistic: `minimax/hailuo-02`, `kuaishou/kling-v2.5-pro`
    - Premium: `kuaishou/kling-v2.1-master`

- [ ] **Should we add generation progress callback?**
  - **Suggested**: No for v1 - matches existing image pattern (blocking call)
  - **Future**: Could add streaming progress in v2

## Requirements Traceability

| Requirement | Plan Section | Implementation |
|-------------|--------------|----------------|
| REQ-F-1 | API Design: Tool 1, TD-4 | `generate_video_replicate` tool |
| REQ-F-2 | API Design: Tool 2 | `list_video_models_replicate` tool |
| REQ-F-3 | API Design: Tool 3 | `get_video_model_parameters_replicate` tool |
| REQ-F-4 | API Design: Tool 1, Overview | First-frame conditioning (input image = frame 0) |
| REQ-F-5 | TD-1, TD-5 | Use-case categorization in video catalog |
| REQ-F-6 | TD-1, TD-5, TD-6, Data Model | Model metadata (cost, description, use_case) |
| REQ-F-7 | TD-1 | Official vendor models only |
| REQ-F-8 | TD-3 | Fixed 720p resolution |
| REQ-F-9 | TD-3 | Fixed 5s duration |
| REQ-F-10 | TD-3 | Fixed MP4 format |
| REQ-F-11 | Integration Points: File System | Collision detection via `get_next_available_path()` |
| REQ-F-12 | TD-2, Integration Points | Local image path input |
| REQ-F-13 | TD-2, Integration Points | Base64 data URI conversion |
| REQ-F-14 | Integration Points: File System, Error Handling | Input validation (exists + format) |
| REQ-F-15 | TD-7, Error Handling | Structured error for invalid input |
| REQ-F-16 | TD-7, Error Handling | Structured error for API failures |
| REQ-NF-1 | TD-1, TD-4, TD-6, TD-7 | Consistent patterns with image tools |
| REQ-NF-2 | API Design: Tool 2 | Cost in model listings |
| REQ-NF-3 | TD-7 | JSON error responses |
| REQ-NF-4 | TD-8 | Logging with existing infrastructure |
