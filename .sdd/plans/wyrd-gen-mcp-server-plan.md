# Wyrd-Gen MCP Server - Technical Plan

**Specification**: [.sdd/specs/wyrd-gen-mcp-server.md](../specs/wyrd-gen-mcp-server.md)
**Version**: 1.1.0
**Status**: Draft
**Created**: 2025-10-16
**Last Updated**: 2025-10-18 (Merged cost-quality-metrics into main plan)

## Overview

This plan addresses the implementation gaps between the Wyrd-Gen MCP server specification v1.2.0 and the current codebase. The system is ~85% complete, with four primary gaps requiring implementation:
1. **Log rotation** - Prevent unbounded disk usage with rotating file handler
2. **File collision detection** - Auto-increment filenames to prevent overwrites (cat.png → cat_1.png)
3. **Launch script environment handling** - Fix environment variable propagation in remote script
4. **Cost & quality metrics** - Add pricing, quality ratings, and cost-efficiency to model discovery tool

The architecture leverages Python's MCP SDK for stdio-based communication with Claude Desktop/Code, using Replicate's API for AI image generation.

## Architecture

### System Context

Wyrd-Gen operates as a headless MCP server bridging Claude clients with Replicate's image generation API:

```
┌─────────────────┐        stdio (JSON-RPC)      ┌──────────────────┐
│ Claude Desktop  │◄──────────────────────────────►│  Wyrd-Gen MCP   │
│  or Claude Code │                                │     Server      │
└─────────────────┘                                └────────┬─────────┘
                                                            │
                                                   HTTP API │
                                                            │
                                                   ┌────────▼─────────┐
                                                   │  Replicate API   │
                                                   │  (External SaaS) │
                                                   └──────────────────┘
                                                            │
                                                   ┌────────▼─────────┐
                                                   │   File System    │
                                                   │ (Local Storage)  │
                                                   └──────────────────┘
```

The server:
- Receives tool invocation requests via stdio
- Translates natural language prompts to Replicate API calls
- Handles binary image data and saves to user's working directory
- Returns JSON responses with file paths and metadata

### Component Overview

**Existing Components** (Already Implemented):
1. **MCP Server Core** (`server.py:397-441`): Handles stdio transport and request routing
2. **Tool Registry** (`server.py:48-99`): Defines three MCP tools with JSON schemas
3. **Image Generation Handler** (`server.py:102-208`): Orchestrates Replicate API calls and file I/O
4. **Model Discovery Tools** (`server.py:211-394`): Provides model listing and parameter introspection
5. **Environment Loader** (`server.py:16-45`): Validates API token and configures logging

