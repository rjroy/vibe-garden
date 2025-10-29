#!/bin/bash

# Claude Code Status Line Script
# Receives JSON input from Claude Code via stdin
# Outputs: Model | Project Directory | Git Branch (status) | +added -removed

# Read JSON from stdin
input=$(cat)

# Parse JSON using jq
model=$(echo "$input" | jq -r '.model.display_name // .model.id // "unknown"')
project_dir=$(basename "$(echo "$input" | jq -r '.workspace.project_dir // .cwd // "unknown"')")

# Get git branch and status
if git rev-parse --git-dir > /dev/null 2>&1; then
    branch=$(git branch --show-current 2>/dev/null || echo "detached")

    # Check for uncommitted changes
    if [[ -n $(git status --porcelain 2>/dev/null) ]]; then
        branch_status="*"
    else
        branch_status=""
    fi

    git_info="$branch$branch_status"
else
    git_info="no-git"
fi

# Get session file changes from Claude Code session data
lines_added=$(echo "$input" | jq -r '.cost.total_lines_added // 0')
lines_removed=$(echo "$input" | jq -r '.cost.total_lines_removed // 0')
diff_stats="+$lines_added -$lines_removed"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Output the status line with colors
echo -e "${GREEN}$model${NC} | ${BLUE}$project_dir${NC} | ${PURPLE}$git_info${NC} | ${YELLOW}$diff_stats${NC}"
