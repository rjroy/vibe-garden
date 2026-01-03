---
description: Build checklist of files to audit
argument-hint: [all|staged|<path>]
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Audit Initialization

Build a checklist of files requiring quality audit.

## Scope Argument

The scope determines which files to audit:
- `all` - All source files in the project (default if no argument)
- `staged` - Only files staged for commit (git)
- `<path>` - Specific file or directory path

Scope provided: $ARGUMENTS

If no scope provided, use `all`.

## Process

### 1. Detect Project Configuration

Check for CLAUDE.md to understand:
- Project language and framework
- Source directories
- Test directories
- Entry points (for dead-code analysis)

If CLAUDE.md is missing or lacks this information:
- Warn that project configuration is incomplete
- Recommend initializing project with proper CLAUDE.md
- Proceed with best-effort detection from file structure

### 2. Determine File Scope

**For `all`:**
- Find all source files (exclude node_modules, dist, build, .git, vendor, __pycache__)
- Identify file types (.ts, .js, .py, .go, etc.)
- Exclude generated files and dependencies

**For `staged`:**
- Run: `git diff --cached --name-only`
- Filter to source files only
- Include both modified and new files

**For `<path>`:**
- If file, add just that file
- If directory, add all source files in directory
- Validate path exists

### 3. Create Audit Directory

Create `.audit/` directory if it doesn't exist.

### 4. Generate Checklist

Create `.audit/checklist.md` with:
- Timestamp of initialization
- Scope used
- Total file count
- Each file with status

**Checklist Format:**
```markdown
# Audit Checklist

Generated: [timestamp]
Scope: [all|staged|path]
Total Files: [count]

## Files

| Status | File | Agents |
|--------|------|--------|
| pending | src/index.ts | structural, semantic |
| pending | src/api/users.ts | structural, semantic, api-contract |
| pending | src/utils/helpers.ts | structural, semantic |
```

### 5. Determine Applicable Agents

For each file, determine which agents should run:
- **structural-auditor**: All source files
- **semantic-auditor**: All source files
- **api-contract-auditor**: Files with external API imports
- **spec-tracer**: Only if `.sdd/specs/` exists

Mark each file with its applicable agents.

## Output

After creating the checklist:
1. Report total files to audit
2. Report agents that will be used
3. Show path to checklist: `.audit/checklist.md`
4. Instruct user to run `/waystone:audit-run` to process

## Edge Cases

**No source files found:**
- Report that no auditable files were found
- Check if in correct directory
- Suggest checking project structure

**Git not available (for staged):**
- Report that git is not available
- Suggest using `all` or specific path instead

**Path doesn't exist:**
- Report that specified path was not found
- Show similar paths if possible
- Ask for correction