**Components Requiring Implementation**:
1. **Log Rotation Manager**: Replace basic FileHandler with RotatingFileHandler
2. **File Collision Detector**: Add filename incrementing logic before write operations
3. **Launch Script Environment Exporter**: Fix environment variable propagation in remote script

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                         Wyrd-Gen MCP Server                         │
│                                                                     │
│  ┌──────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│  │   Tool       │    │   Call Tool     │    │   Environment   │  │
│  │  Registry    │    │    Handler      │    │   Validator     │  │
│  │  (TOOLS)     │    │  (@call_tool)   │    │  (Token Check)  │  │
│  └──────────────┘    └────────┬────────┘    └─────────────────┘  │
│                                │                                   │
│         ┌──────────────────────┼──────────────────────┐           │
│         │                      │                      │           │
│  ┌──────▼────────┐  ┌──────────▼────────┐  ┌─────────▼────────┐ │
│  │ generate_     │  │ list_image_       │  │ get_model_       │ │
│  │   image       │  │   models          │  │   parameters     │ │
│  └───────┬───────┘  └───────────────────┘  └──────────────────┘ │
│          │                                                        │
│  ┌───────▼───────────────────────────────┐                       │
│  │      Replicate Client Wrapper         │                       │
│  │   (replicate_client.run())            │                       │
│  └───────┬───────────────────────────────┘                       │
│          │                                                        │
│  ┌───────▼───────────────────────────────┐                       │
│  │   [NEW] File Collision Detector       │                       │
│  │   - Check if file exists              │                       │
│  │   - Increment counter until unique    │                       │
│  └───────┬───────────────────────────────┘                       │
│          │                                                        │
│  ┌───────▼───────────────────────────────┐                       │
│  │        File Writer (wb mode)          │                       │
│  │   - Save FileOutput.read() to disk    │                       │
│  │   - Handle single/multiple outputs    │                       │
│  └───────────────────────────────────────┘                       │
│                                                                   │
│  ┌───────────────────────────────────────┐                       │
│  │  [NEW] RotatingFileHandler Logger     │                       │
│  │   - 10MB max per file                 │                       │
│  │   - 5 backup files                    │                       │
│  └───────────────────────────────────────┘                       │
└────────────────────────────────────────────────────────────────────┘
```

## Technical Decisions

### Decision 1: Log Rotation Implementation
**Context**: Spec requires log rotation to prevent unbounded disk usage, but current code uses basic FileHandler

**Options Considered**:
- **Option A**: Use Python's built-in `logging.handlers.RotatingFileHandler`
  - **Pros**: Standard library, zero dependencies, automatic rotation, well-tested
  - **Cons**: None significant
- **Option B**: Custom log rotation logic with manual file management
  - **Pros**: More control over rotation logic
  - **Cons**: Reinvents the wheel, more code to maintain, potential bugs
- **Option C**: External logging library (loguru, structlog)
  - **Pros**: More features, better formatting
  - **Cons**: Adds dependencies, overkill for simple use case

**Decision**: Option A - Use `RotatingFileHandler`

**Rationale**: Standard library solution perfectly matches requirements (10MB max, 5 backups). No reason to add dependencies or custom code when built-in handler provides exactly what's needed. Already using `logging` module, so this is a one-line change in handler initialization.

### Decision 2: File Overwrite Protection Strategy
**Context**: Spec requires automatic filename incrementing to prevent data loss (cat.png → cat_1.png → cat_2.png)

**Options Considered**:
- **Option A**: Check-and-increment pattern with counter loop
  - **Pros**: Simple, predictable naming, easy to understand
  - **Cons**: Race condition if multiple processes write simultaneously
- **Option B**: UUID/timestamp-based unique filenames
  - **Pros**: Guaranteed uniqueness, no race conditions
  - **Cons**: Unpredictable filenames, harder for users to find files
- **Option C**: Prompt user for confirmation before overwrite
  - **Pros**: User in control
  - **Cons**: Breaks MCP async model, adds interaction complexity

**Decision**: Option A - Check-and-increment with counter loop

**Rationale**:
- Spec explicitly requires incrementing pattern (AT-11)
- Single-user tool (NFR constraint) eliminates race condition concern
- Predictable naming helps users locate generated files
- Simple implementation: extract base/ext, loop `while os.path.exists()`, increment counter

### Decision 3: Launch Script Environment Propagation
**Context**: `wyrd-gen-remote.sh` needs to export `WYRD_INVOKE_DIR` and properly load `.env` file

**Options Considered**:
- **Option A**: Use `set -a; source .env; set +a` pattern
  - **Pros**: Standard bash idiom for exporting all vars from file, works with plain key=value syntax
  - **Cons**: Requires users to use simple key=value format in .env (no `export` prefix needed)
- **Option B**: Parse .env manually and export each variable
  - **Pros**: More control over variable handling
  - **Cons**: Complex, error-prone, doesn't handle comments/edge cases well
- **Option C**: Use `python-dotenv` or similar tool
  - **Pros**: Robust parsing
  - **Cons**: Adds dependency just for shell script, overkill

**Decision**: Option A - Use `set -a` pattern and explicit `export WYRD_INVOKE_DIR`

**Rationale**:
- `set -a` enables automatic export for all variable assignments, then `source .env` imports them
- `set +a` disables auto-export after sourcing
- Standard pattern in shell scripting, well-documented
- Explicitly export `WYRD_INVOKE_DIR` to ensure it's available to Python process
- Matches how 1Password script handles environment (just different loading mechanism)

### Decision 4: Keep Model Parameters Hardcoded
**Context**: Current implementation uses hardcoded model parameter schemas (server.py:246-383)

**Options Considered**:
- **Option A**: Keep hardcoded schemas
  - **Pros**: Fast, zero API calls, works offline, current implementation
  - **Cons**: Requires manual updates when models change
- **Option B**: Fetch schemas from Replicate API dynamically
  - **Pros**: Always up-to-date
  - **Cons**: Adds latency, API call overhead, requires error handling for API failures

**Decision**: Option A - Keep hardcoded schemas (no change needed)

**Rationale**:
- Spec explicitly states "hardcode popular models for simplicity" (Open Questions)
- Image model parameters rarely change
- Provides better UX (instant response vs API roundtrip)
- Aligns with existing architecture
- Four popular models are already documented and tested

### Decision 5: Model Pricing & Quality Metrics
**Context**: Spec v1.2.0 adds cost tracking, quality ratings, and cost-efficiency calculation to `list_image_models` tool (FR-2, AT-3)

**Options Considered**:
- **Option A: Hardcoded in source** (Chosen)
  - **Pros**: Simple, no runtime dependencies, fast, consistent with existing pattern
  - **Cons**: Requires code changes when prices update, may become stale
- **Option B: Fetch from Replicate API at runtime**
  - **Pros**: Always current
  - **Cons**: Replicate doesn't expose pricing via API, would require web scraping (brittle)
- **Option C: External config file**
  - **Pros**: Easy to update without code changes
  - **Cons**: Adds deployment complexity, file management overhead

**Decision**: Hardcode pricing in source code (Option A)

**Rationale**:
- Existing codebase already uses this pattern for model metadata (server.py:214-235)
- Replicate pricing is relatively stable (changes quarterly at most)
- No public Replicate API endpoint for pricing data
- Simple maintenance: update values when prices change (same process as updating descriptions)
- Keeps the tool fast and dependency-free

**Quality Rating Scale**:
- **Scale**: 1-10 integer (subjective developer assessment)
- **Basis**: Model capabilities, community feedback, known use cases
- **Examples**:
  - flux-kontext-pro: 9/10 (premium features, strong prompt following)
  - flux-1.1-pro: 8/10 (excellent general purpose, less specialized)
  - imagen-4: 9/10 (Google's latest, exceptional photorealism)
  - ideogram-v3-turbo: 7/10 (fast, good for text-in-images)

**Cost-Efficiency Calculation**:
- **Formula**: `cost_efficiency = quality / cost`
- **Interpretation**: Higher values = better value (more quality per dollar)
- **Examples**:
  - flux-kontext-pro: 9 ÷ 0.04 = 225.0
  - ideogram-v3-turbo: 7 ÷ 0.03 = 233.3 (best efficiency despite lower quality)

## Data Model

### No Database Required

This is a stateless service - all data flows through without persistence:

**Input Data**:
```typescript
interface GenerateImageRequest {
  prompt: string;                    // User's natural language description
  model?: string;                    // Replicate model ID (default: flux-kontext-pro)
  output_file_name: string;          // Required: where to save (relative or absolute)
  parameters?: Record<string, any>;  // Model-specific options (aspect_ratio, etc.)
}
```

**Output Data**:
```typescript
interface GenerateImageResponse {
  success: boolean;
  model: string;              // Model ID used
  prompt: string;             // Prompt sent to API
  saved_files: string[];      // Absolute paths to saved images
  parameters: object;         // Parameters used in API call
}

