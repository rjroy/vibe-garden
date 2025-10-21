# Wyrd-Gen MCP

<img src="wyrd-gen-logo.png" align="right" width="128" height="128" alt="Vibe Garden Logo">

**AI-powered image generation for Claude Code via Replicate API**


Wyrd-Gen MCP enables Claude Code users to generate stunning AI images through natural language prompts. Simply describe what you want, and Claude will create it using state-of-the-art image generation models.

[![Version](https://img.shields.io/badge/version-0.1.1-blue.svg)](https://github.com/rjroy/vibe-garden/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/protocol-MCP-purple.svg)](https://modelcontextprotocol.io/)

---

## Features

- 🎨 **Text-to-Image Generation** - Describe your vision in natural language
- 🚀 **Multiple AI Models** - Flux, Stable Diffusion, SDXL, Imagen, and more
- ⚡ **Fast Performance** - Sub-500ms server overhead on top of API response time
- 📁 **Smart File Management** - Auto-incrementing filenames prevent overwriting
- 🔒 **Secure** - OAuth via Replicate API tokens, never stores sensitive data
- 🎯 **Claude Code Plugin** - Install via `/plugin install wyrd-gen-mcp@vibe-garden`
- 🔄 **Log Rotation** - 10MB max per file, 5 backup files maintained
- 🛠️ **Model Discovery** - Query available parameters for any model

---

## Quick Start (5 Minutes)

### 1. Install Plugin

```bash
# In Claude Code, run:
/plugin install wyrd-gen-mcp@vibe-garden
```

### 2. Set Up Replicate API

1. Sign up at [Replicate](https://replicate.com)
2. Get your API token from [replicate.com/account/api-tokens](https://replicate.com/account/api-tokens)
3. Create a `.env` file in the plugin directory:
   ```bash
   REPLICATE_API_TOKEN=r8_your_token_here
   ```

### 3. Use in Claude Code

```
You: Generate an image of a serene mountain landscape at sunset

Claude: [Uses wyrd-gen-mcp generate_image tool]
✓ Image saved to: ./mountain-sunset.png
```

---

## Use Cases

### Creative Prototyping

```
You: Generate 3 variations of a logo concept: minimalist tech startup with circuits

Claude: [Generates 3 images with different interpretations]
```

### Content Creation

```
You: Create a hero image for a blog post about renewable energy - solar panels in a field

Claude: [Generates high-resolution image optimized for web]
```

### Visual Brainstorming

```
You: Show me what a futuristic office space might look like in 2050

Claude: [Generates conceptual visualization]
```

### Rapid Iteration

```
You: Generate a cyberpunk cityscape, then make it more neon, then add rain

Claude: [Iterates through 3 versions based on feedback]
```

---

## Tools Available

### `generate_image`

Generate AI images from text prompts with configurable parameters.

**Parameters**:
- `prompt` (required): Text description of the image
- `output_file_name` (required): Filename to save (e.g., "my-image.png")
- `model` (optional): Model ID (default: "black-forest-labs/flux-kontext-pro")
- `parameters` (optional): Model-specific settings (aspect_ratio, quality, etc.)

**Example Response**:
```json
{
  "success": true,
  "model": "black-forest-labs/flux-kontext-pro",
  "prompt": "serene mountain landscape at sunset",
  "saved_files": [
    "/home/user/projects/mountain-sunset.png"
  ],
  "parameters": {
    "aspect_ratio": "16:9",
    "output_format": "png"
  }
}
```

### `list_image_models`

List available image generation models with descriptions and recommendations.

**Example Response**:
```json
[
  {
    "model": "black-forest-labs/flux-kontext-pro",
    "description": "High-quality, context-aware image generation",
    "best_for": "Professional images with attention to detail"
  },
  {
    "model": "google/imagen-4",
    "description": "Google's latest text-to-image model",
    "best_for": "Photorealistic images and precise compositions"
  },
  ...
]
```

### `get_model_parameters`

Query available parameters for a specific model.

**Parameters**:
- `model` (required): Model ID (e.g., "google/imagen-4")

**Example Response**:
```json
{
  "model": "google/imagen-4",
  "parameters": {
    "prompt": {
      "type": "string",
      "required": true,
      "description": "Text description of the image to generate"
    },
    "aspect_ratio": {
      "type": "string",
      "default": "1:1",
      "options": ["1:1", "16:9", "9:16", "4:3", "3:4"],
      "description": "Image aspect ratio"
    },
    ...
  }
}
```

---

## Popular Models

| Model | Speed | Quality | Best For | Cost Efficiency* |
|-------|-------|---------|----------|------------------|
| **flux-kontext-pro** | Fast | Excellent | Professional work, context-aware | ⭐⭐⭐⭐ |
| **flux-1.1-pro** | Fast | Excellent | High-quality production | ⭐⭐⭐⭐ |
| **imagen-4** | Moderate | Superior | Photorealism, composition | ⭐⭐⭐ |
| **ideogram-v3-turbo** | Very Fast | Good | Rapid prototyping | ⭐⭐⭐⭐⭐ |

*Cost efficiency based on quality-to-price ratio. See spec for current pricing.

---

## Configuration

The plugin uses environment variables for configuration:

```bash
# Required
REPLICATE_API_TOKEN=r8_your_token_here

# Optional (set via launch scripts)
WYRD_INVOKE_DIR=/path/to/working/directory  # Auto-set by launch scripts
```

### Launch Scripts

Two launch scripts are provided for different environments:

**`wyrd-gen.sh`** (1Password CLI):
- Uses `op run` to securely load environment variables
- Recommended for local development
- Requires 1Password CLI installed

**`wyrd-gen-remote.sh`** (Direct .env):
- Sources `.env` file directly
- Use for remote/server environments without 1Password

Both scripts automatically:
- Capture invoke directory (`pwd`)
- Activate Python virtual environment
- Set `WYRD_INVOKE_DIR` for path resolution

---

## File Management

### Auto-Incrementing Filenames

Wyrd-Gen **never overwrites existing files**. If a file already exists, it automatically increments:

```
mountain.png        # First generation
mountain_1.png      # Second generation
mountain_2.png      # Third generation
```

### Path Resolution

- **Relative paths**: Resolved from `WYRD_INVOKE_DIR` (where you launched Claude)
- **Absolute paths**: Used as-is
- **Parent directories**: Created automatically if they don't exist

**Example**:
```
# You launch Claude from: /home/user/projects/
# Request: output_file_name="images/sunset.png"
# Saved to: /home/user/projects/images/sunset.png
```

---

## Logging

Logs are written to `wyrd-gen-mcp.log` in the current working directory.

**Log Rotation**:
- Max file size: 10MB
- Backup files kept: 5
- Handler: Python `RotatingFileHandler`

**Log Contents**:
- Tool invocations with arguments
- Replicate API calls and responses
- File save operations with paths
- Error traces with full exception details

---

## Documentation

- **[Tool Reference](docs/reference/TOOLS.md)** - Detailed tool usage and examples
- **[MCP Overview](docs/reference/MCP_OVERVIEW.md)** - Understanding the protocol
- **[Replicate API](docs/reference/REPLICATE_API.md)** - Model details and pricing
- **[Configuration](docs/reference/CONFIGURATION.md)** - Setup and environment variables
- **[Server Implementation](server/README.md)** - Technical implementation details

---

## Requirements

- **Python**: 3.10 or higher
- **Claude Code**: Latest version
- **Replicate Account**: Free tier available
- **API Token**: From replicate.com/account/api-tokens

---

## Installation (for Developers)

```bash
# Clone repository
git clone https://github.com/rjroy/vibe-garden.git
cd vibe-garden/wyrd-gen-mcp

# Create virtual environment
python -m venv server/venv

# Activate virtual environment
source server/venv/bin/activate  # Linux/macOS
# or
server\venv\Scripts\activate     # Windows

# Install dependencies
cd servers
pip install -e .

# Create .env file
echo "REPLICATE_API_TOKEN=r8_your_token_here" > .env

# Test the server
python -m wyrd_gen_mcp.server
```

---

## Project Status

**Version**: 0.1.1
**Status**: Functional (SDD tracking pending)

**Completed**:
- ✅ Core image generation functionality
- ✅ Multi-model support (4+ models)
- ✅ Model parameter discovery
- ✅ File collision prevention
- ✅ Log rotation (10MB, 5 backups)
- ✅ Dual launch scripts (1Password + direct .env)
- ✅ MCP protocol compliance

**Pending** (tracked in `.sdd/specs/wyrd-gen-mcp-server.md`):
- Task breakdown from existing spec/plan
- Formal SDD progress tracking
- Comprehensive test suite
- Cost & quality metrics for models

---

## Performance

**Startup Time**: < 2 seconds
**Server Overhead**: < 500ms on top of Replicate API response
**File I/O**: < 1 second for images up to 10MB
**Async Execution**: Server remains responsive during generation

---

## Security

- API tokens loaded from environment only
- Tokens never logged or exposed in error messages
- File writes restricted to invoke directory scope
- Path traversal protection via absolute path validation
- No persistent storage of sensitive data

---

## Troubleshooting

### Server Won't Start
- Verify `REPLICATE_API_TOKEN` is set in `.env`
- Ensure virtual environment is activated
- Check `pip install -e .` completed successfully

### Image Generation Fails
- Confirm API token is valid at replicate.com/account
- Check you have sufficient credits
- Review model name for typos (use `list_image_models` tool)

### Files Not Saving
- Check `WYRD_INVOKE_DIR` is set correctly
- Verify write permissions in target directory
- Review `wyrd-gen-mcp.log` for detailed errors

### Claude Code Doesn't Show Tools
- Restart Claude Code after plugin installation
- Verify `.claude-plugin/plugin.json` configuration
- Check MCP server started successfully in logs

---

## Contributing

Contributions welcome! This project uses [Spec-Driven Development (SDD)](../.sdd/README.md).

**To contribute**:
1. Review the spec at `.sdd/specs/wyrd-gen-mcp-server.md`
2. Check the technical plan at `.sdd/plans/wyrd-gen-mcp-server-plan.md`
3. Follow the SDD workflow: Specification → Planning → Tasks → Implementation
4. Submit pull requests with clear rationale

---

## License

MIT License - see [LICENSE](../LICENSE) file for details.

---

## Resources

- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Replicate Documentation](https://replicate.com/docs)
- [Replicate Model Explorer](https://replicate.com/explore)
- [Claude Code](https://claude.ai/code)
- [Vibe Garden Repository](https://github.com/rjroy/vibe-garden)

---

## Contact

**Author**: Ronald Roy
**Email**: gsdwig@gmail.com
**Repository**: [github.com/rjroy/vibe-garden](https://github.com/rjroy/vibe-garden)

---

<div align="center">

**Generate anything you can imagine 🎨**

*Part of the [Vibe Garden](https://github.com/rjroy/vibe-garden) ecosystem*

</div>
