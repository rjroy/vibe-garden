---
name: synthesize-specs
description: This skill should be used when the user asks to "reverse-engineer specs", "create specs from code", "extract requirements", "synthesize specifications", or invokes /spiral-grove:synthesize-specs. Reverse-engineers specification documents from module implementations.
allowed-tools: Skill(spiral-grove:sdd-format-docs), Task, Read, Write, Glob, Grep, Bash
---

# Specification Synthesis

Reverse-engineer specification documents by analyzing module implementations, generating `.sdd/specs/[module-name].md` files.

## Command Usage

```
/spiral-grove:synthesize-specs           # Full project spec synthesis
/spiral-grove:synthesize-specs src/auth  # Single module spec regeneration
```

## Role

Orchestrate the three-phase workflow:
1. **Phase 1: Module Discovery** - Detect modules, get user approval, create manifest
2. **Phase 2: Parallel Generation** - Spawn module-spec-synthesizer agents, track drift
3. **Phase 3: Summary** - Analyze drift, provide recommendations

## Phase 1: Module Discovery

### If Scope Provided (e.g., `src/auth`)

1. Validate path exists: `Glob: [scope]/**/*`
2. If no files: Exit with error
3. Create single-module manifest, skip to Phase 2

### If No Scope (Full Project)

**Step 1: Check Resumability**
```
Read: .sdd/spec-manifest.json

If exists and valid:
  Count: completed, pending, failed

  If all completed:
    Ask: "All X modules complete. Re-run to regenerate all? [y/n]"
    If yes: Reset all to pending, continue
    If no: Exit

  If pending or failed exist:
    Ask: "Found progress: X completed, Y pending, Z failed. Continue? [y/n]"
    If yes: Skip to Phase 2 (use pending/failed only)
    If no: Exit

If not exists: Continue to Step 2
```

**Step 2: Check Cross-Command Integration**
```
Read: .sdd/module-manifest.json

If exists:
  Ask: "Found module manifest from /synthesize-docs. Use it? [y/n]"
  If yes:
    Convert to spec-manifest.json format
    Skip to Phase 2
```

**Step 3: Invoke Module Discovery**
```
Task(
  description: "Discover modules in codebase",
  prompt: "Analyze codebase and detect logical module boundaries using all 5 heuristics. Return ranked list with confidence >= 50%. Project root: [pwd]",
  subagent_type: "spiral-grove:module-discovery-agent"
)
```

**Step 4: Present to User**
```
Display agent's module table

Ask: "Approve? Options: yes | add <path> | remove <path> | cancel"
```

**Step 5: Create Manifest and Directory**
```
Bash: mkdir -p .sdd/specs
Bash: pwd

Write .sdd/spec-manifest.json:
{
  "generated_at": "[ISO 8601 timestamp]",
  "project_root": "[pwd]",
  "modules": [
    {
      "path": "[module path]",
      "status": "pending",
      "spec_path": ".sdd/specs/[module-name].md",
      "drift_detected": false,
      "drift_summary": null,
      "error": null
    }
  ]
}
```

## Phase 2: Parallel Specification Generation

**Step 1: Filter Modules**
```
Read: .sdd/spec-manifest.json
Filter: status === "pending" OR status === "failed"
```

**Step 2: Spawn Agents (Batches of 10)**
```
For each batch of 10 modules:

  Send SINGLE message with MULTIPLE Task calls:

  Task(
    description: "Generate spec for [module-name]",
    prompt: "Generate specification for module at path: [module_path]",
    subagent_type: "spiral-grove:module-spec-synthesizer"
  )

  Wait for all agents in batch
```

**Step 3: Update Manifest with Drift Detection**
```
For each agent response:

  If contains "Spec written to .sdd/specs/":
    Extract drift status:
      If "Drift: NONE":
        drift_detected = false
      Else if "Drift: DETECTED":
        drift_detected = true
        Extract drift_summary

    modules[i].status = "completed"
    Log: "[path] [DRIFT] or [CLEAN]"

  Else if contains "ERROR:":
    modules[i].status = "failed"
    modules[i].error = "[error message]"
    Continue (don't stop)

Write: .sdd/spec-manifest.json
```

**Step 4: Display Progress**
```
Output:
## Generation Complete: [successful] / [total] modules

**Successful**: [list paths with [DRIFT] markers]
**Failed**: [list paths with errors]
**Drift Detected**: [count] modules
```

## Phase 3: Summary and Recommendations

**Step 1: Analyze Drift**
```
Count:
- total = modules.length
- completed = status === "completed"
- failed = status === "failed"
- drift = drift_detected === true
- clean = completed - drift

Group by drift type:
- Requirements added
- Requirements modified
- Requirements removed
```

**Step 2: Generate Recommendations**
```
If drift === 0:
  "All implementations match specs. No action needed."

If drift > 0 && drift < total * 0.3:
  "Minor drift detected. Review and update specs or fix implementations."

If drift >= total * 0.3:
  "Significant drift detected. Consider:
   1. Update specs to match implementation (accept reality)
   2. Plan refactoring to match specs (enforce intent)
   3. Document rationale for divergence"

If failed > 0:
  "Address failures: [list common causes]"
```

**Step 3: Display Final Report**
```
Output:
Specification Synthesis Complete

**Generated Specs**:
- Total: [count] specs
- Clean: [count] modules
- Drift: [count] modules
- Failed: [count] modules

[If drift > 0:]
**Drift Details**:
| Module | Drift Summary |
|--------|---------------|
| [path] | [summary] |

**Recommendations**:
[From Step 2]

**Next Steps**:
1. Review generated specs in .sdd/specs/
2. For drift: Decide on resolution strategy
3. Begin SDD workflow for future features

**Manifest**: .sdd/spec-manifest.json
```

## Error Handling

| Error | Action |
|-------|--------|
| No modules detected | Exit, suggest manual path |
| Invalid module path | Exit with error |
| Agent failure | Continue, report in final output |
| Manifest corruption | Prompt to regenerate |
| No tests found | Warn, continue (lower quality) |

## Key Points

- **Reverse engineering**: Specs describe existing behavior
- **Drift detection**: Compares intended (spec) vs actual (code)
- **Framework-agnostic**: Works on any codebase
- **Batching**: Max 10 parallel agents
- **Resumability**: Manifest tracks progress
- **Cross-command**: Can import from /synthesize-docs
- **Quality**: Better tests = better specs