interface ErrorResponse {
  success: false;
  error: string;             // Human-readable error message
}
```

**File System State**:
- Images saved to `{INVOKE_DIR}/{output_file_name}` with automatic incrementing
- Log file at `{CWD}/wyrd-gen-mcp.log` with rotation at 10MB
- No caching, no intermediate storage

## API Design

### Existing Endpoints (No Changes Required)

The MCP tools are already correctly designed per spec:

**Tool 1: generate_image**
```json
{
  "name": "generate_image",
  "inputSchema": {
    "type": "object",
    "properties": {
      "prompt": {"type": "string"},
      "model": {"type": "string", "default": "black-forest-labs/flux-schnell"},
      "output_file_name": {"type": "string"},
      "parameters": {"type": "object", "default": {}}
    },
    "required": ["prompt", "output_file_name"]
  }
}
```

**Tool 2: list_image_models** (Enhanced in v1.2.0)
```json
{
  "name": "list_image_models",
  "inputSchema": {
    "type": "object",
    "properties": {}
  }
}
```

**Response Enhancement (v1.2.0)**:
Each model now includes pricing and quality information:
```typescript
interface ModelInfo {
  model: string;           // e.g., "black-forest-labs/flux-schnell"
  description: string;     // Human-readable description
  best_for: string;        // Recommended use cases
  cost: number;            // Cost per generation in USD (e.g., 0.04)
  quality: number;         // Quality rating 1-10 (e.g., 9)
  cost_efficiency: number; // Calculated: quality / cost (e.g., 225.0)
}
```

**Tool 3: get_model_parameters**
```json
{
  "name": "get_model_parameters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "model": {"type": "string"}
    },
    "required": ["model"]
  }
}
```

**Response Format**:
- All responses return `list[TextContent]` with JSON-formatted text
- Error handling via try/except wrapping tool handlers (server.py:422-428)

## Integration Points

### Internal Systems

**MCP SDK Integration** (server.py:12-14, 397-441):
- Uses `mcp.server.Server` for protocol handling
- Decorators: `@server.list_tools()`, `@server.call_tool()`
- Transport: `stdio_server()` provides read/write streams
- No changes needed - already correctly implemented

**Logging Integration** (server.py:20-32):
- **Current**: `logging.FileHandler` writing to `wyrd-gen-mcp.log`
- **Required Change**: Replace with `logging.handlers.RotatingFileHandler`
- Integration point: Lines 20-28 in server.py

### External Systems

**Replicate API** (server.py:44, 134-142):
- Client initialization: `replicate.Client(api_token=REPLICATE_API_TOKEN)`
- API call pattern: `replicate_client.run(model, input=model_input)`
- Returns: FileOutput objects with `.read()` method or iterables of FileOutputs
- Error handling: Let exceptions propagate to tool handler wrapper
- No changes needed

**File System** (server.py:123-196):
- **Current behavior**: Direct write to `{INVOKE_DIR}/{output_file_name}`
- **Required changes**:
  - Add collision detection before line 152 (single file) and line 173 (multiple files)
  - Implement `find_available_filename(path: str) -> str` helper function
  - Call before each file write operation

**Environment Loading**:
- **1Password Script** (wyrd-gen.sh): Already correct - uses `op run --env-file=.env`
- **Remote Script** (wyrd-gen-remote.sh): Needs fix on lines 9-10
  - Current: `source .env` without export
  - Required: `set -a; source .env; set +a` pattern with explicit `WYRD_INVOKE_DIR` export

## State Management

**Process-Level State**:
- Replicate client initialized once at startup (server.py:44)
- Logger configured once at module load (server.py:20-32)
- No shared state between requests - fully async and stateless

**Environment Variables**:
- `REPLICATE_API_TOKEN`: Required, validated at startup (server.py:35-39)
- `WYRD_INVOKE_DIR`: Set by launch scripts, used for file path resolution (server.py:18, 125-126)

**No Caching Strategy Needed**:
- Spec explicitly states "Do NOT cache or store API responses" (Explicit Constraints)
- Always fetch fresh from Replicate
- Model parameter schemas are hardcoded, not cached dynamically

## Error Handling Strategy

### Validation Errors

**API Token Validation** (server.py:35-39):
- **Current**: Fail fast with sys.exit(1) at startup - CORRECT
- **Strategy**: No recovery possible, clear error message to stderr and log
- **No change needed**

**Missing Required Parameters**:
- **Current**: MCP SDK validates against inputSchema automatically
- **Strategy**: Let SDK handle validation, return structured error to client
- **No change needed**

### External Service Failures

**Replicate API Errors** (server.py:422-428):
- **Current**: Try/except wrapper catches all exceptions in tool handlers
- **Strategy**: Return `{success: false, error: str(e)}` - per spec "fail fast with clear errors"
- **Spec constraint**: "Do NOT implement retry logic" (Explicit Constraints)
- **No change needed**

### File System Errors

**Directory Creation**:
- **Current**: Relies on valid base paths (NFR-5: "create parent directories if they don't exist")
- **Strategy**: Python's `open()` will fail if parent doesn't exist - let error propagate
- **Alternative consideration**: Could add `os.makedirs(os.path.dirname(path), exist_ok=True)` before writes
- **Decision**: Add directory creation for better UX (not in spec but improves reliability)

**Write Failures**:
- **Current**: No explicit handling, exceptions caught by tool wrapper
- **Strategy**: Let try/except wrapper catch IOError, return structured error
- **No change needed**

**File Overwrite Protection**:
- **Required**: Implement collision detector that always finds next available filename
- **Strategy**: While loop checking `os.path.exists()`, increment counter, no error thrown
- **New implementation needed**

### Unexpected Errors

**Logging Strategy** (server.py:422-428):
- **Current**: `logger.exception()` logs full stack trace before returning error
- **Requirement**: NFR-4 "log all errors with full stack traces"
- **No change needed**

**Server Stability**:
- **Current**: Tool handler wrapper prevents crashes (try/except at server.py:422-428)
- **Requirement**: NFR-4 "never crash the MCP server due to tool execution errors"
- **No change needed**

## Performance Considerations

### Expected Load

**Typical Usage Pattern**:
- Interactive, human-in-the-loop (user asking Claude to generate images)
- 1-5 requests per minute maximum
- Single-user desktop application
- No concurrent request handling needed (stdio is sequential)

**Replicate API Performance**:
- Response time: 5-30 seconds depending on model
- Image size: 1-5MB typically
- No SLA guarantees (external service)

### Optimization Strategy

**Current Implementation Already Optimized**:
- Async I/O with asyncio (server.py:102, 211, 240, 397-441)
- No unnecessary API calls (hardcoded model schemas)
- Direct file writes without buffering layers
- Minimal overhead (<500ms per NFR-2)

**File I/O Performance**:
- **Requirement**: NFR-2 "File I/O for saving images SHALL complete within 1 second for images up to 10MB"
- **Current**: Direct `FileOutput.read()` → `file.write()` pattern
- **Analysis**: 10MB / 1s = 10MB/s - easily achievable on modern storage
- **No optimization needed**

**Collision Detection Impact**:
- **New operation**: `os.path.exists()` check in loop
- **Cost**: <1ms per check (metadata lookup, no file read)
- **Worst case**: 100 existing files = 100ms overhead
- **Acceptable**: Well within 500ms overhead budget

### Monitoring Approach

**Current Logging Coverage** (server.py:104-142, 210-242):
- Tool invocations with arguments
- Replicate API calls with model/input
- File save operations with paths
- Errors with full stack traces

**Metrics to Track** (already logged):
- Request count (implicit in log entries)
- Error rate (exception logs)
- File operations (saved file paths)

**No additional monitoring needed** - comprehensive logging already provides observability

## Security Design

### Authentication

**API Token Handling** (server.py:35-44):
- **Current**: Load from env var, validate at startup, pass to Replicate client
- **Requirement**: NFR-6 "Tokens SHALL NOT be logged or exposed in error messages"
- **Validation**: Code correctly uses token without logging it
- **No change needed**

### Authorization

**File System Access Control**:
- **Requirement**: NFR-7 "SHALL only write to directories relative to invoke directory"
- **Current implementation**: Converts relative paths to absolute using `INVOKE_DIR` as base (server.py:124-127)
- **Security check**: Uses `os.path.abspath()` which resolves `..` traversals
- **Gap**: No explicit validation that final path is under `INVOKE_DIR`
- **Risk**: Low (user controls both invoke dir and output path, single-user tool)
- **Decision**: Accept current implementation - spec doesn't require strict sandboxing, states "validate paths are absolute before writing" which is done

### Data Protection

**Credential Management**:
- **Two modes per spec FR-8**:
  1. 1Password CLI (`wyrd-gen.sh`): Secrets never touch filesystem
  2. Direct `.env` loading (`wyrd-gen-remote.sh`): Plaintext in file (user responsibility)
- **Current**: Both scripts implemented, choice left to user
- **No change needed**

**Token Security**:
- Never logged (verified in code review)
- Not included in error messages (generic exception handling)
- Not exposed in responses (only success/error/file paths returned)

### Rate Limiting

**Spec Constraint**: "Do NOT implement rate limiting (rely on Replicate's rate limits)"
- Strategy: Let Replicate API return 429 errors, propagate to user
- No implementation needed

## Testing Strategy

### Unit Tests

**Not currently implemented, but recommended approach**:

**Functions to test**:
1. `find_available_filename(path: str) -> str` (NEW function)
   - Test: Existing file → returns `filename_1.ext`
   - Test: Multiple collisions → returns `filename_N.ext`
   - Test: No collision → returns original path
   - Test: No extension → returns `filename_N`

2. `generate_image()` handler
   - Mock Replicate client
   - Test parameter handling
   - Test file path resolution
   - Test multiple file outputs

3. `list_image_models()` handler
   - Test returns 4+ models
   - Test response format

4. `get_model_parameters()` handler
   - Test known models return schemas
   - Test unknown model returns error

**Testing approach**: Use `pytest` with `unittest.mock` for Replicate client

### Integration Tests

**Manual testing approach** (spec provides Acceptance Tests AT-1 through AT-14):

**Critical flows to verify**:
1. **AT-1**: Basic image generation with file save
2. **AT-11**: File overwrite protection (new functionality)
3. **AT-12**: Log rotation at 10MB (new functionality)
4. **AT-13**: Launch with 1Password script
5. **AT-14**: Launch with remote script (fixed functionality)

**Test environment**:
- Real Replicate API (use test token with low rate limits)
- Real Claude Desktop or Claude Code MCP client
- Verify log file rotation by generating log entries until 10MB

### E2E Tests

**Testing via Claude Desktop/Code**:

**Test scenarios**:
1. Natural language request: "Generate an image of a sunset"
2. Custom model: "Use Imagen-4 to create a professional product photo"
3. Parameters: "Generate a 16:9 landscape image"
4. File naming: "Save it as sunset.png" (then repeat to test collision)

**Validation**:
- Images saved to correct directory
- Filenames increment when collisions occur
- Log file rotates at 10MB
- Error messages are clear and actionable

### Performance Tests

**Not required by spec**, but simple manual validation:

**Overhead test**:
1. Time `replicate_client.run()` directly (baseline)
2. Time full MCP request (baseline + overhead)
3. Verify overhead <500ms (NFR-2)

**File I/O test**:
1. Generate 10MB image
2. Measure time from API response to file write complete
3. Verify <1s (NFR-2)

## Deployment Considerations

### Database Migrations

**Not applicable** - No database in this architecture

### Feature Flags

**Not applicable** - Simple enough to deploy atomically

### Rollback Plan

**Strategy**:
1. Git revert to previous commit
2. Restart MCP server (Claude Desktop restart or Claude Code MCP reconnect)
3. No data migration needed (stateless)

**Safe rollback conditions**:
- Log file format unchanged (just handler swap)
- File collision logic is additive (old code still works, just doesn't prevent overwrites)
- Launch script changes are backwards compatible

### Monitoring

**During rollout**:
1. Watch `wyrd-gen-mcp.log` for errors
2. Verify log rotation creates `.log.1` backup file
3. Check file collision detection in logs (should show incremented filenames)
4. Test both launch scripts work

**Success criteria**:
- No crashes or unexpected errors in log
- AT-11 (file collision) passes
- AT-12 (log rotation) passes
- AT-14 (remote launch script) passes

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Log rotation fails silently causing disk fill | Low | Medium | Test by generating >10MB of logs, verify backup files created. Python's RotatingFileHandler is battle-tested. |
| File collision detector creates race condition | Very Low | Low | Single-user tool, sequential requests via stdio, no concurrent writes possible. |
| Launch script environment variable not propagated | Medium | High | **Already identified** - fix in wyrd-gen-remote.sh. Test with `echo $WYRD_INVOKE_DIR` inside Python. |
| Breaking existing functionality during refactor | Low | High | Minimize changes - only touch logging initialization, add collision function, fix shell script. Run AT-1 through AT-10 after changes. |
| RotatingFileHandler permissions issues on Windows | Low | Medium | Use same log file path as current implementation (CWD). If issues arise, document in README. |
| Filename incrementing breaks with special characters | Low | Low | Use `os.path.splitext()` which handles edge cases. Test with filenames containing dots, spaces, unicode. |

## Dependencies

### Technical Dependencies

**No new dependencies required**:
- `logging.handlers.RotatingFileHandler` is in Python stdlib
- `os.path.exists()` is in Python stdlib
- Shell script uses standard bash builtins (`set`, `source`)

**Existing dependencies** (pyproject.toml:7-10):
```toml
dependencies = [
    "mcp>=1.0.0",
    "replicate>=0.34.0",
]
```

**Python version**: >=3.10 (already specified in pyproject.toml:6)

### Team Dependencies

**No team dependencies**:
- Solo developer project
- No external approvals needed
- No shared infrastructure changes

### Infrastructure Needs

**No infrastructure changes**:
- Runs on user's local machine
- No deployment pipeline
- No CI/CD integration required

## Timeline Estimate

**Total estimated time: 3-4 hours**

### Log Rotation Implementation
**Estimate: 30 minutes**
- Replace `FileHandler` with `RotatingFileHandler` (5 mins)
- Add maxBytes=10485760, backupCount=5 parameters (2 mins)
- Test log rotation by generating >10MB logs (20 mins)
- Verify backup files created with correct naming (3 mins)

### File Collision Detection
**Estimate: 1 hour**
- Write `find_available_filename()` helper function (15 mins)
- Integrate into single-file write path (server.py:~152) (10 mins)
- Integrate into multi-file write path (server.py:~173) (10 mins)
- Test with existing files to verify incrementing (15 mins)
- Test edge cases (no extension, multiple collisions) (10 mins)

### Launch Script Fix
**Estimate: 30 minutes**
- Update wyrd-gen-remote.sh with `set -a` pattern (5 mins)
- Add explicit `export WYRD_INVOKE_DIR` (2 mins)
- Test script loads .env correctly (10 mins)
- Test WYRD_INVOKE_DIR propagates to Python (10 mins)
- Verify file paths resolve correctly (3 mins)

### Cost & Quality Metrics Implementation
**Estimate: 1 hour**
- Add three fields to each of 4 models in `list_image_models()` (15 mins)
  - cost, quality, cost_efficiency fields
  - Calculate values based on Replicate pricing and quality assessment
- Research current Replicate pricing to verify accuracy (20 mins)
- Update code comments with pricing source and last verified date (5 mins)
- Manual testing via Claude Desktop to verify response format (15 mins)
- Test all 4 models return correct fields and calculations (5 mins)

### Testing & Documentation
**Estimate: 45 minutes**
- Run all 14 Acceptance Tests including AT-3 (model listing) (30 mins)
- Update CLAUDE.md if needed (10 mins)
- Verify no regressions in existing functionality (5 mins)

## Open Questions

- [x] **Should we add parent directory creation for output paths?**
  - **Decision**: Yes - add `os.makedirs(os.path.dirname(path), exist_ok=True)` before file writes
  - **Rationale**: Improves UX, low risk, spec NFR-5 suggests this behavior

- [x] **Should we validate output path stays within INVOKE_DIR?**
  - **Decision**: No - current implementation is sufficient
  - **Rationale**: Single-user tool, user controls both sides, spec doesn't require strict sandboxing

- [ ] **Should we add unit tests as part of this implementation?**
  - **Suggested**: Yes, at minimum test `find_available_filename()` function
  - **Awaiting user input**: Does this project have testing infrastructure set up?

- [ ] **Should we version bump after these changes?**
  - **Suggested**: Bump to v0.2.0 (minor version for new features: collision detection, log rotation)
  - **Awaiting user input**: What's the versioning strategy?

## Appendix

### Existing Code Analysis

**Well-designed patterns to preserve**:

1. **Tool handler wrapper** (server.py:422-428):
   ```python
   try:
       if name == "generate_image":
           return await generate_image(arguments)
       # ...
   except Exception as e:
       logger.exception(f"Error in tool {name}: {e}")
       return [TextContent(type="text", text=json.dumps({
           "success": False, "error": str(e)
       }, indent=2))]
   ```
   - **Why preserve**: Comprehensive error handling, meets NFR-4
   - **Don't change**: This pattern is solid

2. **Environment variable validation** (server.py:35-39):
   ```python
   REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN")
   if not REPLICATE_API_TOKEN:
       logger.error("REPLICATE_API_TOKEN environment variable is required")
       print("Error: REPLICATE_API_TOKEN environment variable is required", file=sys.stderr)
       sys.exit(1)
   ```
   - **Why preserve**: Fail-fast, clear error messages, logs and stderr
   - **Don't change**: Meets spec perfectly

3. **Path resolution logic** (server.py:124-127):
   ```python
   if not os.path.isabs(output_file_name):
       output_file_name = os.path.join(INVOKE_DIR, output_file_name)
   output_file_name = os.path.abspath(output_file_name)
   ```
   - **Why preserve**: Correct handling of relative/absolute paths
   - **Augment**: Add collision detection after this block

### Reusable Utilities

**No existing utilities to reuse** - this is a single-file implementation

**New utility to add**:
```python
def find_available_filename(file_path: str) -> str:
    """Find next available filename by incrementing counter if file exists.

    Examples:
        cat.png -> cat_1.png -> cat_2.png
        image -> image_1 -> image_2
    """
    if not os.path.exists(file_path):
        return file_path

    base, ext = os.path.splitext(file_path)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    return f"{base}_{counter}{ext}"
