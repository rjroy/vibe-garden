# Module Manifest Schema

**Version**: 1.0.0
**Created**: 2025-10-20
**Purpose**: Defines the structure of `.sdd/module-manifest.json` for stateful documentation synthesis resumability

## Overview

The module manifest is a JSON file created by `/spiral-grove:synthesize-docs` that tracks the state of documentation generation across all modules in a project. It enables:

1. **Resumability**: Continue generation from where it left off after interruption
2. **Idempotency**: Re-running the command safely regenerates only pending/failed modules
3. **Status Tracking**: Monitor progress during long-running generation tasks
4. **Error Reporting**: Capture errors for failed module generations

## File Location

`.sdd/module-manifest.json` (at project root)

## JSON Schema

### Root Object

```json
{
  "generated_at": "2025-10-20T14:30:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "claude_md_path": "src/auth/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/api",
      "status": "pending",
      "claude_md_path": "src/api/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/utils",
      "status": "failed",
      "claude_md_path": "src/utils/CLAUDE.md",
      "error": "Module has no source files"
    }
  ]
}
```

### Field Descriptions

#### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `generated_at` | string (ISO 8601) | Yes | Timestamp when manifest was created or last updated |
| `project_root` | string | Yes | Absolute path to project root directory (for validation) |
| `modules` | array | Yes | Array of module entries (see ModuleEntry schema below) |

#### ModuleEntry Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `path` | string | Yes | Relative path to module directory from project root |
| `status` | enum | Yes | Generation status: `"pending"`, `"completed"`, or `"failed"` |
| `claude_md_path` | string | Yes | Relative path to CLAUDE.md file (e.g., `"src/auth/CLAUDE.md"`) |
| `error` | string \| null | No | Error message if status is `"failed"`, otherwise `null` |

#### Status Enum Values

| Value | Meaning | Next Action |
|-------|---------|-------------|
| `"pending"` | Documentation not yet generated | Generate documentation on next run |
| `"completed"` | Documentation successfully generated | Skip on next run (unless user requests regeneration) |
| `"failed"` | Generation failed with error | Retry on next run |

### Validation Rules

1. **Unique Paths**: No two modules can have the same `path` value
2. **Valid Status**: `status` must be one of: `"pending"`, `"completed"`, `"failed"`
3. **Error Consistency**: If `status` is `"failed"`, `error` must be a non-empty string; otherwise `error` should be `null`
4. **Path Format**: Paths must be relative (not absolute), use forward slashes (`/`), and not start with `/` or `./`
5. **Timestamp Format**: `generated_at` must be valid ISO 8601 format
6. **Project Root**: `project_root` should be an absolute path

## Example Manifests

### Example 1: Initial Generation (All Pending)

```json
{
  "generated_at": "2025-10-20T10:00:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "pending",
      "claude_md_path": "src/auth/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/api",
      "status": "pending",
      "claude_md_path": "src/api/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/db",
      "status": "pending",
      "claude_md_path": "src/db/CLAUDE.md",
      "error": null
    }
  ]
}
```

### Example 2: Partial Progress (Mixed States)

```json
{
  "generated_at": "2025-10-20T10:15:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "claude_md_path": "src/auth/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "claude_md_path": "src/api/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/db",
      "status": "failed",
      "claude_md_path": "src/db/CLAUDE.md",
      "error": "No source files found in module directory"
    },
    {
      "path": "src/utils",
      "status": "pending",
      "claude_md_path": "src/utils/CLAUDE.md",
      "error": null
    }
  ]
}
```

### Example 3: Fully Complete

```json
{
  "generated_at": "2025-10-20T10:30:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "claude_md_path": "src/auth/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "claude_md_path": "src/api/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/db",
      "status": "completed",
      "claude_md_path": "src/db/CLAUDE.md",
      "error": null
    },
    {
      "path": "src/utils",
      "status": "completed",
      "claude_md_path": "src/utils/CLAUDE.md",
      "error": null
    }
  ]
}
```

## Lifecycle

### 1. Manifest Creation (Phase 1: Module Discovery)

When `/spiral-grove:synthesize-docs` runs for the first time:

