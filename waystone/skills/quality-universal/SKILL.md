---
name: Quality Universal
description: This skill should be used when auditing code quality, when the structural-auditor or semantic-auditor agents need quality criteria, when determining if code meets baseline standards, or when a project lacks explicit quality rules. Provides universal quality criteria that apply across all projects.
version: 0.1.0
---

# Universal Quality Criteria

This skill provides baseline quality standards for code auditing. These criteria apply universally regardless of language, framework, or project type.

## Purpose

Establish a consistent quality baseline when:
- A project has no explicit quality rules defined
- Auditing code that must meet minimum standards
- Determining what "good enough" means across projects

## Loading Quality Rules

Quality rules are loaded from `docs/rules/` in the target project. Each markdown file in that directory contributes to the quality criteria.

### Discovery Process

1. Check if `docs/rules/` exists in the project root
2. If found, read all `.md` files in that directory
3. Parse each file for quality criteria (headings, lists, thresholds)
4. Combine into unified quality assessment framework

### When Rules Are Missing

If `docs/rules/` does not exist or is empty:
1. Fall back to universal defaults defined in this skill
2. Flag in audit report that project-specific rules should be defined
3. Recommend creating `docs/rules/` with project standards

## Universal Quality Pillars

These five pillars form the baseline quality criteria. See `references/five-pillars.md` for detailed explanations.

### 1. Code Review Discipline

All code must be reviewed before merge.

**Criteria:**
- No direct commits to main/master branch
- Pull requests are mandatory
- PRs reference the issue/requirement being addressed
- Commit messages explain the "why" not just the "what"

**Audit checks:**
- Git history shows PR-based workflow
- Commits link to issues/specs

### 2. Test Coverage

Tests exist and exercise meaningful behavior.

**Criteria:**
- Public functions have corresponding tests
- Error paths are tested, not just happy paths
- Tests verify behavior, not just structure

**Audit checks:**
- Test files exist for source files with public APIs
- Tests contain assertions, not just execution
- Error handling code has test coverage

### 3. Cohesion and Size

Code units are focused and comprehensible.

**Criteria:**
- Functions: investigate if exceeding ~100 lines
- Files: investigate if exceeding ~800 lines
- Each unit does one thing well

**Audit checks:**
- Measure function/file line counts
- Flag violations with location
- Note when size is justified (with comment)

### 4. Self-Documenting Code

Code communicates its intent clearly.

**Criteria:**
- Names accurately describe behavior
- Comments explain "why" for non-obvious logic
- No misleading or outdated comments
- Clever code is documented or simplified

**Audit checks:**
- Function names match their behavior
- Complex logic has explanatory comments
- No TODO/FIXME comments older than 6 months without issue links

### 5. Reproducible Builds

Builds are deterministic and portable.

**Criteria:**
- All dependencies pinned to specific versions
- Build instructions documented in README
- No reliance on undeclared system dependencies

**Audit checks:**
- Lock files exist (package-lock.json, uv.lock, etc.)
- README contains build instructions
- CI configuration exists and passes

## Applying Criteria During Audit

When auditing a file:

1. Load project-specific rules first (via quality-project skill)
2. Fall back to universal criteria for undefined areas
3. Report violations by pillar
4. Distinguish critical (must fix) from advisory (should fix)

### Severity Levels

**Critical** - Must be addressed:
- No tests for public API
- Hardcoded secrets
- Direct commits to main (without PR)

**Warning** - Should be addressed:
- Size limits exceeded without justification
- Missing error path tests
- Outdated TODO comments

**Advisory** - Consider addressing:
- Could improve naming clarity
- Could add explanatory comment
- Dependency not pinned to exact version

## Integration with Agents

This skill provides criteria to:
- **structural-auditor**: Size limits, test presence, secrets detection
- **semantic-auditor**: Naming quality, comment accuracy, code clarity
- **api-contract-auditor**: Documentation requirements for external APIs
- **spec-tracer**: PR/commit linkage to requirements

## Additional Resources

### Reference Files

- **`references/five-pillars.md`** - Detailed explanation of each quality pillar with rationale and examples
