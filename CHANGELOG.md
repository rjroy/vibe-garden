# Changelog

All notable changes to this repository are documented here.

This project uses [CalVer](https://calver.org/) (YYYY.MM) for repository releases. Individual plugins maintain independent [semver](https://semver.org/) versions.

---

## [2026.04] - 2026-04-25

**Lore Development reset.** The `lore-development` plugin was redesigned around a three-tier directory model (`work/`, `reference/`, `learned/`) that separates in-flight artifacts, durable invariants, and institutional knowledge. Existing projects migrate via `/tend migrate`.

### Plugin Versions

- **lore-development** v1.11.2 → v2.0.0 (breaking: directory layout, skill set)

### Lore Development - Breaking Changes

- Directory layout moved from a flat `.lore/{specs,plans,notes,retros,...}` to `.lore/work/`, `.lore/reference/`, and `.lore/learned/`. Skills, schemas, and references updated to the new paths.
- `build/` was renamed to `work/` to avoid colliding with common gitignore conventions.
- The `excavate` skill was removed. Its role splits between `distill` (promote findings into reference) and `tend migrate` (move legacy projects onto the new layout).

### Lore Development - Added

- `distill` skill - promotes verified invariants from code or work artifacts into `.lore/reference/`, with user-gated reconciliation.
- `learn` skill - user-invoked capture for institutional knowledge (rules, snippets, config tricks). Gates on specificity, not shape; never auto-fires from other skills.
- `tend migrate` mode - one-shot migration for projects on the pre-redesign layout.

### Lore Development - Changed

- Frontmatter schema overhauled to match the new layout and artifact taxonomy.
- `tend` references (`directories.md`, `status.md`, `filenames.md`) rewritten for the three-tier model.
- `back-propagate`, `retro`, `update-stubs`, and other skills updated for the new paths.

---

## [2026.02] - 2026-02-01

**First formal release.** This repository has evolved through several identities before settling as Vibe Garden, a collection of Claude Code plugins.

### Plugins

- **compass-rose** v1.3.0 - GitHub Projects integration
- **lore-development** v0.13.0 - Project context and workflow management
- **notify-hook** v1.0.0 - Desktop and mobile notifications
- **mind-reader** v1.0.0 - Active feedback based on session patterns

### What's Included

- Skill-based project management with backlog analysis and priority recommendations
- Research, brainstorming, specification, and retrospective workflows
- Desktop notifications (Linux/macOS) and mobile push via ntfy.sh
- Session duration tracking, unusual hours detection, and sentiment analysis

---

## Prior History

This repository consolidated several experimental plugins developed between late 2025 and early 2026. Earlier commit history reflects that evolution.
