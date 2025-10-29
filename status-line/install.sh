#!/bin/bash

# Claude Code Status Line Installer
# Installs general-status.sh as a Claude Code status line script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_SCRIPT="$SCRIPT_DIR/general-status.sh"
CLAUDE_CONFIG_DIR="$HOME/.claude"
CLAUDE_SETTINGS="$CLAUDE_CONFIG_DIR/settings.json"
INSTALL_DIR="$CLAUDE_CONFIG_DIR/status-line"
TARGET_SCRIPT="$INSTALL_DIR/general-status.sh"

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Claude Code Status Line Installer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

# Check if source script exists
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo -e "${RED}✗ Error: Source script not found at $SOURCE_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found source script: $SOURCE_SCRIPT"

# Check for required dependencies
echo ""
echo "Checking dependencies..."

if ! command -v jq &> /dev/null; then
    echo -e "${RED}✗ Error: jq is not installed${NC}"
    echo -e "  Install with: ${YELLOW}sudo apt install jq${NC} (Debian/Ubuntu)"
    echo -e "             or ${YELLOW}brew install jq${NC} (macOS)"
    exit 1
fi
echo -e "${GREEN}✓${NC} jq is installed"

if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} Warning: git is not installed (git status features will not work)"
else
    echo -e "${GREEN}✓${NC} git is installed"
fi

# Create Claude config directory if it doesn't exist
echo ""
echo "Setting up installation directory..."

if [ ! -d "$CLAUDE_CONFIG_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Creating Claude config directory: $CLAUDE_CONFIG_DIR"
    mkdir -p "$CLAUDE_CONFIG_DIR"
fi

if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} Creating status-line directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

echo -e "${GREEN}✓${NC} Installation directory ready: $INSTALL_DIR"

# Create symbolic link
echo ""
echo "Installing script..."

ln -sf "$SOURCE_SCRIPT" "$TARGET_SCRIPT"

echo -e "${GREEN}✓${NC} Created symbolic link: $TARGET_SCRIPT -> $SOURCE_SCRIPT"
echo -e "${GREEN}✓${NC} Updates to the source script will automatically be reflected"

# Configure settings.json
echo ""
echo "Configuring Claude Code settings..."

if [ ! -f "$CLAUDE_SETTINGS" ]; then
    echo -e "${YELLOW}⚠${NC} Creating new settings.json"
    jq -n --arg cmd "$TARGET_SCRIPT" '{
  statusLine: {
    type: "command",
    command: $cmd,
    padding: 0
  }
}' > "$CLAUDE_SETTINGS"
    echo -e "${GREEN}✓${NC} Created settings.json with status line configuration"
else
    # Check if jq can parse the settings file
    if ! jq empty "$CLAUDE_SETTINGS" 2>/dev/null; then
        echo -e "${RED}✗ Error: Existing settings.json is not valid JSON${NC}"
        echo -e "  Please fix the file manually at: $CLAUDE_SETTINGS"
        exit 1
    fi

    # Update settings.json with jq
    tmp_file=$(mktemp)
    jq --arg cmd "$TARGET_SCRIPT" '.statusLine = {type: "command", command: $cmd, padding: 0}' "$CLAUDE_SETTINGS" > "$tmp_file"
    mv "$tmp_file" "$CLAUDE_SETTINGS"
    echo -e "${GREEN}✓${NC} Updated existing settings.json"
fi

# Test the script
echo ""
echo "Testing installation..."

# Create test JSON input
test_json='{
  "hook_event_name": "Status",
  "session_id": "test-session",
  "model": {
    "id": "claude-sonnet-4-5-20250929",
    "display_name": "Sonnet 4.5"
  },
  "workspace": {
    "project_dir": "'$SCRIPT_DIR'"
  },
  "cost": {
    "total_lines_added": 42,
    "total_lines_removed": 13
  }
}'

# Run the script with test input
output=$(echo "$test_json" | "$TARGET_SCRIPT")

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Script test successful!"
    echo -e "  Output: ${BLUE}$output${NC}"
else
    echo -e "${RED}✗ Error: Script test failed${NC}"
    exit 1
fi

# Display summary
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "Configuration:"
echo "  Script location: $TARGET_SCRIPT"
echo "  Settings file:   $CLAUDE_SETTINGS"
echo ""
echo "Status line format:"
echo "  Model | Project | Branch(status) | +added -removed"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code to see the status line"
echo "  2. The status line will appear at the bottom of your terminal"
echo "  3. To customize, edit: $SOURCE_SCRIPT (changes apply immediately)"
echo ""
echo -e "${BLUE}Tip:${NC} To uninstall, run: rm $TARGET_SCRIPT && jq 'del(.statusLine)' $CLAUDE_SETTINGS"
echo ""
