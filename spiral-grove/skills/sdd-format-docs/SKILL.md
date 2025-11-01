---
name: sdd-format-docs
description: Provides format specifications and schemas for SDD documentation synthesis. Use when generating CLAUDE.md files or working with manifest files for synthesis commands.
---

# SDD Format Documentation

## Available Documentation

**`docs/claude-md-format.md`**
- CLAUDE.md structure specification (root and module variants)
- Module constraint: ≤400 lines
- Hand-edit preservation markers
- Used by: `module-doc-synthesizer` agent, `/synthesize-docs` command

**`docs/module-manifest-schema.md`**
- JSON schema for `.sdd/module-manifest.json`
- Tracks documentation synthesis state (resumability)
- Used by: `/synthesize-docs` command

**`docs/spec-manifest-schema.md`**
- JSON schema for `.sdd/spec-manifest.json`
- Tracks specification synthesis state (resumability, drift detection)
- Used by: `/synthesize-specs` command
