#!/usr/bin/env bash
# Author detection script for Spiral Grove
# Priority: Git → Perforce → ENV → Unknown
# Output format: "Name <email>" or "Name" or "Unknown Author"

set -euo pipefail

# Try Git
if GIT_NAME=$(git config user.name 2>/dev/null) && GIT_EMAIL=$(git config user.email 2>/dev/null); then
  if [[ -n "$GIT_NAME" && -n "$GIT_EMAIL" ]]; then
    echo "$GIT_NAME <$GIT_EMAIL>"
    exit 0
  elif [[ -n "$GIT_NAME" ]]; then
    echo "$GIT_NAME"
    exit 0
  fi
fi

# Try Perforce
if command -v p4 >/dev/null 2>&1; then
  if P4_USER=$(p4 user -o 2>/dev/null | grep "^User:" | awk '{print $2}') && [[ -n "$P4_USER" ]]; then
    P4_EMAIL=$(p4 user -o 2>/dev/null | grep "^Email:" | awk '{print $2}') || true
    if [[ -n "$P4_EMAIL" ]]; then
      # Try to get full name from FullName field
      P4_FULLNAME=$(p4 user -o 2>/dev/null | grep "^FullName:" | sed 's/^FullName:\s*//' | tr -d '\r') || true
      if [[ -n "$P4_FULLNAME" ]]; then
        echo "$P4_FULLNAME <$P4_EMAIL>"
      else
        echo "$P4_USER <$P4_EMAIL>"
      fi
      exit 0
    else
      # No email, use P4 user or full name
      P4_FULLNAME=$(p4 user -o 2>/dev/null | grep "^FullName:" | sed 's/^FullName:\s*//' | tr -d '\r') || true
      if [[ -n "$P4_FULLNAME" ]]; then
        echo "$P4_FULLNAME"
      else
        echo "$P4_USER"
      fi
      exit 0
    fi
  fi
fi

# Try environment variable
ENV_USER="${USER:-${USERNAME:-}}"
if [[ -n "$ENV_USER" ]]; then
  echo "$ENV_USER"
  exit 0
fi

# Fallback
echo "Unknown Author"
exit 0
