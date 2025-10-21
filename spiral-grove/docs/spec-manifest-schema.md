# Spec Manifest Schema

**Version**: 1.0.0
**Created**: 2025-10-21
**Purpose**: Defines the structure of `.sdd/spec-manifest.json` for stateful specification synthesis resumability and drift tracking

## Overview

The spec manifest is a JSON file created by `/spiral-grove:synthesize-specs` that tracks the state of specification generation across all modules in a project. It enables:

1. **Resumability**: Continue generation from where it left off after interruption
2. **Idempotency**: Re-running the command safely regenerates only pending/failed modules
3. **Status Tracking**: Monitor progress during long-running generation tasks
4. **Drift Detection**: Track differences between intended specs and actual implementation
5. **Error Reporting**: Capture errors for failed module generations

## File Location

`.sdd/spec-manifest.json` (at project root)

## JSON Schema

### Root Object

```json
{
  "generated_at": "2025-10-21T14:30:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "spec_path": ".sdd/specs/auth.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "spec_path": ".sdd/specs/api.md",
      "drift_detected": true,
      "drift_summary": {
        "added": 2,
        "missing": 1,
        "modified": 3,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/utils",
      "status": "failed",
      "spec_path": ".sdd/specs/utils.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
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
| `spec_path` | string | Yes | Relative path to specification file (e.g., `".sdd/specs/auth.md"`) |
| `drift_detected` | boolean | No | Whether implementation diverged from specification (only set when status is `"completed"`) |
| `drift_summary` | object | No | Summary of drift changes (only present when `drift_detected` is `true`) |
| `error` | string \| null | No | Error message if status is `"failed"`, otherwise `null` |

#### Status Enum Values

| Value | Meaning | Next Action |
|-------|---------|-------------|
| `"pending"` | Specification not yet generated | Generate specification on next run |
| `"completed"` | Specification successfully generated (drift detected or not) | Skip on next run (unless user requests regeneration) |
| `"failed"` | Generation failed with error | Retry on next run |

#### DriftSummary Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `added` | integer | Yes | Number of requirements added in implementation that aren't in spec |
| `missing` | integer | Yes | Number of requirements in spec that are missing from implementation |
| `modified` | integer | Yes | Number of requirements that changed between spec and implementation |
| `violated_constraints` | integer | Yes | Number of constraints violated by implementation |

### Validation Rules

1. **Unique Paths**: No two modules can have the same `path` value
2. **Valid Status**: `status` must be one of: `"pending"`, `"completed"`, `"failed"`
3. **Error Consistency**: If `status` is `"failed"`, `error` must be a non-empty string; otherwise `error` should be `null`
4. **Drift Consistency**: If `drift_detected` is `true`, `drift_summary` must be present; if `false`, `drift_summary` should be omitted or all counts should be 0
5. **Path Format**: Paths must be relative (not absolute), use forward slashes (`/`), and not start with `/` or `./`
6. **Timestamp Format**: `generated_at` must be valid ISO 8601 format
7. **Project Root**: `project_root` should be an absolute path
8. **Spec Path Format**: Spec paths should start with `.sdd/specs/` and end with `.md`

## Example Manifests

### Example 1: Initial Generation (All Pending)

```json
{
  "generated_at": "2025-10-21T10:00:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "pending",
      "spec_path": ".sdd/specs/auth.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/api",
      "status": "pending",
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

### Example 2: Partial Progress (Mixed States with Drift)

```json
{
  "generated_at": "2025-10-21T10:15:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "spec_path": ".sdd/specs/auth.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "spec_path": ".sdd/specs/api.md",
      "drift_detected": true,
      "drift_summary": {
        "added": 2,
        "missing": 1,
        "modified": 3,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/db",
      "status": "failed",
      "spec_path": ".sdd/specs/db.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": "No source files found in module directory"
    },
    {
      "path": "src/utils",
      "status": "pending",
      "spec_path": ".sdd/specs/utils.md",
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

### Example 3: Fully Complete with Drift Analysis

```json
{
  "generated_at": "2025-10-21T10:30:00Z",
  "project_root": "/home/user/projects/my-app",
  "modules": [
    {
      "path": "src/auth",
      "status": "completed",
      "spec_path": ".sdd/specs/auth.md",
      "drift_detected": false,
      "drift_summary": {
        "added": 0,
        "missing": 0,
        "modified": 0,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/api",
      "status": "completed",
      "spec_path": ".sdd/specs/api.md",
      "drift_detected": true,
      "drift_summary": {
        "added": 1,
        "missing": 0,
        "modified": 2,
        "violated_constraints": 0
      },
      "error": null
    },
    {
      "path": "src/db",
      "status": "completed",
      "spec_path": ".sdd/specs/db.md",
      "drift_detected": true,
      "drift_summary": {
        "added": 0,
        "missing": 1,
        "modified": 0,
        "violated_constraints": 1
      },
      "error": null
    },
    {
      "path": "src/utils",
      "status": "completed",
      "spec_path": ".sdd/specs/utils.md",
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

## Lifecycle

### 1. Manifest Creation (Phase 1: Module Discovery)

When `/spiral-grove:synthesize-specs` runs for the first time:

1. Command detects logical module boundaries using heuristics
2. Presents detected module list to user for approval/modification
3. Creates `.sdd/spec-manifest.json` with all modules in `"pending"` status
4. All drift fields initialized to false/0
5. Saves manifest to disk

**Initial State**: All modules `"pending"`, `drift_detected` is `false`, `error` is `null`

### 2. Specification Generation (Phase 2: Parallel Generation)

Command processes modules in parallel:

1. Reads manifest to get list of `"pending"` and `"failed"` modules
2. Spawns `module-spec-synthesizer` agents for each module (parallel execution)
3. As each agent completes:
   - **Success**: Update module status to `"completed"`
   - **Drift Detected**: Set `drift_detected` to `true`, populate `drift_summary` with counts
   - **No Drift**: Set `drift_detected` to `false`, all `drift_summary` counts to 0
   - **Failure**: Update module status to `"failed"`, set `error` message
4. Updates `generated_at` timestamp after each batch

**During Generation**: Mix of `"pending"`, `"completed"` (with/without drift), and `"failed"`

### 3. Resumability (Interrupted Generation)

If generation is interrupted (timeout, user cancellation, system crash):

1. Manifest preserves state (some `"completed"`, some `"pending"`)
2. User re-runs `/spiral-grove:synthesize-specs`
3. Command reads manifest and detects partial completion
4. Prompts user: "Continue from where we left off? (X modules remaining)"
5. On approval: Processes only `"pending"` and `"failed"` modules
6. Updates manifest as generation progresses

**After Resumption**: More modules marked `"completed"`, fewer `"pending"`

### 4. Idempotent Re-runs (Full Regeneration)

If user wants to regenerate all specifications:

1. User runs `/spiral-grove:synthesize-specs` on fully completed project
2. Command detects all modules are `"completed"`
3. Prompts user: "All X modules complete. Re-run to regenerate all (with drift detection)? [y/n]"
4. On approval: Resets all statuses to `"pending"` and regenerates
5. Existing specs updated with new drift detection

**After Regeneration**: All modules `"completed"` with updated drift status and timestamps

### 5. Incremental Updates (New Modules Added)

If project evolves and new modules are added:

1. User runs `/spiral-grove:synthesize-specs` again
2. Command detects new modules not in manifest
3. Prompts user: "Found 3 new modules. Add to manifest and generate?"
4. On approval: Adds new modules with `"pending"` status
5. Generates specifications for new modules only

**After Incremental Update**: Existing modules unchanged, new modules `"completed"` with drift data

## Usage by Components

### Synthesize-Specs Command (Phase 1: Module Discovery)

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
    spec_path: `.sdd/specs/${extractModuleName(module.path)}.md`,
    drift_detected: false,
    drift_summary: {
      added: 0,
      missing: 0,
      modified: 0,
      violated_constraints: 0
    },
    error: null
  }))
};

fs.writeFileSync('.sdd/spec-manifest.json', JSON.stringify(manifest, null, 2));
```

### Synthesize-Specs Command (Phase 2: Parallel Generation)

```typescript
// Pseudocode for specification generation

const manifest = JSON.parse(fs.readFileSync('.sdd/spec-manifest.json'));

const pendingModules = manifest.modules.filter(m =>
  m.status === "pending" || m.status === "failed"
);

// Spawn agents in parallel
const results = await Promise.allSettled(
  pendingModules.map(module => spawnModuleSpecAgent(module.path))
);

// Update manifest based on results
results.forEach((result, index) => {
  const module = pendingModules[index];
  const manifestIndex = manifest.modules.findIndex(m => m.path === module.path);

  if (result.status === "fulfilled") {
    manifest.modules[manifestIndex].status = "completed";
    manifest.modules[manifestIndex].drift_detected = result.value.driftDetected;
    manifest.modules[manifestIndex].drift_summary = result.value.driftSummary;
    manifest.modules[manifestIndex].error = null;
  } else {
    manifest.modules[manifestIndex].status = "failed";
    manifest.modules[manifestIndex].error = result.reason.message;
  }
});

manifest.generated_at = new Date().toISOString();
fs.writeFileSync('.sdd/spec-manifest.json', JSON.stringify(manifest, null, 2));
```

### Synthesize-Specs Command (Resumability Check)

```typescript
// Pseudocode for resumability check

const manifestPath = '.sdd/spec-manifest.json';

if (fs.existsSync(manifestPath)) {
  const manifest = JSON.parse(fs.readFileSync(manifestPath));

  const completedCount = manifest.modules.filter(m => m.status === "completed").length;
  const pendingCount = manifest.modules.filter(m => m.status === "pending").length;
  const failedCount = manifest.modules.filter(m => m.status === "failed").length;

  if (completedCount === manifest.modules.length) {
    const shouldRegenerate = await promptUser(
      "All X modules complete. Re-run to regenerate all (with drift detection)?"
    );
    if (shouldRegenerate) {
      manifest.modules.forEach(m => {
        m.status = "pending";
        m.drift_detected = false;
        m.drift_summary = { added: 0, missing: 0, modified: 0, violated_constraints: 0 };
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
        m.drift_detected = false;
        m.drift_summary = { added: 0, missing: 0, modified: 0, violated_constraints: 0 };
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
| `"Invalid markdown generated (unbalanced code fences)"` | Agent generated malformed markdown | Agent bug - report issue |
| `"Permission denied writing to [path]"` | Filesystem permission issue | Check directory permissions |

### Error Field Format

```json
{
  "path": "src/broken-module",
  "status": "failed",
  "spec_path": ".sdd/specs/broken-module.md",
  "drift_detected": false,
  "drift_summary": {
    "added": 0,
    "missing": 0,
    "modified": 0,
    "violated_constraints": 0
  },
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
- All modules have required fields (`path`, `status`, `spec_path`, `drift_detected`, `drift_summary`)
- Status values are valid (`"pending"`, `"completed"`, `"failed"`)
- Drift summary values are valid non-negative integers
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

**Estimated Size**: ~30KB (100 modules × ~300 bytes per entry due to drift_summary)

**Read/Write Performance**: Negligible (<10ms) even for large projects

### Concurrency

Manifest is read once at command start and written once at command end (or after each batch). No concurrent writes, so no locking needed.

### Incremental Updates

Manifest supports incremental updates without regenerating the entire file:

```typescript
// Update single module status with drift data
const moduleIndex = manifest.modules.findIndex(m => m.path === "src/auth");
manifest.modules[moduleIndex].status = "completed";
manifest.modules[moduleIndex].drift_detected = true;
manifest.modules[moduleIndex].drift_summary = {
  added: 2,
  missing: 1,
  modified: 3,
  violated_constraints: 0
};
manifest.generated_at = new Date().toISOString();
fs.writeFileSync('.sdd/spec-manifest.json', JSON.stringify(manifest, null, 2));
```

## Versioning

This schema follows semantic versioning:

- **Major version**: Breaking changes to required fields or enum values
- **Minor version**: New optional fields
- **Patch version**: Clarifications, documentation fixes

**Current Version**: 1.0.0 (initial release)

## References

- **Parent Spec**: `.sdd/specs/spiral-grove/specification-synthesis.md`
- **Plan**: `.sdd/plans/spiral-grove/specification-synthesis-plan.md`
- **Command Implementation**: `spiral-grove/commands/synthesize-specs.md`
- **Module Manifest Schema**: `spiral-grove/docs/module-manifest-schema.md` (companion schema for docs)
- **CLAUDE.md Format**: `spiral-grove/docs/claude-md-format.md`
