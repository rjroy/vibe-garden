---
description: Find unreachable and orphaned code
allowed-tools: Read, Glob, Grep, Bash
---

# Dead Code Detection

Find files that are not reachable from any entry point.

## Prerequisites

This command requires CLAUDE.md to define entry points. Check for:
- Main entry files (index.ts, main.py, etc.)
- Route definitions
- Export configurations
- Build entry points

If CLAUDE.md doesn't define entry points:
- Report that dead code detection cannot run
- Explain that entry points must be documented
- Provide example of what to add to CLAUDE.md:

```markdown
## Entry Points

- `src/index.ts` - Main application entry
- `src/routes/*.ts` - Route handlers
- `src/workers/*.ts` - Background workers
```

Do not attempt to guess entry points. Exit with clear instructions.

## Process

### 1. Parse Entry Points

Read CLAUDE.md and extract entry point definitions:
- Look for "Entry Points" section
- Parse file paths and globs
- Validate each entry point exists

### 2. Build Import Graph

Starting from each entry point:
1. Parse imports/requires
2. Recursively follow each import
3. Build set of all reachable files

**Language-specific parsing:**

**JavaScript/TypeScript:**
```
import X from './path'
require('./path')
export * from './path'
```

**Python:**
```
import module
from module import X
```

**Go:**
```
import "package/path"
```

### 3. Compare Against All Files

Get list of all source files (same scope as audit-init).
Compare against reachable set.

**Orphaned files:** Files that exist but are not in reachable set.

### 4. Categorize Orphans

For each orphaned file, determine likely reason:

**Test files:** `*.test.ts`, `*_test.py`, `*_test.go`
- Not orphaned, tests are invoked by test runner
- Mark as: EXPECTED (test file)

**Config files:** Various config patterns
- Not orphaned, used by build tools
- Mark as: EXPECTED (configuration)

**Generated files:** In `dist/`, `build/`, `generated/`
- Not orphaned, generated at build time
- Mark as: EXPECTED (generated)

**Type declarations:** `*.d.ts`, type stubs
- Not orphaned, used by compiler
- Mark as: EXPECTED (types)

**Actually orphaned:** Everything else
- Mark as: ORPHAN
- Flag for investigation

### 5. Generate Report

Output findings:

```markdown
# Dead Code Analysis

Run: [timestamp]
Entry Points: [count]
Total Files: [count]
Reachable: [count]
Orphaned: [count]

## Entry Points Analyzed
- src/index.ts
- src/routes/*.ts (5 files)

## Orphaned Files

### Likely Dead Code
| File | Last Modified | Recommendation |
|------|---------------|----------------|
| src/old-feature.ts | 6 months ago | Delete or document |
| src/utils/deprecated.ts | 1 year ago | Probably safe to delete |

### Needs Investigation
| File | Notes |
|------|-------|
| src/api/internal.ts | May be loaded dynamically |

## Excluded (Expected)
- 15 test files
- 3 config files
- 2 type declarations
```

## Output

After analysis:
1. Report count of orphaned files
2. Highlight files that are likely safe to delete
3. List files needing investigation
4. Save report to `.audit/dead-code.md`

## Limitations

**Dynamic imports:**
- Cannot trace `import()` with variable paths
- Cannot trace `require()` with computed strings
- Flag files that might be dynamically loaded

**External entry points:**
- CLI tools may have entry points not in CLAUDE.md
- API routes may be loaded by framework magic
- Workers may be spawned dynamically

**Recommendation:** When in doubt, flag for investigation rather than claiming dead.

## Edge Cases

**Circular imports:**
- Handle gracefully, don't infinite loop
- File is reachable if in any cycle from entry point

**Re-exports:**
- Follow re-export chains
- `export * from` counts as import

**Conditional imports:**
- Treat all branches as reachable
- Don't analyze runtime conditions
