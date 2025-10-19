# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wyrd-Gen is an MCP (Model Context Protocol) server that provides AI image generation capabilities via Replicate's API. It integrates with Claude Desktop to enable LLMs to generate images through natural language prompts.

## Development Commands

```bash
# Create virtual environment (first time setup)
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Run the server (requires REPLICATE_API_TOKEN env var)
python -m wyrd_gen_mcp.server

# Or use the installed script
wyrd-gen-mcp
```

## Architecture

### MCP Server Pattern (src/wyrd_gen_mcp/server.py)

This is a stdio-based MCP server following the standard Python MCP pattern:

1. **Server Initialization** (server.py:144): Creates MCP Server instance with name
2. **Tool Registration** (server.py:26-68): Defines tools with JSON schemas via `TOOLS` list
3. **Request Handlers**:
   - `@server.list_tools()` (server.py:147-149): Returns available tools
   - `@server.call_tool()` (server.py:152-164): Executes tool requests
4. **Transport Layer** (server.py:167-168): Uses stdio_server() for client-server communication

### Tool Implementation

**generate_image** (server.py:71-103):
- Calls `replicate_client.run()` with model ID and parameters
- Returns JSON response with image URLs and metadata
- Default model: `black-forest-labs/flux-schnell`

**list_image_models** (server.py:106-133):
- Returns hardcoded list of popular models with descriptions
- No external API calls

### Key Integration Points

- **Environment**: Requires `REPLICATE_API_TOKEN` (validated at server.py:16-19)
- **External API**: Replicate client initialized at server.py:22
- **Model Format**: Replicate models use `owner/model-name` format as strings

## Python Environment

- **Python Version**: Requires Python 3.10+
- **Virtual Environment**: Always use `python -m venv venv` to create isolated environment
- **Dependencies**: Managed via pyproject.toml
- **Package Structure**: src-layout with wyrd_gen_mcp package
- **Installation**: Use `pip install -e .` for editable/development installs

## Testing the Server

Since this is an MCP server meant to run via Claude Desktop or Claude Code:

1. Create and activate venv: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -e .`
3. Set `REPLICATE_API_TOKEN` environment variable (or use `op` with `.env` file)
4. Configure in Claude Desktop's `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "wyrd-gen": {
         "command": "/absolute/path/to/wyrd-gen/scripts/wyrd-gen.sh"
       }
     }
   }
   ```

Or for Claude Code, add to `.claude/mcp.json`:
   ```json
   {
     "mcpServers": {
       "wyrd-gen": {
         "command": "/absolute/path/to/wyrd-gen/scripts/wyrd-gen.sh"
       }
     }
   }
   ```

Note: The `wyrd-gen.sh` script handles:
- Capturing the invoke directory for saving files
- Loading environment variables via `op run --env-file=.env`
- Activating the virtual environment
- Running the MCP server

## Adding New Tools

When adding MCP tools:
1. Add tool definition to `TOOLS` list with proper JSON schema
2. Create an async handler function for the tool
3. Add handler case in `call_tool()` decorator function
4. Follow existing error handling pattern (try/except with error JSON response)
5. Return responses as `list[TextContent]` with JSON-formatted text

## Adding Support for New Models

The `list_image_models` tool uses a hardcoded list (server.py:110-127). When adding new models:
1. Update this list with new model entries
2. Test with `replicate_client.run()` to verify model ID format
3. Update docs/reference/REPLICATE_API.md with model details

## Documentation Structure

Reference docs in `docs/reference/` provide context for users:
- `MCP_OVERVIEW.md`: MCP protocol architecture
- `REPLICATE_API.md`: Replicate API and model information
- `TOOLS.md`: Tool usage examples
- `CONFIGURATION.md`: Claude Desktop integration setup
