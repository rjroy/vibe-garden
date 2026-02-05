---
title: Lessons Graduation for /retro
date: 2026-01-31
status: implemented
tags: [methodology, retro, knowledge-management, lessons-learned, graduation, lore-development]
modules: [lore-development]
related: [.lore/brainstorm/lessons-graduation-2026-01-31.md, .lore/retros/plugin-version-management.md]
---

# Spec: Lessons Graduation

## Overview

Extend the `/retro` skill to classify and graduate lessons beyond project-local storage. After writing a retro, each lesson is presented to the user for classification. Lessons marked "critical" are appended to the project's CLAUDE.md. Lessons marked "universal" are appended to a user-scope rules file that loads in every session.

## Entry Points

- `/retro` completion (from normal retro flow)
- `/retro` on an existing retro document (from graduation-only mode)

## Requirements

- REQ-1: After saving a retro, extract lessons from the "Lessons Learned" section
- REQ-2: Present each lesson to the user via AskUserQuestion:
  - Prompt format: `Review lesson: "[lesson text]"`
  - Options: Invalid, Valid (Recommended), Critical, Universal
- REQ-3: Invalid lessons are removed from the retro before final save
- REQ-4: Valid lessons remain in the retro only (current behavior)
- REQ-5: Critical lessons are appended to project CLAUDE.md under "## Critical Lessons"
- REQ-6: Universal lessons are appended to `~/.claude/rules/lessons-learned.md`
- REQ-7: Universal lessons are categorized by inferring from retro tags (see Category Inference)
- REQ-8: Lesson format is minimal (just the lesson text, no date/source metadata)
- REQ-9: If `/retro` is invoked on an existing retro document, skip normal retro flow and run graduation pass directly
- REQ-10: If no lessons exist in the retro, skip graduation (no prompts)
- REQ-11: Create missing directories, files, and sections as needed. New sections append at file bottom.
- REQ-12: Don't append duplicate lessons to target files

## Exit Points

| Exit | Triggers When | Target |
|------|---------------|--------|
| Normal completion | All lessons classified, files updated | Session continues |
| User cancels | User declines to classify | Retro saved without graduation |
| No lessons | Retro has empty Lessons Learned section | Retro saved, no graduation prompts |

## Success Criteria

- [ ] `/retro` prompts for lesson classification after saving
- [ ] Invalid lessons are removed from final retro document
- [ ] Critical lessons appear in project CLAUDE.md under correct heading
- [ ] Universal lessons appear in `~/.claude/rules/lessons-learned.md` under inferred category
- [ ] Running `/retro` on existing retro runs graduation only
- [ ] Files are created if they don't exist (CLAUDE.md section, lessons-learned.md)

## AI Validation

**Defaults**:
- Unit tests with mocked filesystem for file operations
- Code review by fresh-context sub-agent

**Custom**:
- Test classification flow with all four options (Invalid, Valid, Critical, Universal)
- Verify CLAUDE.md section format matches spec
- Verify lessons-learned.md category inference from tags
- Test graduation-only mode on existing retro

## Constraints

- User must approve each lesson classification (no automation)
- Lesson text is preserved exactly (no summarization or reformatting by AI)
- Categories for universal lessons are inferred, not prompted (reduces friction)
- CLAUDE.md edits append to existing section, never overwrite

## File Formats

### Project CLAUDE.md Section

```markdown
## Critical Lessons

- When changing a Claude Code plugin, always update its version in plugin.json. The plugin cache uses version as the key.
```

### User Rules File (`~/.claude/rules/lessons-learned.md`)

```markdown
# Lessons Learned

Hard-won lessons that apply across all projects.

## Plugin Development

- When changing a Claude Code plugin, always update its version in plugin.json. The plugin cache uses version as the key.

## Process

- [future lessons in this category]
```

### Category Inference

Infer category from retro tags, not exact match. The table below provides guidance, not rigid mapping:

| Tags like | Category |
|-----------|----------|
| plugin, extension | Plugin Development |
| git, commit, branch | Git Workflow |
| test, testing, coverage | Testing |
| process, methodology, workflow | Process |
| performance, optimization | Performance |
| (no clear match) | General |

**Category hygiene**:
- Before adding a new category, review existing categories in the file
- Don't let any one category sprawl (if a category has 10+ items, consider splitting)
- Don't create too many categories (aim for a balanced, navigable set)
- Err on the side of fitting into existing categories over creating new ones

## Context

- Brainstorm: `.lore/brainstorm/lessons-graduation-2026-01-31.md`
- Triggering example: `.lore/retros/plugin-version-management.md` contains a universal lesson currently invisible to future work
- lore-researcher agent only surfaces lessons when keywords match; graduation ensures critical/universal lessons are always loaded
