# Waystone

AI Code Quality Audit plugin for Claude Code.

## Problem

AI-generated code suffers from recurring issues:

1. **Dead code** - Files written but never connected to the application
2. **Skipped research** - AI assumes API behavior instead of reading docs
3. **Sledgehammer fixes** - Guessing and patching instead of understanding
4. **Missing tests** - Structural coverage without behavioral verification
5. **Spec drift** - Code that doesn't trace back to any requirement

## Solution

Waystone provides auditing commands and specialized agents to catch these issues both at creation time and when retrofitting existing codebases.

## Installation

```bash
# Test locally
claude --plugin-dir /path/to/waystone

# Or copy to your plugins directory
cp -r waystone ~/.claude/plugins/
```

## Commands

### `/waystone:audit-init [scope]`

Build a checklist of files to audit.

**Scope options:**
- `all` - All source files (default)
- `staged` - Only git staged files
- `<path>` - Specific file or directory

**Output:** `.audit/checklist.md`

### `/waystone:audit-run [agent-filter]`

Process the audit checklist with quality agents.

**Agent filters (optional):**
- `structural` - Only structural-auditor
- `semantic` - Only semantic-auditor
- `api` - Only api-contract-auditor
- `spec` - Only spec-tracer

**Output:** `.audit/reports/` and `.audit/summary.md`

### `/waystone:audit-dead-code`

Find unreachable and orphaned code by tracing from entry points.

**Requires:** Entry points defined in project's CLAUDE.md

**Output:** `.audit/dead-code.md`

### `/waystone:audit-recheck <file>`

Deep-dive research on a file flagged by api-contract-auditor.

Fetches actual API documentation and compares against implementation. Run one file at a time to manage context.

**Output:** `.audit/recheck/[file].md`

## Agents

| Agent | Purpose |
|-------|---------|
| `structural-auditor` | Size limits, logging presence, test coverage, secret detection |
| `semantic-auditor` | Name-behavior alignment, comment accuracy, logic errors, test quality |
| `api-contract-auditor` | Quick pass: was API usage informed by docs or guessed? (YES/NO/RECHECK) |
| `spec-tracer` | Links code to specifications in `.sdd/specs/`, flags orphaned code |

## Configuration

### Quality Rules

Define project quality standards in `docs/rules/` as markdown files:

```markdown
---
thresholds:
  max_function_lines: 100
  max_file_lines: 800
  coverage_target: 80
---

# Code Quality Rules

[Your rules here...]
```

See `skills/quality-project/examples/quality-template.md` for a starter template.

### Entry Points (for dead-code detection)

Add to your project's CLAUDE.md:

```markdown
## Entry Points

- `src/index.ts` - Main application entry
- `src/routes/*.ts` - Route handlers
- `src/workers/*.ts` - Background workers
```

## Workflow

### Full Audit

```bash
/waystone:audit-init all
/waystone:audit-run
# Review .audit/summary.md
# For files needing recheck:
/waystone:audit-recheck src/api/client.ts
```

### Pre-commit Check

```bash
/waystone:audit-init staged
/waystone:audit-run
```

### Dead Code Cleanup

```bash
/waystone:audit-dead-code
# Review .audit/dead-code.md
# Investigate orphaned files
```

## Output Structure

```
.audit/
├── checklist.md          # Files to audit (from audit-init)
├── summary.md            # Aggregated findings (from audit-run)
├── dead-code.md          # Orphan analysis (from audit-dead-code)
├── reports/              # Per-file audit findings (mirrors source tree)
│   └── src/api/client.md # For src/api/client.ts
└── recheck/              # Deep-dive research results (mirrors source tree)
    └── src/api/client.md # For src/api/client.ts
```

## Requirements

- Project should have CLAUDE.md with language/framework info
- For spec-tracer: specifications in `.sdd/specs/`
- For dead-code: entry points defined in CLAUDE.md
- For quality rules: `docs/rules/` directory (optional, defaults apply)

## License

MIT
