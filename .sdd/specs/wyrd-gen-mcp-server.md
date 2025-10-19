# Wyrd-Gen MCP Server Specification

**Version**: 1.2.0
**Status**: Draft
**Created**: 2025-10-16
**Last Updated**: 2025-10-17

## Executive Summary

Wyrd-Gen is an MCP (Model Context Protocol) server that bridges Claude Desktop/Code with Replicate's AI image generation API, enabling LLMs to generate images through natural language prompts with automatic file management and local storage.

## User Story

As a **Claude Desktop/Code user**, I want **to generate AI images through natural language conversations**, so that **I can create visual content without leaving my AI assistant interface or managing API calls manually**.

## Stakeholders

- **Primary**: Claude Desktop and Claude Code users who need AI image generation capabilities
- **Secondary**:
  - Developers building workflows with image generation
  - Content creators using AI-assisted image creation
  - Replicate API users seeking streamlined integration
- **Tertiary**:
  - MCP server developers looking for reference implementations
  - Anthropic (for MCP ecosystem growth)

## Success Criteria

1. Users can generate images using natural language prompts with 100% success rate when valid credentials are provided
2. Generated images are automatically saved to the user's working directory with predictable file naming
3. Server starts within 2 seconds and responds to image generation requests within the time limits of the underlying Replicate API
4. Zero manual API interaction required - users interact solely through natural language
5. Server handles errors gracefully with clear error messages returned to the user
6. Support for multiple popular image generation models (minimum 4 models)
7. Configuration requires one-time setup with automatic environment management thereafter
8. System NEVER overwrites existing files - automatically increments filenames to prevent data loss
9. Log files rotate automatically when reaching 10MB, maintaining maximum 5 backup files to conserve disk space

## Functional Requirements

### Image Generation

**FR-1: Text-to-Image Generation**
- System SHALL accept a text prompt and generate corresponding AI images
- System SHALL support configurable output file names via `output_file_name` parameter
- System SHALL save generated images to disk automatically
- System SHALL support model-specific parameters passed through a flexible `parameters` object
- Default model SHALL be `black-forest-labs/flux-kontext-pro`

**FR-2: Model Selection**
- System SHALL support multiple image generation models from Replicate
- System SHALL provide a mechanism to list available models with descriptions
- System SHALL include cost and quality metrics for each model:
  - `cost`: Current cost per generation in USD as provided by Replicate
  - `quality`: Subjective quality rating from 1-10 (developer assessment)
  - `cost_efficiency`: Calculated ratio of quality to cost (higher is better)
- Models SHALL include at minimum:
  - `black-forest-labs/flux-kontext-pro` (default)
  - `black-forest-labs/flux-1.1-pro`
  - `google/imagen-4`
  - `ideogram-ai/ideogram-v3-turbo`

**FR-3: Model Parameter Discovery**
- System SHALL provide a tool to query available parameters for specific models
- Parameter information SHALL include:
  - Parameter name and type
  - Valid options/ranges
  - Default values
  - Optional vs required status
  - Human-readable descriptions

**FR-4: File Output Management**
- System SHALL save images relative to the directory where Claude was invoked (captured via `WYRD_INVOKE_DIR` environment variable)
- System SHALL convert relative file paths to absolute paths using invoke directory as base
- System SHALL handle single file outputs (FileOutput with `.read()` method)
- System SHALL handle multiple file outputs with numbered suffixes (e.g., `image_0.png`, `image_1.png`)
- System SHALL preserve file extensions when adding numeric suffixes
- System SHALL NEVER overwrite existing files
- System SHALL automatically find the next available filename by incrementing a counter (e.g., `cat.png` → `cat_1.png` → `cat_2.png`)
- System SHALL return a list of saved file paths in the response

### Tool Interface

**FR-5: MCP Tool Definitions**
- System SHALL expose three MCP tools:
  1. `generate_image` - Generate images with configurable parameters
  2. `list_image_models` - List available models with metadata
  3. `get_model_parameters` - Get parameter schemas for specific models

**FR-6: Response Format**
- All tool responses SHALL be returned as JSON-formatted TextContent
- Successful `generate_image` responses SHALL include:
  - `success: true`
  - `model`: model ID used
  - `prompt`: prompt used
  - `saved_files`: array of absolute file paths
  - `parameters`: parameters passed to the model
