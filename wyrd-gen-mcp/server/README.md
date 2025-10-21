# Wyrd-Gen MCP Server

An MCP (Model Context Protocol) server that enables AI image generation through Replicate's API. Integrates with Claude Desktop to provide seamless image generation capabilities.

## Features

- Generate images using state-of-the-art AI models (Flux, SDXL, Stable Diffusion)
- Simple text-to-image generation via natural language prompts
- Support for multiple popular image generation models
- Configurable image dimensions and batch generation
- Full MCP protocol compliance for Claude Desktop integration

## Quick Start

### Prerequisites

- Python 3.10 or higher
- pip
- A Replicate API token ([get one here](https://replicate.com/account/api-tokens))

### Installation

```bash
# Clone or navigate to the project
cd wyrd-gen

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

### Usage with Claude Desktop

1. Install the package (see above)

2. Create a `.env` file in the project root with your Replicate API token:
   ```
   REPLICATE_API_TOKEN=r8_your_token_here
   ```

3. Add to your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
**Linux:** `~/.config/Claude/claude_desktop_config.json`

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

**Note:** The `wyrd-gen.sh` script automatically handles:
- Capturing the directory where you invoke Claude from (for saving images)
- Loading environment variables from `.env` via 1Password CLI (`op`)
- Activating the Python virtual environment
- Running the MCP server

4. Restart Claude Desktop or reload Claude Code

5. Start generating images:
   - "Generate an image of a cat wearing a space suit"
   - "Create a cyberpunk cityscape with neon lights"
   - "Show me a serene mountain landscape at sunset"

## Available Tools

### generate_image

Generate images using AI models.

**Parameters:**
- `prompt` (required): Description of the image to generate
- `model` (optional): Model ID (default: "black-forest-labs/flux-schnell")
- `width` (optional): Image width in pixels (default: 1024)
- `height` (optional): Image height in pixels (default: 1024)
- `num_outputs` (optional): Number of images to generate (default: 1)

### list_image_models

List available image generation models with descriptions.

## Supported Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| black-forest-labs/flux-schnell | Very Fast | Good | Quick iterations |
| black-forest-labs/flux-dev | Moderate | Excellent | Production images |
| stability-ai/sdxl | Moderate | Very Good | General purpose |
| stability-ai/stable-diffusion | Fast | Good | Classic workflows |

## Documentation

Comprehensive documentation is available in the `docs/reference/` directory:

- **[MCP_OVERVIEW.md](docs/reference/MCP_OVERVIEW.md)** - Understanding the Model Context Protocol
- **[REPLICATE_API.md](docs/reference/REPLICATE_API.md)** - Replicate API reference and model details
- **[TOOLS.md](docs/reference/TOOLS.md)** - Detailed tool documentation and examples
- **[CONFIGURATION.md](docs/reference/CONFIGURATION.md)** - Setup and configuration guide

## Development

```bash
# Create and activate virtual environment (if not already done)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install in editable mode
pip install -e .

# Run the server directly
python -m wyrd_gen_mcp.server

# Or use the installed script
wyrd-gen-mcp
```

## Project Structure

```
wyrd-gen/
├── src/
│   └── wyrd_gen_mcp/
│       ├── __init__.py
│       └── server.py     # Main MCP server implementation
├── docs/
│   └── reference/        # Documentation
│       ├── MCP_OVERVIEW.md
│       ├── REPLICATE_API.md
│       ├── TOOLS.md
│       └── CONFIGURATION.md
├── venv/                 # Virtual environment (not in git)
├── pyproject.toml
└── README.md
```

## Troubleshooting

### Server won't start
- Verify `REPLICATE_API_TOKEN` is set in the environment
- Ensure Python virtual environment is activated
- Check that `pip install -e .` completed successfully

### Image generation fails
- Confirm your Replicate API token is valid
- Check you have sufficient credits at replicate.com
- Review the model name for typos

### Claude Desktop doesn't show the tools
- Restart Claude Desktop after config changes
- Verify JSON syntax in config file
- Check Claude Desktop logs for errors

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Resources

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Replicate Documentation](https://replicate.com/docs)
- [Claude Desktop](https://claude.ai/desktop)