1. Command detects logical module boundaries using heuristics
2. Presents detected module list to user for approval/modification
3. Creates `.sdd/module-manifest.json` with all modules in `"pending"` status
4. Saves manifest to disk

**Initial State**: All modules `"pending"`, `error` is `null`

### 2. Documentation Generation (Phase 2: Parallel Generation)

Command processes modules in parallel:

1. Reads manifest to get list of `"pending"` and `"failed"` modules
2. Spawns `module-doc-synthesizer` agents for each module (parallel execution)
3. As each agent completes:
   - **Success**: Update module status to `"completed"`
   - **Failure**: Update module status to `"failed"`, set `error` message
4. Updates `generated_at` timestamp after each batch

**During Generation**: Mix of `"pending"`, `"completed"`, and `"failed"`

### 3. Resumability (Interrupted Generation)

If generation is interrupted (timeout, user cancellation, system crash):

1. Manifest preserves state (some `"completed"`, some `"pending"`)
2. User re-runs `/spiral-grove:synthesize-docs`
3. Command reads manifest and detects partial completion
4. Prompts user: "Continue from where we left off? (X modules remaining)"
5. On approval: Processes only `"pending"` and `"failed"` modules
6. Updates manifest as generation progresses

**After Resumption**: More modules marked `"completed"`, fewer `"pending"`

### 4. Idempotent Re-runs (Full Regeneration)

If user wants to regenerate all documentation:

1. User runs `/spiral-grove:synthesize-docs` on fully completed project
2. Command detects all modules are `"completed"`
3. Prompts user: "All documentation already generated. Regenerate all modules?"
4. On approval: Resets all statuses to `"pending"` and regenerates
5. Existing CLAUDE.md files updated (hand-edited sections preserved)

**After Regeneration**: All modules `"completed"` with updated timestamps

### 5. Incremental Updates (New Modules Added)

If project evolves and new modules are added:

1. User runs `/spiral-grove:synthesize-docs` again
2. Command detects new modules not in manifest
3. Prompts user: "Found 3 new modules. Add to manifest and generate?"
4. On approval: Adds new modules with `"pending"` status
5. Generates documentation for new modules only

**After Incremental Update**: Existing modules unchanged, new modules `"completed"`

## Usage by Components

### Synthesize-Docs Command (Phase 1: Module Discovery)

```typescript
// Pseudocode for manifest creation

const detectedModules = detectModuleBoundaries(projectRoot);
const userApprovedModules = await promptUserForApproval(detectedModules);

const manifest = {
  generated_at: new Date().toISOString(),
  project_root: process.cwd(),
  modules: userApprovedModules.map(module => ({
    path: module.path,
    status: "pending",
    claude_md_path: `${module.path}/CLAUDE.md`,
    error: null
  }))
};

fs.writeFileSync('.sdd/module-manifest.json', JSON.stringify(manifest, null, 2));
```

### Synthesize-Docs Command (Phase 2: Parallel Generation)

```typescript
// Pseudocode for documentation generation

const manifest = JSON.parse(fs.readFileSync('.sdd/module-manifest.json'));

const pendingModules = manifest.modules.filter(m =>
  m.status === "pending" || m.status === "failed"
);

// Spawn agents in parallel
const results = await Promise.allSettled(
  pendingModules.map(module => spawnModuleDocAgent(module.path))
);

// Update manifest based on results
results.forEach((result, index) => {
  const module = pendingModules[index];
  const manifestIndex = manifest.modules.findIndex(m => m.path === module.path);

  if (result.status === "fulfilled") {
    manifest.modules[manifestIndex].status = "completed";
    manifest.modules[manifestIndex].error = null;
  } else {
    manifest.modules[manifestIndex].status = "failed";
    manifest.modules[manifestIndex].error = result.reason.message;
  }
});

manifest.generated_at = new Date().toISOString();
fs.writeFileSync('.sdd/module-manifest.json', JSON.stringify(manifest, null, 2));
```

### Synthesize-Docs Command (Resumability Check)

