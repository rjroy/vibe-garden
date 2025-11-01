# CLAUDE.md Format Specification

**Version**: 1.0.0
**Created**: 2025-10-20
**Purpose**: Defines the structure and constraints for module-level CLAUDE.md documentation files

## Overview

CLAUDE.md files provide concise, operational documentation for code modules. These files are designed to be loaded into Claude's context during maintenance work, providing just enough information to understand a module's purpose, structure, and usage patterns without overwhelming the context window.

## Design Principles

1. **Conciseness**: Maximum 400 lines per module CLAUDE.md (≈2K tokens, stays within 5% of 200K context budget when loading 5 files)
2. **Operational Focus**: Emphasize WHAT and HOW (implementation details), not WHY (that's in specs)
3. **Maintenance-Oriented**: Written for developers who need to modify, debug, or extend existing code
4. **Hand-Edit Friendly**: Support user customization via marked sections that survive regeneration
5. **Hierarchical**: Root CLAUDE.md for project overview, module CLAUDE.md for details

## File Types

### Root CLAUDE.md

Located at project root (`./CLAUDE.md`), provides project-wide context.

**Purpose**: Orient Claude to the entire codebase structure and conventions.

**Required Sections**:
- **Repository Overview**: 2-3 sentence project description
- **Repository Structure**: Directory tree with annotations
- **Module Index**: List of modules with brief descriptions and links to module CLAUDE.md files
- **Development Workflow**: How to build, test, and contribute
- **Common Commands**: Frequently used commands (slash commands, npm scripts, etc.)
- **Document Conventions**: File naming, cross-references, status values

**Optional Sections**:
- Key Principles (if project has specific design philosophy)
- Anti-Patterns to Avoid
- Research Integration (if applicable)

**Size Constraint**: No strict limit (typically 200-600 lines for large projects)

**Origin Field**: Not typically included (root CLAUDE.md documents the project, not derived from a single spec)

### Module CLAUDE.md

Located in module directory (e.g., `src/auth/CLAUDE.md`), provides module-specific context.

**Purpose**: Document a single logical module's implementation for maintenance work.

**Required Sections**:

```markdown
# [Module Name]

**Origin**: Implemented from .sdd/specs/[feature-name].md
**Last Generated**: [ISO 8601 timestamp]

## Purpose

[1-2 sentences: What this module does and why it exists]

## Key Components

[List of main files, classes, functions with brief descriptions]

- `file.ts`: [Purpose]
  - `function()`: [What it does]
  - `class Name`: [Responsibilities]

## Public API

[Exported interfaces that other modules use]

- Functions: `export function foo()`
- Types: `export interface Bar`
- Constants: `export const CONFIG`

## Integration Points

[How this module connects to the rest of the system]

- **Dependencies**: Modules this depends on
- **Dependents**: Modules that depend on this
- **External APIs**: Third-party services used
- **Events**: Events emitted or consumed

## Common Operations

[Typical usage patterns and workflows]

### [Operation Name]

[Step-by-step description or code snippet]

## Testing

[How to test this module]

- **Test files**: Location and organization
- **Test commands**: How to run tests
- **Key test scenarios**: What's tested
- **Mocking**: How to mock dependencies

<!-- BEGIN: HAND-EDITED -->
[User can add custom content here that survives regeneration]
<!-- END: HAND-EDITED -->
```

**Size Constraint**: ≤ 400 lines (hard limit, enforced by agent validation)

**Origin Field**: `**Origin**: Implemented from .sdd/specs/[feature-name].md` (added during SDD integration phase)

## Hand-Edited Sections

### Purpose

Allow users to add custom documentation that survives regeneration when code changes.

### Marker Syntax

Hand-edited sections are delimited by HTML comment markers:

```markdown
<!-- BEGIN: HAND-EDITED -->
[User content here - preserved during regeneration]
<!-- END: HAND-EDITED -->
```

### Rules

1. **Markers must appear on their own lines** (no surrounding text)
2. **Only ONE hand-edited section per file** (for simplicity)
3. **Markers are optional** - if absent, entire file regenerated
4. **Nested markers forbidden** - will cause validation error
5. **Unpaired markers forbidden** - must have matching BEGIN/END

### Placement

Typically placed at end of file, but can be anywhere. Recommended location:

```markdown
## Testing

[Generated testing documentation]

<!-- BEGIN: HAND-EDITED -->
## Common Gotchas

- Issue 1: [User documents known issues]
- Workaround: [User documents workarounds]

## Performance Notes

[User adds performance observations]
<!-- END: HAND-EDITED -->
```

### Regeneration Behavior

When `module-doc-synthesizer` agent regenerates CLAUDE.md:

1. Agent reads existing CLAUDE.md
2. Extracts content between `<!-- BEGIN: HAND-EDITED -->` and `<!-- END: HAND-EDITED -->`
3. Generates new documentation for all standard sections
4. Inserts preserved hand-edited content at same location
5. Writes updated CLAUDE.md to disk

**Preservation Guarantee**: Content between markers is NEVER modified by agent, even if code changes drastically.

### Validation

Agent validates markers before preservation:

- **Missing END marker**: Error (regenerate without preservation)
- **Nested markers**: Error (abort regeneration)
- **Multiple BEGIN markers**: Error (abort regeneration)
- **Markers with surrounding text**: Warning (may not preserve correctly)

### Example

**Before Regeneration**:
```markdown
## Testing

Run tests with `npm test`.

<!-- BEGIN: HAND-EDITED -->
## Known Issues

- Auth tokens expire after 1 hour (see issue #42)
- Rate limiting kicks in after 100 requests/minute
<!-- END: HAND-EDITED -->
```

**After Code Change + Regeneration**:
```markdown
## Testing

Run tests with `npm test`. New test suite added for error handling.

<!-- BEGIN: HAND-EDITED -->
## Known Issues

- Auth tokens expire after 1 hour (see issue #42)
- Rate limiting kicks in after 100 requests/minute
<!-- END: HAND-EDITED -->
```

Hand-edited content preserved exactly, testing section updated.

## Origin Field Format

The **Origin** field links module documentation back to its originating specification.

### Syntax

```markdown
**Origin**: Implemented from .sdd/specs/[feature-name].md
```

### Placement

Second line of module CLAUDE.md, immediately after module title:

```markdown
# Authentication Module

**Origin**: Implemented from .sdd/specs/authentication.md
**Last Generated**: 2025-10-20T14:30:00Z

## Purpose
...
```

### SDD Integration

The Origin field is added during **Phase 3 (SDD Integration)** of `/spiral-grove:synthesize-docs`:

1. Agent generates CLAUDE.md without Origin field
2. Command analyzes module path and matches to spec file (fuzzy matching)
3. If match found, command inserts Origin field after title
4. If no match, command skips Origin field (module may not have spec, e.g., utility modules)

### Hierarchical Specs

For parent/child spec hierarchies:

- **Parent spec**: `authentication.md`
- **Child specs**: `authentication/oauth-flow.md`, `authentication/token-refresh.md`

Module CLAUDE.md links to child spec if applicable:

```markdown
**Origin**: Implemented from .sdd/specs/authentication/oauth-flow.md
```

### Purpose

1. **Traceability**: Developers can find the original spec for a module
2. **Spec-Code Linkage**: Enables `/spiral-grove:review spec-vs-code` to detect drift
3. **Context Restoration**: When modifying code, developers can load the spec for decision rationale

## Line Count Constraint

### Limit

**400 lines maximum** per module CLAUDE.md.

### Rationale

- 400 lines ≈ 2,000 tokens
- Loading 5 module CLAUDE.md files = 10,000 tokens (5% of 200K context budget)
- Keeps context efficient for maintenance work

### Enforcement

The `module-doc-synthesizer` agent validates line count after generation:

1. Generate CLAUDE.md content
2. Count lines (including blank lines, markers, comments)
3. If ≤ 400: Write to disk
4. If > 400: Apply condensing strategies (see below)

### Condensing Strategies

If initial generation exceeds 400 lines, agent applies these strategies in order:

1. **Remove redundant examples**: Keep 1-2 most representative examples per section
2. **Shorten component descriptions**: Reduce to 1 sentence per component
3. **Collapse similar sections**: Merge related subsections
4. **Move extensive snippets to hand-edited prompt**: Suggest user add details manually

After applying strategies, retry validation **once**. If still > 400 lines:

- Return CLAUDE.md with warning message to user
- Suggest splitting module into smaller submodules
- Write file anyway (user can manually condense)

### Counting Rules

- **Blank lines**: Counted
- **Comments**: Counted (including `<!-- -->` markers)
- **YAML frontmatter**: Not used in module CLAUDE.md (root only if needed)
- **Code blocks**: Counted (including ` ``` ` delimiters)

### Example Violation

```markdown
# Large Module (Initial Generation: 450 lines)

[Condensing applied]

# Large Module (After Condensing: 395 lines)

✅ Within limit, saved successfully.
```

## Templates

### Module CLAUDE.md Template

```markdown
# [Module Name]

**Origin**: Implemented from .sdd/specs/[feature-name].md
**Last Generated**: [ISO 8601 timestamp]

## Purpose

[1-2 sentences describing module's role in the system]

## Key Components

### [File or Component Name]

- **Purpose**: [Brief description]
- **Key Functions/Classes**:
  - `functionName()`: [What it does]
  - `ClassName`: [Responsibilities]

## Public API

**Exported Functions**:
- `export function foo(arg: Type): ReturnType` - [Description]

**Exported Types**:
- `export interface Bar` - [Description]

**Constants**:
- `export const CONFIG` - [Description]

## Integration Points

**Dependencies** (modules this depends on):
- `../utils/logger`: Logging functionality
- `../db/connection`: Database access

**Dependents** (modules that use this):
- `../api/routes`: Uses this module's exported functions

**External APIs**:
- Gmail API: Used for email retrieval

**Events**:
- Emits: `user.authenticated` when login succeeds
- Consumes: `config.updated` to refresh settings

## Common Operations

### [Operation Name]

**Purpose**: [What this operation accomplishes]

**Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Example**:
\`\`\`typescript
// Example code snippet
\`\`\`

## Testing

**Test Files**:
- `tests/[module].test.ts`: Unit tests
- `tests/integration/[module].integration.test.ts`: Integration tests

**Run Tests**:
\`\`\`bash
npm test [module]
\`\`\`

**Key Scenarios**:
- [Scenario 1]: Tests [behavior]
- [Scenario 2]: Tests [edge case]

**Mocking**:
- [Dependency]: Mocked using [approach]

<!-- BEGIN: HAND-EDITED -->
<!-- Users can add custom sections here -->
<!-- END: HAND-EDITED -->
```

### Root CLAUDE.md Template

```markdown
# [Project Name]

[2-3 sentence project description and purpose]

## Repository Overview

- **Purpose**: [High-level purpose]
- **Key Features**: [3-5 bullet points]
- **Tech Stack**: [Languages, frameworks, tools]

## Repository Structure

\`\`\`
project/
├── .sdd/                       # SDD artifacts (specs, plans, tasks, progress)
│   ├── specs/                  # Feature specifications
│   ├── plans/                  # Technical plans
│   ├── tasks/                  # Task breakdowns
│   └── progress/               # Implementation progress
├── src/                        # Source code
│   ├── module-a/               # Module A
│   │   └── CLAUDE.md           # Module documentation
│   └── module-b/               # Module B
│       └── CLAUDE.md           # Module documentation
├── tests/                      # Test files
├── docs/                       # Additional documentation
└── CLAUDE.md                   # This file (root documentation)
\`\`\`

## Module Index

| Module | Location | Description | Docs |
|--------|----------|-------------|------|
| Module A | `src/module-a/` | [Brief description] | [CLAUDE.md](src/module-a/CLAUDE.md) |
| Module B | `src/module-b/` | [Brief description] | [CLAUDE.md](src/module-b/CLAUDE.md) |

## Development Workflow

**Build**:
\`\`\`bash
[build command]
\`\`\`

**Test**:
\`\`\`bash
[test command]
\`\`\`

**Run**:
\`\`\`bash
[run command]
\`\`\`

## Common Commands

- `/spec-writing`: Create feature specification
- `/plan-generation`: Create technical plan
- `/task-breakdown`: Break down into tasks
- `/implementation`: Execute tasks with tracking

## Document Conventions

**File Naming**:
- Specs: `[feature-name].md`
- Plans: `[feature-name]-plan.md`
- Tasks: `[feature-name]-tasks.md`

**Status Values**:
- Specs: Draft | Under Review | Approved | Superseded
- Plans: Draft | Under Review | Approved | Updated
- Tasks: Draft | Ready for Implementation | In Progress | Complete

## Key Principles

[Optional: Project-specific design principles]

## Notes

[Optional: Important context for developers]
```

## Constraints and Validation

### Valid Markdown

All CLAUDE.md files must be valid CommonMark markdown:

- Proper heading hierarchy (no skipped levels: `# H1` → `### H3` is invalid)
- Balanced code fences (` ``` ` must have closing ` ``` `)
- Valid link syntax `[text](url)`
- Proper list indentation

Agents should validate output before writing to disk.

### No Duplicate Sections

CLAUDE.md files must not contain duplicate section headings at the same level.

**Invalid**:
```markdown
## Testing
[Content]

## Common Operations
[Content]

## Testing
[Duplicate heading - INVALID]
```

Agents should detect duplicates during merging of hand-edited sections.

### Line Count Enforcement

Module CLAUDE.md files exceeding 400 lines trigger condensing logic (see Line Count Constraint section).

### Marker Validation

Hand-edited section markers must follow strict rules (see Hand-Edited Sections section).

## Example CLAUDE.md Files

### Example 1: Small Utility Module (150 lines)

```markdown
# String Utilities

**Origin**: Implemented from .sdd/specs/utility-libraries.md
**Last Generated**: 2025-10-20T10:00:00Z

## Purpose

Provides common string manipulation functions used across the application for formatting, validation, and sanitization.

## Key Components

### `src/utils/string.ts`

- **Purpose**: Core string utility functions
- **Key Functions**:
  - `sanitize()`: Removes special characters for safe display
  - `formatCurrency()`: Formats numbers as currency strings
  - `truncate()`: Truncates strings with ellipsis

## Public API

**Exported Functions**:
- `export function sanitize(input: string): string` - Sanitizes user input
- `export function formatCurrency(amount: number, locale: string): string` - Formats currency
- `export function truncate(text: string, maxLength: number): string` - Truncates text

## Integration Points

**Dependencies**:
- `lodash`: Used for `_.escape()` in sanitization

**Dependents**:
- `../ui/components`: Uses `formatCurrency()` and `truncate()`
- `../api/validation`: Uses `sanitize()` for input validation

**External APIs**: None

## Common Operations

### Sanitizing User Input

**Purpose**: Remove special characters before displaying user-generated content.

**Example**:
\`\`\`typescript
import { sanitize } from '../utils/string';

const userInput = '<script>alert("XSS")</script>';
const safe = sanitize(userInput); // '&lt;script&gt;alert("XSS")&lt;/script&gt;'
\`\`\`

### Formatting Currency

**Purpose**: Display monetary amounts in locale-specific format.

**Example**:
\`\`\`typescript
import { formatCurrency } from '../utils/string';

const amount = 1234.56;
const formatted = formatCurrency(amount, 'en-US'); // '$1,234.56'
\`\`\`

## Testing

**Test Files**:
- `tests/utils/string.test.ts`: 15 unit tests

**Run Tests**:
\`\`\`bash
npm test string
\`\`\`

**Key Scenarios**:
- Sanitization: Tests HTML, SQL injection, script tags
- Currency: Tests multiple locales (US, EU, JP)
- Truncation: Tests edge cases (empty string, exact length, unicode)

**Mocking**: No external dependencies to mock
```

### Example 2: Complex Module with Hand-Edited Section (380 lines)

```markdown
# Authentication Module

**Origin**: Implemented from .sdd/specs/authentication.md
**Last Generated**: 2025-10-20T14:30:00Z

## Purpose

Handles user authentication via OAuth 2.0, session management, and token refresh. Integrates with Google OAuth for user login and maintains session state using Redis.

## Key Components

### `src/auth/oauth.ts`

- **Purpose**: OAuth 2.0 flow implementation
- **Key Functions**:
  - `initiateOAuthFlow()`: Starts OAuth flow, redirects to provider
  - `handleOAuthCallback()`: Processes callback, exchanges code for token
  - `refreshToken()`: Refreshes expired access tokens

**Classes**:
- `OAuthProvider`: Abstract base class for OAuth providers
- `GoogleOAuthProvider`: Google-specific OAuth implementation

### `src/auth/session.ts`

- **Purpose**: Session storage and retrieval
- **Key Functions**:
  - `createSession()`: Creates new session in Redis
  - `getSession()`: Retrieves session by ID
  - `invalidateSession()`: Logs user out

**Classes**:
- `SessionManager`: Handles all session operations

### `src/auth/middleware.ts`

- **Purpose**: Express middleware for route protection
- **Key Functions**:
  - `requireAuth()`: Middleware to protect routes
  - `extractUserFromSession()`: Retrieves user object from session

## Public API

**Exported Functions**:
- `export async function initiateOAuthFlow(provider: string): Promise<string>` - Returns OAuth URL
- `export async function handleOAuthCallback(code: string): Promise<User>` - Exchanges code for user
- `export async function refreshToken(userId: string): Promise<void>` - Refreshes tokens
- `export function requireAuth(): RequestHandler` - Express middleware

**Exported Types**:
- `export interface User` - User object structure
- `export interface Session` - Session structure
- `export interface OAuthConfig` - OAuth configuration

**Constants**:
- `export const OAUTH_SCOPES` - Required OAuth scopes

## Integration Points

**Dependencies**:
- `../utils/logger`: Logging authentication events
- `../db/redis`: Session storage
- `google-auth-library`: Google OAuth client

**Dependents**:
- `../api/routes`: Uses `requireAuth()` middleware
- `../ui/login`: Calls `initiateOAuthFlow()`

**External APIs**:
- Google OAuth 2.0 API: User authentication
- Redis: Session storage (localhost:6379)

**Events**:
- Emits: `user.login` when authentication succeeds
- Emits: `user.logout` when session invalidated
- Emits: `token.refreshed` when token refreshed

## Common Operations

### Logging in a User

**Purpose**: Authenticate user via Google OAuth.

**Steps**:
1. User clicks "Login with Google"
2. Frontend calls `initiateOAuthFlow('google')`
3. User redirected to Google consent screen
4. Google redirects back with authorization code
5. Backend calls `handleOAuthCallback(code)`
6. Session created and returned to frontend

**Example**:
\`\`\`typescript
// Frontend initiates login
const oauthUrl = await initiateOAuthFlow('google');
window.location.href = oauthUrl;

// Backend handles callback
app.get('/auth/callback', async (req, res) => {
  const user = await handleOAuthCallback(req.query.code);
  req.session.userId = user.id;
  res.redirect('/dashboard');
});
\`\`\`

### Protecting Routes

**Purpose**: Ensure only authenticated users can access certain routes.

**Example**:
\`\`\`typescript
import { requireAuth } from '../auth/middleware';

app.get('/api/protected', requireAuth(), (req, res) => {
  // req.user is available here
  res.json({ message: 'Authenticated!' });
});
\`\`\`

### Token Refresh

**Purpose**: Refresh expired access tokens automatically.

**Steps**:
1. Middleware detects expired token (401 from Google API)
2. Calls `refreshToken(userId)`
3. New token stored in session
4. Original request retried with new token

## Testing

**Test Files**:
- `tests/auth/oauth.test.ts`: OAuth flow tests (12 tests)
- `tests/auth/session.test.ts`: Session management tests (8 tests)
- `tests/auth/middleware.test.ts`: Middleware tests (5 tests)
- `tests/integration/auth.integration.test.ts`: E2E auth flow (3 tests)

**Run Tests**:
\`\`\`bash
npm test auth
\`\`\`

**Key Scenarios**:
- OAuth flow: Tests successful login, invalid code, network errors
- Session management: Tests creation, retrieval, expiration, invalidation
- Middleware: Tests protected routes, missing session, expired session
- Token refresh: Tests automatic refresh, refresh failure

**Mocking**:
- Google OAuth API: Mocked using `nock` to simulate OAuth responses
- Redis: Mocked using `redis-mock` for unit tests
- Real Redis used in integration tests

<!-- BEGIN: HAND-EDITED -->
## Known Issues

- **Token Refresh Race Condition**: If multiple requests trigger token refresh simultaneously, some may fail with 401. Workaround: Retry failed requests once.
  - Tracking: Issue #127
  - Fix planned for v2.1.0

- **Session Cleanup**: Sessions are not automatically cleaned up from Redis after expiration. Manual cleanup required.
  - Workaround: Run `npm run cleanup-sessions` weekly
  - Tracking: Issue #142

## Performance Notes

- OAuth flow typically takes 2-3 seconds (includes redirect to Google)
- Session retrieval from Redis: <10ms (local) or <50ms (remote Redis)
- Token refresh: 500-1000ms (network call to Google)

## Debugging Tips

- Enable DEBUG logging: `DEBUG=auth:* npm start`
- Check Redis session keys: `redis-cli KEYS 'session:*'`
- Inspect OAuth tokens: `node scripts/decode-jwt.js <token>`
<!-- END: HAND-EDITED -->
```

## Usage by Components

### Module Documentation Synthesizer Agent

The agent uses this spec to:

1. **Generate structure**: Follow template for consistent output
2. **Validate constraints**: Enforce 400-line limit, valid markdown
3. **Preserve hand-edits**: Extract/merge content between markers
4. **Add Origin field**: Insert spec reference (during SDD integration)

### Synthesize-Docs Command

The command uses this spec to:

1. **Orchestrate agents**: Spawn multiple `module-doc-synthesizer` agents in parallel
2. **Validate outputs**: Ensure all generated CLAUDE.md files conform to spec
3. **Add Origin fields**: Match modules to specs and insert references

### Review Command (spec-vs-code mode)

The review extension uses this spec to:

1. **Parse CLAUDE.md**: Extract Origin field to find linked spec
2. **Validate linkage**: Ensure spec file exists and is accessible
3. **Report drift**: Compare spec acceptance criteria to implementation

## Versioning

This format specification follows semantic versioning:

- **Major version**: Breaking changes to required sections or marker syntax
- **Minor version**: New optional sections or non-breaking additions
- **Patch version**: Clarifications, examples, typo fixes

**Current Version**: 1.0.0 (initial release)

## References

- **Parent Spec**: `.sdd/specs/spiral-grove/documentation-synthesis.md`
- **Plan**: `.sdd/plans/spiral-grove/documentation-synthesis-plan.md`
- **Agent Implementation**: `spiral-grove/agents/module-doc-synthesizer.md` (to be created)
- **Command Implementation**: `spiral-grove/commands/synthesize-docs.md` (to be created)
