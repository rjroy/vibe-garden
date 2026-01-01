#!/usr/bin/env bash
# Shell wrapper for gh_project.py
# Provides better permission granularity than calling python3 directly
#
# Usage:
#   gh_project.sh list-issues
#   gh_project.sh get-issue <number>
#   gh_project.sh set-status <number> "<status>"
#   gh_project.sh add-to-project <number>

set -euo pipefail

# Get the directory where this script lives
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run the Python script with all arguments passed through
exec python3 "${SCRIPT_DIR}/gh_project.py" "$@"
