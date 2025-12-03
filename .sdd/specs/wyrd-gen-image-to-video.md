---
version: 1.0.0
status: Approved
created: 2025-12-02
last_updated: 2025-12-02
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
---

# Wyrd-Gen Image-to-Video Extension Specification

## Executive Summary

Extend wyrd-gen-mcp to support image-to-video generation via Replicate's video models. This adds the ability to animate static images into short video clips, following the same architectural patterns as the existing text-to-image functionality.

The extension provides a curated catalog of video models organized by use case (budget iteration, animation/Live2D, stylized content, photorealistic, premium quality), with fixed output constraints (720p, 5 seconds, MP4) to simplify the interface while covering the primary creative workflows.

## User Story

As a creative developer using wyrd-gen-mcp, I want to generate short videos from static images, so that I can animate artwork, create motion content, and iterate on video concepts without leaving my Claude Code workflow.

## Stakeholders

- **Primary**: Creative developers using wyrd-gen-mcp for content generation
- **Secondary**: Plugin maintainers (Ronald Roy)

## Success Criteria

1. Users can generate 5-second 720p MP4 videos from a single input image
2. Model selection is use-case driven with clear recommendations (budget, animation, photorealistic, etc.)
3. Cost information is visible in model listings to support budget-conscious iteration
4. The extension follows existing wyrd-gen-mcp patterns (tool structure, error handling, file output)
5. All video models in the catalog are "official" vendor models on Replicate (not community forks)

## Functional Requirements

### Core Video Generation

- **REQ-F-1**: System shall expose a `generate_video_replicate` tool that accepts an input image, prompt, model selection, and output filename
- **REQ-F-2**: System shall expose a `list_video_models_replicate` tool that returns available models with use case categorization and cost information
- **REQ-F-3**: System shall expose a `get_video_model_parameters_replicate` tool that returns model-specific parameter schemas
- **REQ-F-4**: Input image shall be treated as the first frame of the generated video (first-frame conditioning)

### Model Catalog

- **REQ-F-5**: Catalog shall include models covering these use cases:
  - **Iteration/Budget**: Cheapest option for rapid prototyping
  - **Live2D/Anime**: Purpose-built for animation and Live2D content
  - **Stylized/Artistic**: Multiple style presets (anime, 3D, comic, etc.)
  - **Photorealistic**: High-quality live-action style output
  - **Premium**: Maximum quality for final production
- **REQ-F-6**: Each model entry shall include: model ID, description, use case category, cost per video, and quality/capability ratings
- **REQ-F-7**: Catalog shall only include official vendor models from Replicate (Kuaishou/Kling, MiniMax/Hailuo, Alibaba/Wan, etc.)

### Output Handling

- **REQ-F-8**: All generated videos shall be 720p resolution
- **REQ-F-9**: All generated videos shall be 5 seconds duration
- **REQ-F-10**: All generated videos shall be MP4 format
- **REQ-F-11**: Videos shall be saved to the specified output path, following existing file collision detection patterns

### Input Handling

- **REQ-F-12**: System shall accept local image file paths as input
- **REQ-F-13**: System shall convert local images to Replicate-compatible format (URL or base64) before API submission
- **REQ-F-14**: System shall validate that input file exists and is a supported image format (PNG, JPG, JPEG, WebP)
- **REQ-F-15**: System shall return structured error with descriptive message when input image is corrupt, unreadable, or unsupported format
- **REQ-F-16**: System shall return structured error when Replicate API call fails (timeout, rate limit, server error), including error type and actionable message

## Non-Functional Requirements

- **REQ-NF-1** (Consistency): Tool naming, parameter structure, and response format shall match existing image generation tools
- **REQ-NF-2** (Cost Transparency): Cost per video shall be displayed in model listings and optionally in generation responses
- **REQ-NF-3** (Error Handling): All errors shall return structured JSON responses matching existing error patterns
- **REQ-NF-4** (Logging): All video generation requests shall be logged with the same detail level as image generation

## Explicit Constraints (DO NOT)

- Do NOT support start+end frame (keyframe interpolation) - only single image input
- Do NOT expose resolution, duration, or format parameters - these are fixed at 720p/5s/MP4
- Do NOT include community/accelerated model variants (e.g., "WaveSpeed Wan") - only official vendor models
- Do NOT implement video-to-video or text-to-video - only image-to-video
- Do NOT cache or store API responses
- Do NOT implement model chaining or multi-step generation

## Technical Context

- **Existing Stack**: Python MCP server, Replicate SDK, async I/O
- **Integration Points**: Replicate API (video models), existing wyrd-gen-mcp architecture
- **Input Constraints**: Video models have input image dimension limits (to be verified during planning phase)
- **Patterns to Respect**:
  - Hardcoded model catalog in JSON (same as `model_catalog.json`)
  - Tool handler pattern with `@server.call_tool()` decorator
  - Structured JSON responses with success/error states
  - File path resolution using `WYRD_INVOKE_DIR`

## Acceptance Tests

1. **Basic Video Generation**: Given a valid image path, prompt, model, and output filename, the system generates a 5-second 720p MP4 video saved to the specified location
2. **Model Listing**: `list_video_models_replicate` returns all cataloged models with use case categories and cost information
3. **Parameter Discovery**: `get_video_model_parameters_replicate` returns the parameter schema for a specified model
4. **Budget Model Selection**: The "iteration" use case model is the cheapest option in the catalog
5. **Input Validation**: System returns structured error when input image doesn't exist or is unsupported format
6. **Output Collision**: System handles filename collisions using existing pattern (cat.mp4 → cat_1.mp4)
7. **Cost Display**: Model cost per video is included in listing response
8. **API Error Handling**: System returns structured error with type and message when Replicate API fails

## Open Questions

- [ ] Which specific Replicate model IDs map to each use case? (Requires verification against current Replicate catalog)
- [ ] Does Replicate require image upload to URL or accept base64 for video models?
- [ ] Are there models that don't support 720p/5s constraints that should be excluded?

## Out of Scope

- Text-to-video generation (no input image)
- Video-to-video transformation
- Keyframe interpolation (start+end frame)
- Variable resolution/duration/format
- Local video model support (GPU-based generation)
- Video upscaling or post-processing
- Audio generation or synchronization

---

**Next Phase**: Once approved, use `/spiral-grove:plan-generation` to create technical implementation plan.
