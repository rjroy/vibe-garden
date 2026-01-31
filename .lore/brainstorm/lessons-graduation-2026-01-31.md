---
title: Lessons Graduation System
date: 2026-01-31
status: open
tags: [methodology, retro, knowledge-management, lessons-learned, graduation]
modules: [lore-development]
related: [.lore/retros/plugin-version-management.md]
---

# Brainstorm: Lessons Graduation System

## Context

We've built a learning system with lore-development: context is added, retros are defined, context is loaded. But the lore-researcher is lossy without regrets. It only surfaces lessons when search keywords match. Universal lessons don't trigger because new projects have no `.lore/` yet, or search terms don't overlap.

The triggering example: the plugin-version-management retro contains a universal lesson ("version is a cache key") that anyone working on Claude Code plugins should know. But it's buried in a project-local retro, invisible to future work.

## Ideas Explored

### Hierarchy of Lessons

Lessons exist at different scopes:

1. **Project-local** - "We used X pattern in this codebase" (stays in `.lore/retros/`)
2. **Critical** - "This matters for this project" (promoted to project CLAUDE.md)
3. **Universal** - "This applies everywhere" (promoted to user-scope rules)

### Manual Graduation via AskUserQuestion

After `/retro` writes the retro document, present each lesson for classification:

```
How significant is this lesson?

○ Invalid - not actually a lesson, remove it
○ Valid - project-local, stays in retro (Recommended)
○ Critical - important for this project, add to CLAUDE.md
○ Universal - applies everywhere, add to user rules
```

Automated graduation rejected for now: LLMs aren't reliable enough to classify lesson significance. Human judgment required.

### Where Graduated Lessons Live

| Classification | Location | Loaded When |
|---------------|----------|-------------|
| Valid | `.lore/retros/[name].md` | Never (searched by lore-researcher) |
| Critical | `./CLAUDE.md` | Every session in this project |
| Universal | `~/.claude/rules/lessons-learned.md` | Every session everywhere |

### File Formats

**Project CLAUDE.md Addition:**
```markdown
## Critical Lessons

Lessons that emerged from work in this project. See `.lore/retros/` for full context.

- **Version is a cache key** (2026-01-31): When changing a Claude Code plugin, always update its version in plugin.json. [Source: .lore/retros/plugin-version-management.md]
```

**User Rules File (`~/.claude/rules/lessons-learned.md`):**
```markdown
# Lessons Learned

Hard-won lessons that apply across all projects. Each was graduated from a project retro.

## Plugin Development

- **Version is a cache key** (2026-01-31): When changing a Claude Code plugin, always update its version in plugin.json. [Source: vibe-garden/always-learn]
```

### Edge Case: Retro-ing a Retro

If `/retro` detects the subject is itself a retro or lore document, skip normal retro flow and run graduation pass directly. This handles the case where someone wants to review old retros for graduation without writing a meta-retro.

### Philosophy vs Lessons

"lore-development is a philosophy" is different from a lesson. It's meta-context that shapes how new skills should be designed, but it's not a rule to follow. This would be marked "critical" for the lore-development project itself, not "universal". The distinction:

- **Lesson**: "Always do X when Y" (actionable rule)
- **Philosophy**: "This system exists because Z" (context for decision-making)

Philosophy belongs in project CLAUDE.md as narrative, not in lessons-learned as bullets.

## Open Questions

1. **Lesson format**: Include date and source for traceability? Or is that noise?

2. **Categories in universal**: Should graduation ask for a category (e.g., "Plugin Development"), infer from tags, or dump everything flat?

3. **Updating vs duplicating**: If a lesson gets refined later, update existing entry or add new one? (Probably update, with claude-md-management handling hygiene.)

4. **The "critical" middle ground**: Is it actually useful, or just "I'm not sure it's universal"? Current take: critical = confident it matters for this project; valid = let lore-researcher decide later.

5. **Decay and pruning**: Handled by claude-md-management plugin for CLAUDE.md files. Universal lessons file would need similar hygiene eventually.

## Next Steps

1. Spec the changes to `/retro` skill
2. Define the lessons-learned.md format for user scope
3. Implement graduation flow with AskUserQuestion
4. Test with existing retros (like plugin-version-management)
