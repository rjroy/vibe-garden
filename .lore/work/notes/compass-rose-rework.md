---
title: "Implementation notes: compass-rose-rework"
date: 2026-05-20
status: complete
tags: [implementation, notes, compass-rose, lore-development]
source: .lore/work/specs/compass-rose-rework.md
modules: [compass-rose, lore-development]
---

# Implementation notes: compass-rose-rework

Source: [compass-rose-rework spec](../specs/compass-rose-rework.md)

Status: Complete — compass-rose-rework — 6/6 phases complete — all requirements pass

## Phase tracker

**Phase 1 — Delete retired artifacts (start-work, gh-api-scripts, file-issue)** — Done

Deleted: `compass-rose/skills/start-work/`, `compass-rose/skills/gh-api-scripts/`, `lore-development/skills/file-issue/`. All three were present and removed cleanly.

**Phase 2 — Rewrite add-item skill (REQ-CR-2, REQ-CR-3)** — Done

Rewrote add-item/SKILL.md: 399 lines → 65 lines. No GitHub references. Status hardcoded open, XL escalation removed, priority/size truly optional. Skill-reviewer: all requirements met.

**Phase 3 — Rewrite next-item skill (REQ-CR-4)** — Done

Rewrote next-item/SKILL.md: dropped all GitHub API calls and 100+ lines of git heuristic scoring. Priority+date sort only. Skill-reviewer: all requirements met, explicit anti-patterns added for start-work and git log.

**Phase 4 — Rewrite backlog skill + update backlog-analyzer agent (REQ-CR-5)** — Done

Rewrote backlog/SKILL.md (file-based, wontfix included). Updated backlog-analyzer.md: new `{ filepath, title, priority, size, status, date, body }` input shape, scoring logic preserved. One fix cycle: reviewer caught bare filenames in example headings — corrected to full relative paths.

**Phase 5 — Rewrite reprioritize skill + update codebase-scanner agent (REQ-CR-6)** — Done

Rewrote reprioritize/SKILL.md (file-based, Edit tool for meta updates, no report saved). Updated codebase-scanner.md: new input shape, output uses "Updates to Apply" table. One fix cycle: reviewer caught leftover "gh CLI" in Next Steps and old field list (id, url) in parse comment — both corrected.

**Phase 6 — Update READMEs and vision document (REQ-CR-8)** — Done

Rewrote compass-rose/README.md (870 → ~60 lines, file-based model). Removed file-issue row from lore-development/README.md. Updated vision.md: anti-goal now references `.lore/work/issues/`, Principle 4 example updated, Principle 6 start-work reference removed. One fix cycle: reviewer caught start-work in Principle 6 body text — corrected.

## Decisions and divergences

No spec divergences. One minor correction applied directly (next-item anti-pattern line named the retired skill by name; replaced with behavior-only wording). The .compass-rose/config.json in the vibe-garden repo itself was also deleted — it was vibe-garden's own project config for the old GitHub Projects integration.