```typescript
// Pseudocode for resumability check

const manifestPath = '.sdd/module-manifest.json';

if (fs.existsSync(manifestPath)) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath));

  const completedCount = manifest.modules.filter(m => m.status === "completed").length;
  const pendingCount = manifest.modules.filter(m => m.status === "pending").length;
  const failedCount = manifest.modules.filter(m => m.status === "failed").length;

  if (completedCount === manifest.modules.length) {
    const shouldRegenerate = await promptUser(
      "All documentation already generated. Regenerate all modules?"
    );
    if (shouldRegenerate) {
      manifest.modules.forEach(m => {
        m.status = "pending";
        m.error = null;
      });
    }
  } else {
    const shouldResume = await promptUser(
      `Continue from where we left off? (${pendingCount + failedCount} modules remaining)`
    );
    if (!shouldResume) {
      // User wants fresh start
      manifest.modules.forEach(m => {
        m.status = "pending";
        m.error = null;
      });
    }
  }

  // Save updated manifest
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
} else {
  // First run - create new manifest
  await createNewManifest();
}
```

## Error Handling

### Common Error Messages

| Error Message | Cause | Resolution |
|---------------|-------|------------|
| `"No source files found in module directory"` | Module directory exists but contains no .ts, .js, .py, etc. files | Check module path, may be an empty directory |
| `"Module exceeded 400-line limit after condensing"` | Generated CLAUDE.md too large even after applying condensing strategies | Split module into smaller submodules |
| `"Invalid markdown generated (unbalanced code fences)"` | Agent generated malformed markdown | Agent bug - report issue |
| `"Hand-edited markers malformed (nested or unpaired)"` | Existing CLAUDE.md has invalid hand-edit markers | Manually fix markers or remove them |
| `"Permission denied writing to [path]"` | Filesystem permission issue | Check directory permissions |

### Error Field Format

```json
{
  "path": "src/broken-module",
  "status": "failed",
  "claude_md_path": "src/broken-module/CLAUDE.md",
  "error": "No source files found in module directory"
}
```

Error messages should be:
- **Concise**: 1-2 sentences
- **Actionable**: Describe how to fix the issue
- **User-friendly**: Avoid technical jargon

## Manifest Corruption Recovery

If manifest becomes corrupted (invalid JSON, missing required fields):

1. Command attempts to read manifest
2. JSON parse fails or validation fails
3. Command displays error: "Manifest corrupted. Regenerate from scratch?"
4. On user approval: Deletes old manifest and creates new one from scratch
5. On user rejection: Aborts and asks user to manually fix manifest

**Validation Checks**:
- Valid JSON syntax
- Required fields present (`generated_at`, `project_root`, `modules`)
- All modules have required fields (`path`, `status`, `claude_md_path`)
- Status values are valid (`"pending"`, `"completed"`, `"failed"`)
- No duplicate paths

## Performance Considerations

### Manifest Size

For a project with 100 modules:

```json
{
  "generated_at": "...",
  "project_root": "...",
  "modules": [ /* 100 module entries */ ]
}
```

**Estimated Size**: ~20KB (100 modules × ~200 bytes per entry)

**Read/Write Performance**: Negligible (<10ms) even for large projects

### Concurrency

Manifest is read once at command start and written once at command end (or after each batch). No concurrent writes, so no locking needed.

### Incremental Updates

Manifest supports incremental updates without regenerating the entire file:

```typescript
// Update single module status
manifest.modules.find(m => m.path === "src/auth").status = "completed";
manifest.generated_at = new Date().toISOString();
fs.writeFileSync('.sdd/module-manifest.json', JSON.stringify(manifest, null, 2));
```

## Versioning

This schema follows semantic versioning:

- **Major version**: Breaking changes to required fields or enum values
- **Minor version**: New optional fields
- **Patch version**: Clarifications, documentation fixes

**Current Version**: 1.0.0 (initial release)

## References

- **Parent Spec**: `.sdd/specs/spiral-grove/documentation-synthesis.md`
- **Plan**: `.sdd/plans/spiral-grove/documentation-synthesis-plan.md` (lines 229-256, 554-597)
- **Command Implementation**: `spiral-grove/commands/synthesize-docs.md` (to be created)
- **CLAUDE.md Format**: `spiral-grove/docs/claude-md-format.md`
