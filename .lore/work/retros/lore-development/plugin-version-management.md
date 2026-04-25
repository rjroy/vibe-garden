---
title: Always update plugin version after changes
date: 2026-01-31
status: complete
tags: [plugin-development, versioning, release-management, process]
modules: [lore-development]
---

# Retro: Plugin Version Management

## Summary

After merging commit 78e3d2e (task tracking for tend skill), the plugin version in `lore-development/.claude-plugin/plugin.json` was not incremented. This meant the changes would not be picked up by Claude Code's plugin cache, which uses version as the cache key.

## What Went Well

- The issue was caught before significant time was lost
- The fix was trivial once identified (single line version bump)

## What Could Improve

- Version increment should be part of the commit itself, not a follow-up
- No automated check exists to flag when plugin files change without a version bump
- Easy to forget during the flow of implementation work

## Lessons Learned

**Plugin versions are cache keys, not just documentation.** Claude Code caches plugins by version. If the version doesn't change, the old cached version continues to be used regardless of file changes. This is different from development workflows where file changes take effect immediately.

**Version bumps belong in the same commit as the change.** Treating version increment as a separate step creates a gap where the change exists but isn't visible. The version bump should be the last edit before committing, not an afterthought.

**Consider a pre-commit hook.** A hook could check if any file under `.claude-plugin/` or plugin command files changed, and verify that `plugin.json` version was also modified. This would catch the issue at commit time rather than after merge.

## Artifacts

- Affected plugin: `lore-development/.claude-plugin/plugin.json`
- Triggering commit: 78e3d2e (fix: Add task tracking to tend skill)
- Fix: Version increment from 0.11.0 to 0.11.1
