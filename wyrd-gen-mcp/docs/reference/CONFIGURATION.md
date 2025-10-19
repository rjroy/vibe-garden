# Configuration Guide

## Environment Variables

### REPLICATE_API_TOKEN (Required)

Your Replicate API authentication token.

**How to get it:**
1. Sign up at [replicate.com](https://replicate.com)
2. Navigate to [Account API Tokens](https://replicate.com/account/api-tokens)
3. Create a new token or copy existing one

**Setting the variable:**

```bash
# Linux/macOS
export REPLICATE_API_TOKEN="r8_your_token_here"

# Windows (PowerShell)
$env:REPLICATE_API_TOKEN="r8_your_token_here"

# Or create a .env file
echo "REPLICATE_API_TOKEN=r8_your_token_here" > .env
```

## Claude Desktop Configuration

To use this MCP server with Claude Desktop, add it to your configuration file:

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%\Claude\claude_desktop_config.json`

### Linux
Location: `~/.config/Claude/claude_desktop_config.json`

### Configuration Format

```json
{
  "mcpServers": {
    "wyrd-gen": {
      "command": "python",
      "args": ["-m", "wyrd_gen_mcp.server"],
      "env": {
        "REPLICATE_API_TOKEN": "r8_your_token_here"
      }
    }
  }
}
```

**Important:**
- Ensure Python 3.10+ is installed and accessible
- Replace `r8_your_token_here` with your actual Replicate API token
- Restart Claude Desktop after configuration changes

## Installation Methods

### Method 1: Direct Python Module (Recommended)

Install the package in a virtual environment and use the configuration above:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

### Method 2: Using Installed Script

If you want to use the installed script command:

```bash
# Install the package
pip install -e .

# Then in Claude Desktop config, use:
{
  "command": "wyrd-gen-mcp",
  "args": [],
  "env": {
    "REPLICATE_API_TOKEN": "r8_your_token_here"
  }
}
```

## Troubleshooting

### Server not starting
- Verify `REPLICATE_API_TOKEN` is set correctly
- Ensure Python 3.10+ is installed
- Check that `pip install -e .` completed successfully
- Verify virtual environment is activated if using one

### API errors
- Verify token is valid at replicate.com
- Check you have sufficient credits
- Review Replicate API status

### Connection issues
- Restart Claude Desktop
- Check MCP server logs (stderr output)
- Verify JSON configuration is valid