```

**Location**: Add to server.py before `generate_image()` function (around line 100)

### Anti-patterns to Avoid

**From codebase review**:

1. **Don't add caching** - Spec explicitly forbids it
2. **Don't add retry logic** - Spec explicitly forbids it
3. **Don't validate model parameters client-side** - Let Replicate API handle it
4. **Don't create new files** - Keep single-file architecture
5. **Don't add dependencies** - Use stdlib only

**Code smells NOT present** (code is clean):
- No global mutable state
- No blocking I/O (all async)
- No hardcoded paths (uses env vars correctly)
- No bare excepts (specific exception handling)
- No missing docstrings (functions documented)

### Implementation File Map

**Files requiring changes**:

1. **src/wyrd_gen_mcp/server.py** (4 changes):
   - Lines 20-28: Replace FileHandler with RotatingFileHandler
   - Line ~100: Add `find_available_filename()` function
   - Lines 152, 173: Call collision detector before file writes
   - Lines 214-235: Add cost, quality, cost_efficiency fields to each model in `list_image_models()`:
     ```python
     {
         "model": "black-forest-labs/flux-schnell",
         "description": "...",
         "best_for": "...",
         "cost": 0.04,           # NEW
         "quality": 9,           # NEW
         "cost_efficiency": 225.0  # NEW
     }
     ```

2. **scripts/wyrd-gen-remote.sh** (1 change):
   - Lines 9-10: Fix environment loading and export

**Files NOT requiring changes**:
- `pyproject.toml` (no new dependencies)
- `scripts/wyrd-gen.sh` (already correct)
- `src/wyrd_gen_mcp/__init__.py` (empty module file)
- All documentation (CLAUDE.md already accurate)

### Gap Analysis Summary

**Spec Requirements vs Implementation**:

| Requirement | Spec Section | Current State | Gap |
|-------------|--------------|---------------|-----|
| Log rotation | FR-9, NFR-4 | Basic FileHandler | Need RotatingFileHandler |
| File collision detection | FR-4, NFR-5, AT-11 | Direct write | Need incrementing logic |
| Remote script env vars | FR-8, AT-14 | Missing exports | Need set -a pattern |
| Cost & quality metrics | FR-2, AT-3 (v1.2.0) | Missing fields | Add cost, quality, cost_efficiency |
| Three MCP tools | FR-5 | ✅ Implemented | None |
| Replicate integration | FR-1 | ✅ Implemented | None |
| Model listing (base) | FR-2, FR-3 | ✅ Implemented | None |
| Error handling | NFR-4 | ✅ Implemented | None |
| Path resolution | FR-4 | ✅ Implemented | None |
| API token validation | FR-7 | ✅ Implemented | None |
| Async I/O | NFR-3 | ✅ Implemented | None |

**Completion Status**: ~85% implemented, ~15% remaining (4 gaps identified above)
