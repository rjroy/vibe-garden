# Synthesize Commands - Practical Reference

**Purpose**: Practical guide for retrofitting existing codebases with SDD documentation and specifications using the synthesize commands.

**Companion Documents**:
- [SDD-QUICK-REFERENCE.md](./SDD-QUICK-REFERENCE.md) - Core SDD workflow commands
- [SDD-FOUNDATIONS.md](./SDD-FOUNDATIONS.md) - SDD methodology foundations

**Last Updated**: 2025-10-21

---

## Table of Contents

1. [Overview](#overview)
2. [When to Use Synthesize Commands](#when-to-use-synthesize-commands)
3. [Command: /synthesize-docs](#command-synthesize-docs)
4. [Command: /synthesize-specs](#command-synthesize-specs)
5. [Working Together: Docs + Specs](#working-together-docs--specs)
6. [Practical Workflows](#practical-workflows)
7. [Common Scenarios](#common-scenarios)
8. [Performance and Scale](#performance-and-scale)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The synthesize commands enable **large-scale codebase retrofitting** by automatically generating SDD documentation and specifications from existing implementations. These are "reverse engineering" commands that analyze code to produce SDD artifacts.

### The Two Commands

| Command | Purpose | Output | Use When |
|---------|---------|--------|----------|
| `/synthesize-docs` | Generate CLAUDE.md files (HOW documentation) | `[module]/CLAUDE.md` + root `CLAUDE.md` | Need operational documentation for maintenance |
| `/synthesize-specs` | Generate specifications (WHAT requirements) | `.sdd/specs/[module].md` | Need to adopt SDD on legacy codebase |

### Key Characteristics

**One-Click Operation**:
- Automatic module discovery
- Parallel processing (batches of 10)
- Resumable if interrupted
- Safe to re-run (idempotent)

**Framework-Agnostic**:
- TypeScript, JavaScript, Python, Go, Rust, Java, C++
- Unreal Engine support (C++ modules, Plugins, Content)
- Detects modules via package files and directory patterns

**Intelligent Analysis**:
- Reads code, tests, configs, and documentation
- Extracts requirements from behavior
- Links to existing SDD specs (if present)
- Detects drift between specs and implementation

---

## When to Use Synthesize Commands

### Use `/synthesize-docs` When:

✅ **Onboarding new team members**
- Need quick understanding of "how the system works"
- Want operational knowledge extracted from code
- Large codebase without documentation

✅ **Maintenance and debugging**
- Need reference for module responsibilities
- Want to understand integration points
- Looking for implementation patterns

✅ **Knowledge preservation**
- Team members leaving
- Tribal knowledge needs capturing
- Code lacks comments/documentation

✅ **Post-implementation documentation** (SDD workflow)
- Completed implementation via `/implementation` command
- Need to document operational knowledge
- Want to capture as-built architecture

### Use `/synthesize-specs` When:

✅ **Adopting SDD on legacy codebase**
- Want to start using SDD workflow
- Need specifications for existing features
- No existing requirement documents

✅ **Drift detection**
- Have existing specs but suspect implementation diverged
- Want to compare intended vs. actual behavior
- Need to identify undocumented changes

✅ **Compliance and auditing**
- Need to document what system actually does
- Want requirements extracted from implementation
- Preparing for security/compliance review

✅ **Reverse engineering**
- Inherited codebase without documentation
- Need to understand requirements from code
- Planning refactoring or rewrite

### Don't Use Synthesize Commands For:

❌ **New feature development** - Use `/spec-writing` → `/plan-generation` workflow instead
❌ **Small codebases** - Manual documentation may be faster (<10 modules)
❌ **Prototype code** - Requirements will change rapidly
❌ **Throwaway scripts** - Not worth the documentation overhead

---

## Command: /synthesize-docs

### What It Does

Generates `CLAUDE.md` documentation files by analyzing module implementations. These files provide **operational knowledge** for maintenance and debugging.

**Output Structure**:
```
project-root/
├── CLAUDE.md                    # Root overview (project structure, modules)
├── src/
│   ├── auth/
│   │   └── CLAUDE.md            # Auth module documentation (≤400 lines)
│   ├── api/
│   │   └── CLAUDE.md            # API module documentation
│   └── utils/
│       └── CLAUDE.md            # Utils module documentation
└── .sdd/
    └── module-manifest.json     # Tracking manifest
```

### How It Works

**Phase 1: Module Discovery**
1. Scans for package files (`package.json`, `setup.py`, `Cargo.toml`, `*.uproject`, etc.)
2. Scans for code-heavy directories (`src/`, `lib/`, `Source/`, etc.)
3. Ranks by confidence (high: has package file + tests, medium: has tests, low: code only)
4. Presents list for user approval

**Phase 2: Parallel Generation** (Batches of 10)
1. Spawns `module-doc-synthesizer` agents in parallel
2. Each agent analyzes one module (code, tests, configs)
3. Generates CLAUDE.md (≤400 lines, operational focus)
4. Updates manifest with status (completed/failed)

**Phase 3: SDD Integration** (Optional)
1. If `.sdd/specs/` exists, matches modules to specs
2. Adds **Origin** field linking CLAUDE.md → spec
3. Creates traceability between documentation and requirements

**Phase 4: Root Documentation**
1. Generates root `CLAUDE.md` with project overview
2. Indexes all modules with links to their CLAUDE.md files

### Usage

**Full project synthesis**:
```
/synthesize-docs
```

**Single module regeneration**:
```
/synthesize-docs src/auth
```

### Command Flow

```
1. Module Discovery
   ├─→ Check for .sdd/module-manifest.json (resumability)
   ├─→ Check for .sdd/spec-manifest.json (cross-command integration)
   └─→ Scan codebase → Present list → User approves

2. Parallel Generation (10 at a time)
   ├─→ Spawn agents for pending/failed modules
   ├─→ Agents analyze and write CLAUDE.md files
   └─→ Update manifest with results

3. SDD Integration (if .sdd/specs/ exists)
   ├─→ Match modules to specs
   ├─→ Add Origin fields to CLAUDE.md files
   └─→ Report linked modules

4. Root CLAUDE.md
   └─→ Generate project overview with module index
```

### Key Features

**Resumability**:
- Interrupted synthesis can continue from where it left off
- Re-running on completed project prompts: "Regenerate all? [y/n]"
- Safe to run multiple times

**Hand-Edit Preservation**:
- Content between `<!-- BEGIN: HAND-EDITED -->` markers is preserved
- Regeneration updates AI sections, keeps manual edits
- No risk of losing custom documentation

**Cross-Command Integration**:
- Can use `.sdd/spec-manifest.json` from `/synthesize-specs` as starting point
- Avoids re-discovering modules if specs already generated
- Prompts: "Use spec manifest? [y/n]"

**Performance**:
- Target: 100 modules in ~10-15 minutes
- Batched parallel execution (max 10 concurrent agents)
- Progress tracking in manifest

### Output Example

**Module CLAUDE.md** (`src/auth/CLAUDE.md`):
```markdown
# Authentication Module

**Origin**: Implemented from [.sdd/specs/authentication.md](.sdd/specs/authentication.md)
**Last Generated**: 2025-10-21T14:30:00Z

## Purpose

Handles user authentication via OAuth2 and session management...

## Architecture

- **OAuth2 Flow**: Authorization code grant with PKCE
- **Session Storage**: Redis-backed sessions (30-day TTL)
- **Token Management**: JWT access tokens (15min) + refresh tokens (30d)

## Key Components

### `OAuthService`
- **Responsibility**: Manages OAuth2 flow with external providers
- **Integration**: Auth0 SDK for provider abstraction
...

## Configuration

[Module-specific config details]

## Common Tasks

[Maintenance operations]
```

**Root CLAUDE.md**:
```markdown
# Project Name

**Last Generated**: 2025-10-21T14:30:00Z

## Purpose

Brief project description extracted from README/package.json...

## Architecture

High-level system overview...

## Directory Structure

```
src/
├── auth/          # Authentication and authorization
├── api/           # REST API endpoints
└── utils/         # Shared utilities
```

## Modules

- [Authentication](src/auth/CLAUDE.md) - OAuth2 and session management
- [API](src/api/CLAUDE.md) - REST API implementation
- [Utilities](src/utils/CLAUDE.md) - Shared helper functions

## Getting Started

[Instructions extracted from README, package.json scripts, Makefile]
```

### Manifest Structure

`.sdd/module-manifest.json`:
```json
{
  "generated_at": "2025-10-21T14:30:00Z",
  "project_root": "/absolute/path/to/project",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "claude_md_path": "src/auth/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/broken",
      "status": "failed",
      "claude_md_path": "src/broken/CLAUDE.md",
      "error": "No source files found in module directory"
    }
  ]
}
```

**Status values**: `pending`, `completed`, `failed`

---

## Command: /synthesize-specs

### What It Does

Generates specification files by reverse-engineering requirements from implementation. These files capture **WHAT the system does** (requirements, constraints, acceptance criteria).

**Output Structure**:
```
.sdd/
├── spec-manifest.json           # Tracking manifest with drift status
└── specs/
    ├── auth.md                  # Auth module specification
    ├── api.md                   # API module specification
    └── utils.md                 # Utils module specification
```

### How It Works

**Phase 1: Module Discovery**
1. Scans for package files and code-heavy directories (same as `/synthesize-docs`)
2. Ranks by confidence
3. Presents list for user approval
4. Creates `.sdd/specs/` directory and manifest

**Phase 2: Parallel Specification Generation** (Batches of 10)
1. Spawns `module-spec-synthesizer` agents in parallel
2. Each agent:
   - Checks for existing spec (drift detection mode)
   - Analyzes code, tests, configs
   - Extracts requirements, constraints, acceptance criteria
   - Compares to existing spec (if present) and marks drift
   - Generates spec following `/spec-writing` template
3. Updates manifest with status and drift information

**Phase 3: Summary and Recommendations**
1. Analyzes drift across all modules
2. Reports drift statistics
3. Provides recommendations for resolution

### Usage

**Full project spec synthesis**:
```
/synthesize-specs
```

**Single module spec regeneration**:
```
/synthesize-specs src/auth
```

### Command Flow

```
1. Module Discovery
   ├─→ Check for .sdd/spec-manifest.json (resumability)
   ├─→ Check for .sdd/module-manifest.json (cross-command integration)
   ├─→ Scan codebase → Present list → User approves
   └─→ Create .sdd/specs/ directory

2. Parallel Spec Generation (10 at a time)
   ├─→ Spawn agents for pending/failed modules
   ├─→ Agents analyze implementation
   ├─→ Check for existing specs → Drift detection
   ├─→ Generate specs with drift reports (if applicable)
   └─→ Update manifest with results and drift status

3. Summary and Recommendations
   ├─→ Count modules with drift
   ├─→ Report drift details
   └─→ Recommend next steps
```

### Key Features

**Drift Detection**:
- Compares existing specs to actual implementation
- Identifies added, missing, modified requirements
- Flags violated constraints
- Provides severity assessment (High/Medium/Low)

**Evidence-Based Requirements**:
- Every requirement traceable to code or tests
- Quantified metrics from test assertions
- Constraints from validation logic
- No invented requirements

**Reverse Engineering**:
- Specs marked with `**Reverse-Engineered**: true`
- Source module tracked in metadata
- Honest about gaps (if no tests, admits limited spec quality)

**Cross-Command Integration**:
- Can use `.sdd/module-manifest.json` from `/synthesize-docs` as starting point
- Avoids re-discovering modules
- Prompts: "Use module manifest? [y/n]"

**Resumability**:
- Same as `/synthesize-docs`
- Can continue interrupted synthesis
- Safe to re-run with drift detection

### Output Example

**Generated Spec** (`.sdd/specs/auth.md`):

```markdown
# Authentication Module Specification

**Version**: 1.0.0
**Status**: Draft
**Created**: 2025-10-21T14:30:00Z
**Last Updated**: 2025-10-21T14:30:00Z
**Reverse-Engineered**: true
**Source Module**: src/auth

---

## Drift Detection Report

**Last Comparison**: 2025-10-21T14:30:00Z
**Compared Against**: Version 1.0.0
**Drift Status**: Drift Detected

### Requirements Added (Not in Original Spec)

- API key authentication support
- Token refresh endpoint

### Requirements Modified (Code Differs from Spec)

| Requirement | Spec Says | Code Does | Severity |
|-------------|-----------|-----------|----------|
| Response time | < 100ms | < 200ms (test) | Medium |

### Recommendations

1. Update spec to reflect new API key authentication feature
2. Evaluate if 200ms response time is acceptable or optimize code

---

## Executive Summary

The Authentication Module provides user authentication via OAuth2 and session management...

## User Story

As a user, I want to securely authenticate to the application so that I can access protected resources.

## Stakeholders

**Primary**: End users requiring secure access
**Secondary**: API consumers, third-party integrations
**Tertiary**: Security auditors, compliance teams

## Success Criteria

1. Authentication success rate > 99.9%
2. Login flow completes in < 200ms (p95)
3. Zero unauthorized access incidents
4. Support 10,000 concurrent sessions

## Functional Requirements

### FR-1: OAuth2 Authentication
The system must support OAuth2 authorization code flow with PKCE for secure authentication.

**Evidence**: Code analysis shows OAuth2Provider class implementing RFC 7636 PKCE extension.

### FR-2: Session Management
The system must maintain user sessions with configurable TTL.

**Evidence**: SessionManager uses Redis with 30-day default TTL (configurable via SESSION_TTL env var).

[Additional requirements...]

## Non-Functional Requirements

### Performance
- Authentication endpoint must respond in < 200ms at 95th percentile
  - **Evidence**: Test assertion `expect(responseTime).toBeLessThan(200)` in tests/auth/performance.test.ts

### Security
- All tokens must be signed with RS256 algorithm
  - **Evidence**: JWT configuration in oauth.ts uses RS256 signing
- Passwords must not be logged or exposed in errors
  - **Evidence**: ErrorHandler sanitizes auth-related errors

[Additional NFRs...]

## Explicit Constraints

- **DO NOT** support basic auth (security risk)
  - **Evidence**: Code comment in auth.ts: "Basic auth disabled per security policy"
- **DO NOT** store tokens in localStorage (XSS vulnerability)
  - **Evidence**: Session storage uses HTTP-only cookies only

## Technical Context

### Dependencies
- Auth0 SDK (external OAuth provider)
- Redis (session storage)
- jsonwebtoken (JWT handling)

### Integration Points
- **Incoming**: API Gateway forwards auth requests
- **Outgoing**: User service for profile data
- **Events**: Publishes auth.login, auth.logout events

## Acceptance Tests

### AC-1: Successful OAuth Login
**Given** a valid OAuth authorization code
**When** user completes OAuth flow
**Then** system issues access token and refresh token
**And** creates session in Redis
**Evidence**: tests/auth/oauth.test.ts line 45

[Additional acceptance criteria...]

## Open Questions

- TODO: Should we support SAML for enterprise customers? (found in auth.ts:120)
- Should session TTL vary by user role? (found in session.ts:67)

## Out of Scope

- Multi-factor authentication (planned for v2.0)
- Biometric authentication
- Social login (Google, Facebook) beyond OAuth providers
```

### Manifest Structure

`.sdd/spec-manifest.json`:
```json
{
  "generated_at": "2025-10-21T14:30:00Z",
  "project_root": "/absolute/path/to/project",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "spec_path": ".sdd/specs/auth.md",
      "drift_detected": true,
      "drift_summary": {
        "added": 2,
        "missing": 0,
        "modified": 1,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "spec_path": ".sdd/specs/api.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": null
    }
  ]
}
```

**Status values**: `pending`, `completed`, `failed`

### Drift Severity Guidelines

**High Severity**:
- Breaking behavior changes
- Security degradation
- Performance >50% worse than spec
- Violated critical constraints

**Medium Severity**:
- Performance 25-50% worse
- Scope expansion (new features added)
- Optional feature changes

**Low Severity**:
- Minor improvements
- Cosmetic changes
- Relaxed non-critical constraints

---

## Working Together: Docs + Specs

The two synthesize commands are complementary and designed to work together.

### CLAUDE.md vs Specifications

| Aspect | CLAUDE.md (`/synthesize-docs`) | Specifications (`/synthesize-specs`) |
|--------|-------------------------------|--------------------------------------|
| **Purpose** | Operational maintenance | Requirements definition |
| **Focus** | HOW it works | WHAT it does |
| **Audience** | Developers maintaining code | Stakeholders, product teams, QA |
| **Content** | Architecture, components, config, tasks | Requirements, constraints, acceptance tests |
| **Use Case** | Debugging, refactoring, onboarding | Feature planning, compliance, drift detection |
| **Length** | ≤400 lines per module | 10-15 pages typical |

### Recommended Order

**Scenario 1: Documentation-First (Maintenance Focus)**
```
1. /synthesize-docs          # Generate operational docs
2. /synthesize-specs          # Generate specs (uses module manifest)
```
Use when: Primary goal is understanding how the system works

**Scenario 2: Specification-First (Requirements Focus)**
```
1. /synthesize-specs          # Generate specs with drift detection
2. /synthesize-docs           # Generate docs (uses spec manifest, adds Origin links)
```
Use when: Primary goal is adopting SDD or compliance documentation

**Scenario 3: Both Simultaneously**
```
Run both commands (order doesn't matter if starting fresh)
```
Use when: Retrofitting large legacy project for complete documentation

### Cross-Command Benefits

When both commands are run:
- **Shared module discovery**: Second command reuses first command's manifest (avoids re-scanning)
- **Traceability**: CLAUDE.md files link to specs via Origin field
- **Complementary views**: Specs answer "why", docs answer "how"
- **Complete picture**: Requirements + implementation knowledge

---

## Practical Workflows

### Workflow 1: Legacy Codebase Onboarding

**Goal**: New team member needs to understand large undocumented codebase

**Steps**:
```
1. /synthesize-docs
   → Generates CLAUDE.md for all modules
   → Read root CLAUDE.md for project overview
   → Navigate to specific modules for deep dives

2. (Optional) /synthesize-specs
   → Understand requirements/constraints
   → See what system is supposed to do
```

**Time Investment**: ~15 minutes for 100 modules
**Outcome**: Comprehensive operational documentation

---

### Workflow 2: Adopting SDD on Existing Project

**Goal**: Start using SDD workflow on legacy codebase

**Steps**:
```
1. /synthesize-specs
   → Generates specs for all modules
   → Review specs for accuracy
   → Fix any obvious drift

2. Begin SDD workflow for new features:
   → /spec-writing (or update synthesized spec)
   → /plan-generation
   → /task-breakdown
   → /implementation

3. (Optional) /synthesize-docs
   → Generate docs after implementation
   → Or update existing docs
```

**Time Investment**: ~30-45 minutes for 100 modules
**Outcome**: Complete specs enabling SDD adoption

---

### Workflow 3: Drift Detection and Remediation

**Goal**: Find where implementation diverged from specs

**Steps**:
```
1. /synthesize-specs
   → Compares code to existing specs
   → Generates drift reports

2. Review drift reports in .sdd/specs/*.md
   → Look for "Drift Detection Report" section
   → Assess severity (High/Medium/Low)

3. For each drifted module, decide:
   a) Update spec to match code (accept drift)
      → Edit spec, remove drift report
   b) Fix code to match spec (reject drift)
      → Update implementation
      → Re-run /synthesize-specs to verify
   c) Document intentional deviation
      → Add note to spec explaining why

4. (Optional) /review spec
   → Validate updated specs before continuing
```

**Time Investment**: Variable (depends on drift extent)
**Outcome**: Specs synchronized with implementation

---

### Workflow 4: Compliance Documentation

**Goal**: Generate requirements documentation for audit/compliance

**Steps**:
```
1. /synthesize-specs
   → Generates evidence-based specs
   → All requirements traceable to code

2. Review generated specs:
   → Add business context if missing
   → Add compliance mappings (e.g., GDPR article references)
   → Mark security-critical requirements

3. /synthesize-docs
   → Generate operational docs
   → Demonstrate how requirements are implemented

4. Export documentation:
   → Convert .md files to PDF if needed
   → Include in compliance package
```

**Time Investment**: ~1 hour for 100 modules (generation + review)
**Outcome**: Audit-ready documentation

---

### Workflow 5: Single Module Update

**Goal**: Updated one module significantly, need refreshed docs/specs

**Steps**:
```
# After implementing changes to src/auth:

1. /synthesize-specs src/auth
   → Regenerates only auth spec
   → Detects drift from previous version
   → Review and resolve drift

2. /synthesize-docs src/auth
   → Regenerates only auth CLAUDE.md
   → Updates operational documentation
   → Preserves hand-edits

3. (Optional) /review spec
   → Validate spec quality before committing
```

**Time Investment**: ~30 seconds per module
**Outcome**: Up-to-date single module documentation

---

## Common Scenarios

### Scenario: No Modules Detected

**Symptom**: Command reports "No modules detected"

**Causes**:
- Project structure doesn't match expected patterns
- Working directory is wrong
- All code in non-standard directories

**Solutions**:
1. Verify working directory: `pwd`
2. Check for package files: `ls package.json setup.py Cargo.toml`
3. Manually specify module: `/synthesize-docs src/custom-path`
4. If truly custom structure, add modules manually to manifest

---

### Scenario: All Modules Failed

**Symptom**: All modules show `status: "failed"` in manifest

**Common Errors**:
- "No source files found" → Empty directories or wrong paths
- "Permission denied" → File system permissions issue
- ".sdd/specs/ directory does not exist" → Command should create it (bug report)

**Solutions**:
1. Check module directories have actual code files
2. Verify file permissions: `ls -la`
3. Re-run command (may be transient issue)
4. Check `.sdd/module-manifest.json` or `.sdd/spec-manifest.json` for specific errors

---

### Scenario: Module Exceeds 400 Lines

**Symptom**: Warning "Generated CLAUDE.md exceeded 400 lines after condensing"

**Cause**: Module is too large or complex for single CLAUDE.md

**Solutions**:
1. Accept the warning (file still generated, just longer)
2. Consider splitting module into sub-modules
3. Manually edit CLAUDE.md to condense sections
4. Use hand-edit markers to preserve condensed version

---

### Scenario: Drift Detected Everywhere

**Symptom**: All modules show drift from existing specs

**Causes**:
- Specs are outdated (common for legacy projects)
- Implementation evolved significantly
- Original specs were aspirational, not descriptive

**Solutions**:
1. Review drift severity (focus on High first)
2. Batch update specs to match implementation (if drift is acceptable)
3. For critical drift (security, performance), fix implementation
4. Document intentional deviations in specs

---

### Scenario: Poor Spec Quality (No Tests)

**Symptom**: Warning "No test files found for module"

**Cause**: Module lacks tests (common in legacy code)

**Impact**: Spec quality limited (acceptance criteria inferred from code only)

**Solutions**:
1. Accept limited spec (still useful for basic requirements)
2. Add tests to improve future regeneration quality
3. Manually enhance spec with domain knowledge
4. Use hand-edit markers to preserve enhancements

---

### Scenario: Interrupted Synthesis

**Symptom**: Command stops mid-execution (network issue, timeout, etc.)

**Solution**:
```
Re-run the command:
/synthesize-docs    or    /synthesize-specs

Command will:
1. Detect existing manifest
2. Show progress: "X completed, Y pending, Z failed"
3. Prompt: "Continue from where we left off? [y/n]"
4. Resume with pending/failed modules only
```

**Idempotent**: Safe to run multiple times

---

## Performance and Scale

### Performance Targets

| Scale | Modules | Estimated Time | Notes |
|-------|---------|----------------|-------|
| Small | 1-10 | 30-60 seconds | Single batch |
| Medium | 11-50 | 2-8 minutes | 1-5 batches |
| Large | 51-100 | 8-15 minutes | 6-10 batches |
| Very Large | 100+ | 15+ minutes | 10+ batches, may hit rate limits |

**Batch Size**: 10 agents run concurrently per batch

### Optimization Tips

**For Large Projects (>100 modules)**:
1. Run during low-activity time (fewer API rate limit issues)
2. Consider scoped synthesis first (critical modules only)
3. Use cross-command integration (reuse manifests)
4. Monitor `.sdd/module-manifest.json` or `.sdd/spec-manifest.json` for progress

**For Slow Networks**:
1. Expect longer times (agents fetch tool results over network)
2. Resumability ensures no lost progress
3. Consider running overnight for very large projects

**Parallel Execution**:
- Commands already parallelize internally (batches of 10)
- Do NOT run both commands simultaneously (manifest conflicts)
- Run sequentially: `/synthesize-docs` → `/synthesize-specs` or vice versa

---

## Troubleshooting

### Manifest Corruption

**Symptom**: Command reports "Manifest corrupted"

**Solution**:
```
1. Backup corrupt manifest:
   mv .sdd/module-manifest.json .sdd/module-manifest.json.bak

2. Re-run command (starts fresh discovery)

3. Manually merge completed modules if needed:
   - Check .bak file for "completed" modules
   - Add to new manifest to avoid regenerating
```

---

### Permission Issues

**Symptom**: "Write permission denied"

**Solution**:
```
1. Check .sdd/ directory permissions:
   ls -la .sdd/

2. Fix permissions:
   chmod -R u+w .sdd/

3. Check individual module directories:
   ls -la src/auth/

4. Fix if needed:
   chmod u+w src/auth/
```

---

### Agent Spawn Failures

**Symptom**: Some modules fail with "Agent spawn failure"

**Causes**:
- API rate limits hit
- Network connectivity issues
- Transient service issues

**Solutions**:
1. Wait a few minutes (rate limit cooldown)
2. Re-run command (resumes with failed modules)
3. If persistent, check network connectivity
4. Report issue if reproducible

---

### Cross-Command Manifest Issues

**Symptom**: Command doesn't offer to use other manifest

**Causes**:
- Manifest file missing or corrupted
- Wrong working directory

**Solutions**:
1. Verify both manifests exist:
   - `.sdd/module-manifest.json` (from `/synthesize-docs`)
   - `.sdd/spec-manifest.json` (from `/synthesize-specs`)
2. Check working directory: `pwd`
3. Manually create `.sdd/` if missing: `mkdir -p .sdd`

---

### Unreal Engine Specific Issues

**Symptom**: Unreal modules not detected

**Causes**:
- .uproject file not at root
- Source/ directory doesn't contain *.Build.cs files
- Plugins not in standard Plugins/ location

**Solutions**:
1. Verify .uproject exists: `ls *.uproject`
2. Check Source structure:
   ```
   Source/
   ├── MyProject/
   │   └── MyProject.Build.cs
   ├── MyProjectEditor/
   │   └── MyProjectEditor.Build.cs
   └── ...
   ```
3. Manually specify plugin modules: `/synthesize-docs Plugins/MyPlugin/Source/MyPlugin`

---

## Summary

### Key Takeaways

✅ **Synthesize commands enable large-scale codebase retrofitting** with SDD documentation and specifications

✅ **One-click operation**: Automatic discovery, parallel processing, resumable, safe to re-run

✅ **Two complementary commands**:
- `/synthesize-docs` → CLAUDE.md files (HOW - operational knowledge)
- `/synthesize-specs` → Specification files (WHAT - requirements)

✅ **Framework-agnostic**: TypeScript, Python, Go, Rust, Java, C++, Unreal Engine

✅ **Intelligent features**:
- Drift detection (compare specs vs. implementation)
- Cross-command integration (reuse manifests)
- Hand-edit preservation (CLAUDE.md)
- Evidence-based requirements (traceable to code/tests)

✅ **Performance**: 100 modules in ~10-45 minutes depending on command

✅ **Use cases**:
- Legacy codebase onboarding
- SDD adoption
- Compliance documentation
- Drift detection
- Knowledge preservation

### Quick Reference

**Documentation only**:
```
/synthesize-docs
```

**Specifications only**:
```
/synthesize-specs
```

**Both (documentation first)**:
```
/synthesize-docs
/synthesize-specs    # Uses module manifest
```

**Both (specs first)**:
```
/synthesize-specs
/synthesize-docs     # Uses spec manifest, adds Origin links
```

**Single module**:
```
/synthesize-docs src/auth
/synthesize-specs src/auth
```

---

## Document History

**Version**: 1.0.0
**Created**: 2025-10-21
**Last Updated**: 2025-10-21
**Author**: Spiral Grove Documentation Team
**Status**: Complete

---

**End of Document**