- `list_image_models` responses SHALL include for each model:
  - `model`: model ID
  - `description`: human-readable description
  - `best_for`: recommended use cases
  - `cost`: current cost per generation in USD (from Replicate pricing)
  - `quality`: subjective quality rating (1-10 scale, developer assessment)
  - `cost_efficiency`: calculated as `quality / cost` ratio (higher is better)
- Error responses SHALL include:
  - `success: false`
  - `error`: human-readable error message

### Environment and Configuration

**FR-7: Authentication**
- System SHALL require `REPLICATE_API_TOKEN` environment variable
- System SHALL fail fast with clear error message if token is not provided
- Token validation SHALL occur at server startup

**FR-8: Launch Script Integration**
- System SHALL provide TWO shell scripts for different environment loading strategies:
  1. `wyrd-gen.sh` - Uses 1Password CLI for secure secret management:
     - Captures the invoke directory via `pwd`
     - Loads environment variables from `.env` via 1Password CLI (`op run --env-file=.env`)
     - Activates the Python virtual environment
     - Launches the MCP server with `WYRD_INVOKE_DIR` set
  2. `wyrd-gen-remote.sh` - Directly loads `.env` file for non-1Password environments:
     - Captures the invoke directory via `pwd`
     - Sources `.env` file directly (using `set -a; source .env; set +a` pattern)
     - Activates the Python virtual environment
     - Launches the MCP server with `WYRD_INVOKE_DIR` set

**FR-9: Logging**
- System SHALL log to file at `wyrd-gen-mcp.log` in the current working directory
- System SHALL implement log rotation to prevent unbounded disk usage:
  - Maximum log file size: 10MB per file
  - Keep maximum of 5 backup files
  - Use `RotatingFileHandler` from Python logging module
- Logging SHALL include:
  - Invoke directory and current working directory
  - Tool invocations with arguments
  - Replicate API calls and responses
  - File save operations
  - Error traces with full exception details
- Log level SHALL be DEBUG for comprehensive troubleshooting

### MCP Protocol Compliance

**FR-10: Protocol Implementation**
- System SHALL implement MCP server using stdio transport
- System SHALL register handlers for:
  - `list_tools()` - Return available tools
  - `call_tool(name, arguments)` - Execute tool requests
- System SHALL use `mcp.server.Server` for server instance
- System SHALL use `stdio_server()` for transport layer

## Non-Functional Requirements

### Performance

**NFR-1: Startup Time**
- Server initialization SHALL complete within 2 seconds
- Virtual environment activation and module loading SHALL not exceed 3 seconds total

**NFR-2: Image Generation Throughput**
- Server SHALL not add more than 500ms overhead to Replicate API response time
- File I/O for saving images SHALL complete within 1 second for images up to 10MB

**NFR-3: Responsiveness**
- Server SHALL remain responsive to new requests while image generation is in progress (async execution)

### Reliability

**NFR-4: Error Handling**
- System SHALL catch all exceptions in tool handlers and return structured error responses
- System SHALL log all errors with full stack traces
- System SHALL never crash the MCP server due to tool execution errors

**NFR-5: File System Safety**
- System SHALL create parent directories if they don't exist (relies on valid base paths)
- System SHALL handle file write failures gracefully with error messages
- System SHALL use absolute paths to prevent ambiguity
- System SHALL NEVER overwrite existing files without explicit user confirmation
- System SHALL use incrementing file counters to avoid data loss from accidental overwrites

### Security

**NFR-6: Credential Management**
- API tokens SHALL be loaded from environment variables only
- Tokens SHALL NOT be logged or exposed in error messages
- Environment loading SHALL support TWO methods:
  - 1Password CLI (`op run`) for local development with secure secret management (preferred)
  - Direct `.env` file loading for remote/server environments without 1Password CLI

**NFR-7: File System Access**
- System SHALL only write to directories relative to the invoke directory
- System SHALL NOT perform directory traversal outside intended scope
- File operations SHALL validate paths are absolute before writing

### Compatibility

**NFR-8: Python Version**
- System SHALL require Python 3.10 or higher
- System SHALL use modern Python async/await patterns

**NFR-9: Platform Support**
- System SHALL support Linux, macOS, and Windows
- Shell script launcher SHALL use POSIX-compliant bash

