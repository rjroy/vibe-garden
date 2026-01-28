---
skill: excavate
description: Discover and document the implicit design of an existing codebase
artifact_path: .lore/excavations
---

# Excavate: Design Archaeology for Existing Codebases

## Purpose

Extract the implicit design from an existing codebase. This is the reverse of normal SDD - instead of Spec → Plan → Code, we're doing Code → Inferred Plan → Reconstructed Spec.

Use this when:
- Joining an undocumented project
- Inheriting a legacy codebase
- Needing to understand "what does this system actually do?"
- Preparing for major refactoring

## The Challenge

Large codebases (100+ files, 100k+ LOC) can't be understood in one pass:
- **Features ≠ modules** - A feature might span auth, database, API, and UI
- **Implicit decisions** - The "why" behind patterns isn't in the code
- **Accidental complexity** - Some structure is intentional, some is historical accident
- **Context limits** - Can't load everything into memory

## Approach: Layered Excavation

Excavation happens in **layers**, each building on the previous. Human checkpoints between layers allow correction before investing more effort.

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: SURFACE SURVEY                                        │
│  ├── Directory structure analysis                               │
│  ├── Entry point identification (CLI, API, UI, main)            │
│  ├── Configuration discovery (env, config files)                │
│  ├── Dependency graph (package.json, imports)                   │
│  └── Output: structure.md, entry-points.md                      │
├────────────────────[HUMAN CHECKPOINT]───────────────────────────┤
│  Layer 2: FEATURE EXTRACTION                                    │
│  ├── Trace execution paths from entry points                    │
│  ├── Identify cross-cutting concerns                            │
│  ├── Cluster related files into "feature units"                 │
│  ├── Map feature boundaries (what calls what)                   │
│  └── Output: features.md, feature-map.md                        │
├────────────────────[HUMAN CHECKPOINT]───────────────────────────┤
│  Layer 3: DESIGN INFERENCE                                      │
│  ├── Identify patterns in use (factory, repository, etc.)       │
│  ├── Infer architectural decisions                              │
│  ├── Document apparent constraints                              │
│  ├── Flag inconsistencies and tech debt                         │
│  └── Output: patterns.md, decisions.md, debt.md                 │
├────────────────────[HUMAN CHECKPOINT]───────────────────────────┤
│  Layer 4: DOCUMENTATION GENERATION                              │
│  ├── Generate feature specs (reconstructed)                     │
│  ├── Create architecture overview                               │
│  ├── Document integration points                                │
│  └── Output: .lore/specs/[feature].md (per feature)             │
└─────────────────────────────────────────────────────────────────┘
```

## Invocation

```
/lore-development:excavate
```

The skill is **conversational** - it will:
1. Start with Layer 1 (surface survey)
2. Present findings and ask for confirmation/correction
3. Proceed to next layer only after user approval
4. Allow focusing on specific features or areas

### Optional Parameters

You can focus the excavation:
```
/lore-development:excavate path=src/auth    # Focus on a subdirectory
/lore-development:excavate layer=2          # Resume at specific layer
/lore-development:excavate feature=payment  # Deep dive on known feature
```

## Layer Details

### Layer 1: Surface Survey

**Goal**: Understand the terrain before digging.

**Discovery Methods**:
| Method | What It Finds |
|--------|--------------|
| Directory structure | Package boundaries, module organization |
| File naming patterns | Conventions (*.controller.ts, *.service.ts) |
| Config files | Feature flags, environment variables |
| Package manifests | Dependencies, scripts, entry points |
| README files | Documented intent (often outdated) |
| Git history | Most-changed files, active areas |

**Output**: `.lore/excavations/layer-1-survey.md`

```markdown
# Surface Survey: [Project Name]

## Structure Overview
[Directory tree with annotations]

## Entry Points
| Entry Point | Type | File | Purpose |
|-------------|------|------|---------|
| /api/users | REST | src/routes/users.ts | User management |
| /login | Page | src/pages/login.tsx | Authentication |
| npm start | CLI | src/index.ts | Application bootstrap |

## Configuration
| Config | Location | Purpose |
|--------|----------|---------|
| DATABASE_URL | .env | Database connection |
| src/config.ts | Code | Application settings |

## Dependencies (key)
[Significant dependencies with notes]

## Git Insights
- Most active areas: [list]
- Recent major changes: [list]

## Initial Observations
[Notable patterns, anomalies, or questions]
```

### Layer 2: Feature Extraction

**Goal**: Identify what this system *does* (not how it's organized).

**Discovery Methods**:
| Method | What It Finds |
|--------|--------------|
| Entry point tracing | Execution paths through the system |
| Import graph analysis | What depends on what |
| Test organization | What developers considered "units" |
| Route/handler mapping | User-facing capabilities |
| Event/message patterns | Async feature boundaries |

**The Core Insight**: A "feature" is defined by:
- User-facing capability (what they can do)
- Data it operates on
- Entry points that trigger it
- Components that implement it

**Output**: `.lore/excavations/layer-2-features.md`

```markdown
# Feature Extraction: [Project Name]

