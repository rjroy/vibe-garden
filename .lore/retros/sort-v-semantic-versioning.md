---
title: sort -V for semantic version directory selection
date: 2026-02-01
status: complete
tags: [shell, versioning, plugins, coreutils]
---

# Retro: sort -V for Semantic Version Sorting

## Summary

Updated the mind-reader plugin's baseline update script to dynamically find the latest plugin version instead of hardcoding `1.1.0`. Used `sort -V` to correctly order semantic version directories.

## Context

The original script hardcoded the plugin path:
```bash
PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/cache/vibe-garden/mind-reader/1.1.0}"
```

This breaks whenever the plugin updates (1.1.0 → 1.2.0, etc.), requiring manual script edits.

## Solution

```bash
LATEST_VERSION=$(ls "$PLUGIN_CACHE" | sort -V | tail -1)
```

The `-V` flag (version sort) handles semantic versioning correctly:
- `1.9.0` comes before `1.10.0` (not lexicographically after)
- `1.0.0` < `1.0.1` < `1.1.0` < `2.0.0`

Without `-V`, lexicographic sort produces wrong results:
```
1.0.0
1.0.1
1.1.0
1.10.0   # Wrong! Would sort before 1.2.0 lexicographically
1.2.0
```

## What Went Well

- Quick fix with no external dependencies (coreutils `sort -V` is standard on GNU systems)
- Script now survives plugin upgrades automatically
- Pattern is reusable anywhere version directories need selection

## What Could Improve

- Could have caught this during initial setup (hardcoded paths are a smell)
- Plugin system could provide a stable "current version" symlink

## Lessons Learned

- `sort -V` exists in GNU coreutils for exactly this use case. Don't roll custom version comparison logic in shell scripts.
- Hardcoded version paths in scripts are a maintenance landmine. When the version appears in a path, ask: "What happens when this changes?"

## Artifacts

- Script: `~/.claude/mind-reader/update-baseline.sh`
- Plugin: `~/.claude/plugins/cache/vibe-garden/mind-reader/`