**NFR-10: MCP Compatibility**
- System SHALL be compatible with:
  - Claude Desktop (via `claude_desktop_config.json`)
  - Claude Code (via `.claude/mcp.json`)
- System SHALL use MCP Python SDK version >= 1.0.0

### Maintainability

**NFR-11: Code Organization**
- System SHALL follow src-layout package structure
- All business logic SHALL be in `src/wyrd_gen_mcp/server.py`
- Package metadata SHALL be in `pyproject.toml`

**NFR-12: Documentation**
- System SHALL provide comprehensive documentation in `docs/reference/`:
  - MCP protocol overview
  - Replicate API reference
  - Tool usage examples
  - Configuration guide
- README SHALL provide quick start instructions and troubleshooting

### Deployment

**NFR-13: Installation**
- System SHALL be installable via `pip install -e .` for development
- System SHALL provide console script entry point `wyrd-gen-mcp`
- System SHALL use virtual environments for dependency isolation

**NFR-14: Dependency Management**
- System SHALL minimize dependencies (only `mcp` and `replicate` required)
- System SHALL specify exact minimum versions for dependencies

## Explicit Constraints (DO NOT)

- **Do NOT** support image-to-image workflows (only text-to-image in initial scope)
- **Do NOT** implement image editing or modification capabilities
- **Do NOT** cache or store API responses - always fetch fresh from Replicate
- **Do NOT** implement rate limiting (rely on Replicate's rate limits)
- **Do NOT** support streaming or progressive image generation updates
- **Do NOT** validate image content or apply content filtering (rely on model-level filtering)
- **Do NOT** support batch operations across multiple prompts in single request
- **Do NOT** implement retry logic for failed API calls (fail fast with clear errors)
- **Do NOT** support custom model training or fine-tuning
- **Do NOT** include image viewing or preview capabilities (out of scope for MCP server)

## Technical Context

### Existing Stack
- **Language**: Python 3.10+
- **MCP Framework**: `mcp` Python SDK >= 1.0.0
- **API Client**: `replicate` Python SDK >= 0.34.0
- **Transport**: stdio (standard input/output for IPC)
- **Package Manager**: pip with pyproject.toml
- **Build System**: hatchling
- **Logging**: Python `logging.handlers.RotatingFileHandler` for log rotation

### Integration Points
- **Replicate API**: External HTTP API for AI model execution
  - Authentication via API token
  - Model format: `owner/model-name` strings
  - Returns FileOutput objects with `.read()` method or iterables
- **Claude Desktop**: JSON configuration file at OS-specific paths
- **Claude Code**: `.claude/mcp.json` configuration
- **Environment Loading**:
  - **1Password CLI** (optional): `op run --env-file=.env` for secure secret management
  - **Direct .env loading** (fallback): Standard shell sourcing for environments without 1Password CLI
- **File System**: Local disk for image output storage with collision detection

### Must Respect
- **MCP Protocol**: stdio-based JSON-RPC communication
- **Replicate Model API**: Model-specific parameter schemas
- **Python Package Standards**: PEP 517/518 compliant packaging
- **Async Patterns**: asyncio for non-blocking I/O

## Acceptance Tests

### AT-1: Basic Image Generation
**Given** the server is running with valid `REPLICATE_API_TOKEN`
**When** user requests "Generate an image of a cat" with `output_file_name="cat.png"`
**Then** an image file is created at `{INVOKE_DIR}/cat.png` and response indicates success with the saved file path

### AT-2: Custom Model and Parameters
**Given** the server is running
**When** user generates image with `model="google/imagen-4"` and `parameters={"aspect_ratio": "16:9", "output_format": "webp"}`
**Then** image is generated using specified model and parameters, saved successfully, and response includes the model and parameters used

### AT-3: Model Listing
**Given** the server is running
**When** user invokes `list_image_models` tool
**Then** response contains at least 4 models with `model`, `description`, `best_for`, `cost`, `quality`, and `cost_efficiency` fields
**And** `cost_efficiency` equals `quality / cost` for each model

### AT-4: Parameter Discovery
**Given** the server is running
**When** user invokes `get_model_parameters` with `model="google/imagen-4"`
**Then** response contains parameter schemas including aspect_ratio, output_format, safety_filter_level, and negative_prompt

### AT-5: Multiple File Output
**Given** a model that returns multiple images
**When** user generates images with `num_outputs=3` and `output_file_name="batch.png"`
**Then** three files are created: `batch_0.png`, `batch_1.png`, `batch_2.png` and all paths are returned in response

### AT-6: Missing API Token
**Given** `REPLICATE_API_TOKEN` is not set
**When** server attempts to start
**Then** server exits with error code 1 and logs "REPLICATE_API_TOKEN environment variable is required"

### AT-7: Invalid Model
**Given** the server is running
**When** user requests generation with non-existent model
**Then** error response is returned with `success: false` and descriptive error message

### AT-8: File Path Resolution
**Given** server started with `WYRD_INVOKE_DIR=/home/user/projects`
**When** user specifies `output_file_name="images/output.png"`
**Then** file is saved to `/home/user/projects/images/output.png` (absolute path)

### AT-9: Logging Functionality
**Given** the server is running
**When** user generates an image
**Then** log file contains entries for: tool invocation, API call, file save operation, and success/failure status

### AT-10: Error Recovery
**Given** the server is running
**When** an API call fails due to network error
**Then** server returns error response but remains running and responsive to subsequent requests

### AT-11: File Overwrite Protection
**Given** a file `cat.png` already exists in the invoke directory
**When** user generates an image with `output_file_name="cat.png"`
**Then** system creates `cat_1.png` instead and returns the incremented filename in the response

### AT-12: Log Rotation
**Given** the server has been running and `wyrd-gen-mcp.log` has reached 10MB
**When** new log entries are written
**Then** system creates `wyrd-gen-mcp.log.1` and starts fresh `wyrd-gen-mcp.log`, maintaining maximum 5 backup files

### AT-13: Launch Script with 1Password
**Given** `.env` file contains `REPLICATE_API_TOKEN=op://vault/item/field`
**When** server is started via `wyrd-gen.sh`
**Then** 1Password CLI resolves the secret reference and server starts successfully with valid token

### AT-14: Launch Script without 1Password
**Given** `.env` file contains `REPLICATE_API_TOKEN=r8_plaintext_token`
**When** server is started via `wyrd-gen-remote.sh`
**Then** script sources `.env` directly and server starts successfully with valid token

## Open Questions

- [x] Should the server support image-to-image workflows? **Decision: No, out of scope for v1.0**
- [x] Should we implement client-side validation of model parameters before API calls? **Decision: No, rely on Replicate API errors**
- [x] Should we support custom output directories outside the invoke directory? **Decision: No, always use invoke directory as base for security**
- [x] Should the server cache model parameter schemas? **Decision: No, hardcode popular models for simplicity**
- [x] How should we handle 1Password CLI not being installed? **Decision: Provide two launch scripts - one for 1Password CLI (`wyrd-gen.sh`) and one for direct `.env` loading (`wyrd-gen-remote.sh`)**
- [x] Should we allow file overwrites? **Decision: No, always increment filenames to prevent accidental data loss**
- [x] How should we handle log file growth? **Decision: Implement rotating file handler with 10MB max size and 5 backup files**

## Out of Scope

- **Image editing workflows** - Deferred to future version if needed
- **Video generation** - Different use case, separate project
- **Custom model deployment** - Use Replicate's existing models only
- **Web UI or preview** - MCP servers are headless by design
- **Image storage service integration** - Local file system only
- **Multi-user/team features** - Single-user tool
- **Advanced scheduling or queuing** - Direct API calls only
- **Image format conversion** - Use model's native output format
- **Prompt engineering assistance** - User responsibility
- **Cost tracking or billing** - Managed through Replicate account

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-10-16 | Initial specification reverse-engineered from existing implementation |
| 1.1.0 | 2025-10-16 | Added: Dual launch scripts (1Password + direct .env), log rotation (10MB/5 backups), file overwrite protection with auto-incrementing filenames |
| 1.2.0 | 2025-10-17 | Added: Model cost tracking, quality ratings (1-10), and calculated cost-efficiency metrics for `list_image_models` tool |

## Notes

This specification was reverse-engineered from the existing Wyrd-Gen MCP server implementation. All requirements reflect the current state of the codebase as of commit hash `8ce960f`. The specification documents the **as-built** functionality and serves as the source of truth for future development and maintenance.