## Discovered Features

### Feature: User Authentication
**Capability**: Users can register, login, logout, reset password
**Entry Points**:
  - POST /api/auth/register
  - POST /api/auth/login
  - POST /api/auth/logout
  - POST /api/auth/reset-password
**Files Involved**:
  - src/routes/auth.ts (routes)
  - src/services/auth-service.ts (business logic)
  - src/models/user.ts (data model)
  - src/middleware/auth.ts (session handling)
  - src/utils/password.ts (hashing)
**Data**: users table, sessions table
**Dependencies**: bcrypt, jsonwebtoken
**Cross-cuts**: Logging, error handling

### Feature: Shopping Cart
[...]

## Feature Dependency Map
[Mermaid diagram or ASCII showing feature relationships]

## Cross-Cutting Concerns
| Concern | Implementation | Used By |
|---------|---------------|---------|
| Logging | src/utils/logger.ts | All features |
| Error Handling | src/middleware/errors.ts | All routes |
| Caching | src/utils/cache.ts | Product queries |

## Uncertain Areas
[Code that doesn't clearly belong to any feature]
```

### Layer 3: Design Inference

**Goal**: Understand *why* the system is built this way.

**This is the hardest layer.** Code shows WHAT, not WHY. We must:
- Identify patterns and infer intent
- Look for comments explaining decisions
- Check commit messages for context
- Make educated guesses (clearly labeled)

**Output**: `.lore/excavations/layer-3-design.md`

```markdown
# Design Inference: [Project Name]

## Architectural Patterns

### Pattern: Repository + Service Layers
**Evidence**:
  - All database access through *Repository classes
  - Business logic in *Service classes
  - Controllers only handle HTTP concerns
**Inferred Intent**: Separation of concerns, testability
**Consistency**: 8/10 files follow pattern, 2 exceptions noted

### Pattern: Event-Driven Updates
**Evidence**:
  - EventEmitter usage in order processing
  - Subscriber patterns for notifications
**Inferred Intent**: Decoupling, async processing
**Consistency**: Partially adopted (orders only)

## Key Design Decisions (Inferred)

### Decision: PostgreSQL over MongoDB
**Evidence**: pg dependency, SQL migrations folder
**Possible Rationale**:
  - Relational data model (users, orders, products)
  - ACID transactions for payments
**Confidence**: Medium (no documentation found)

### Decision: JWT for Authentication
**Evidence**: jsonwebtoken in auth service
**Possible Rationale**: Stateless API, microservice readiness
**Trade-offs**:
  - Pro: No session store needed
  - Con: Can't revoke tokens immediately
**Confidence**: High (common pattern)

## Technical Debt Identified

### Debt: Inconsistent Error Handling
**Location**: Various controllers
**Issue**: Some throw, some return error objects
**Impact**: Unpredictable API responses
**Suggested Fix**: Standardize on middleware error handler

### Debt: Hardcoded Configuration
**Location**: src/services/email-service.ts
**Issue**: SMTP settings in code, not config
**Impact**: Can't change without deployment

## Questions for Team
[Things that couldn't be inferred from code]
```

### Layer 4: Documentation Generation

**Goal**: Produce the specs/docs that *should* have existed.

After human review of layers 1-3, generate:
- Feature specifications (reconstructed)
- Architecture overview
- Integration documentation

**Output**:
- `.lore/specs/[feature].md` (per feature)
- `.lore/architecture.md` (system overview)

These become living documents that can be updated going forward.

## Implementation Strategy

### For Large Codebases (100+ files)

1. **Don't read everything** - Use sampling and heuristics
2. **Start from edges** - Entry points tell you what matters
3. **Follow the data** - Data models reveal feature boundaries
4. **Trust git history** - Recently changed = currently relevant
5. **Iterate** - Make a pass, refine, make another pass

### Execution

Layer 1 uses an exploration agent internally:
- Directory scanning with Glob
- Dependency analysis
- Git history analysis
- Config file reading

Layers 2-4 are more interactive:
- User provides domain knowledge
- Skill synthesizes with code analysis
- Checkpoints allow correction

## Artifact Structure

```
.lore/
├── excavations/
│   ├── layer-1-survey.md       # Surface survey results
│   ├── layer-2-features.md     # Feature extraction
│   ├── layer-3-design.md       # Design inference
│   └── sessions/
│       └── 2025-01-28.md       # Session transcript/notes
├── specs/                      # Generated specs (same as forward SDD)
│   ├── authentication.md
│   ├── shopping-cart.md
│   └── [feature].md
└── architecture.md             # Generated architecture overview
```

## Limitations

**What this skill CAN do**:
- Discover structure and patterns
- Identify features from entry points
- Infer likely design decisions
- Generate documentation scaffolding

**What this skill CANNOT do**:
- Know the original intent with certainty
- Understand business context you don't provide
- Distinguish intentional patterns from accidents
- Find features with no entry points (dead code)

## Example Session

```
User: /lore-development:excavate