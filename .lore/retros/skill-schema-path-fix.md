---
title: Use CLAUDE_PLUGIN_ROOT for schema paths in skills
date: 2026-02-02
status: complete
tags: [bug-fix, plugin, paths, skills]
modules: [lore-development]
---

# Retro: Skill Schema Path Fix

## Summary

Fixed 8 references across 7 lore-development skills that used relative paths (`../../shared/frontmatter-schema.md`) to load the frontmatter schema. Changed to `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` which resolves correctly regardless of working directory.

## What Went Well

- Problem was immediately clear once examined
- Fix was mechanical and low-risk
- Verification via grep confirmed all instances updated

## What Could Improve

- Should have caught this when the shared schema was introduced
- No automated check for relative paths in skills that should use plugin-root-relative paths

## Lessons Learned

- Skills execute from the user's working directory, not the skill file's directory. Relative paths in skills resolve against cwd, not the skill location.
- `${CLAUDE_PLUGIN_ROOT}` is the correct way to reference plugin assets from skills.

## Artifacts

Skills updated:
- `skills/brainstorm/SKILL.md`
- `skills/ddp/SKILL.md`
- `skills/excavate/SKILL.md`
- `skills/research/SKILL.md`
- `skills/retro/SKILL.md`
- `skills/specify/SKILL.md`
- `skills/tend/SKILL.md` (2 references)
