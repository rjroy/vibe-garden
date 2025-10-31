---
argument-hint: [scope]
description: Reverse-engineer specifications from implementation across the codebase
allowed-tools: Skill(spiral-grove:sdd-format-docs), Task, Read, Write, Glob, Grep, Bash
---

# Specification Synthesis Mode

Reverse-engineer specification documents by analyzing module implementations, generating `.sdd/specs/[module-name].md` files.

## Command Usage

```
/spiral-grove:synthesize-specs           # Full project spec synthesis
/spiral-grove:synthesize-specs src/auth  # Single module spec regeneration
```

## Your Role

You orchestrate the three-phase workflow:
1. **Phase 1: Module Discovery** - Detect modules, get user approval, create manifest
2. **Phase 2: Parallel Generation** - Spawn module-spec-synthesizer agents, track drift
3. **Phase 3: Summary** - Analyze drift, provide recommendations

## Phase 1: Module Discovery

### If scope provided (e.g., `src/auth`):
1. Validate path exists: `Glob: [scope]/**/*`
2. If no files: Exit with error
3. Create single-module manifest, skip to Phase 2

### If no scope (full project):

**Step 1: Check for Resumability**
```
Read: .sdd/spec-manifest.json

If exists and valid:
  Count statuses: completed, pending, failed

  If all completed:
    Ask: "All X modules complete. Re-run to regenerate all? [y/n]"
    If yes: Reset all to pending, continue
    If no: Exit

  If pending or failed exist:
    Ask: "Found progress: X completed, Y pending, Z failed. Continue? [y/n]"
    If yes: Skip to Phase 2 (use pending/failed modules only)
    If no: Exit

If not exists: Continue to Step 2
```

**Step 2: Check Cross-Command Integration**
```
Read: .sdd/module-manifest.json

If exists:
  Ask: "Found module manifest from /synthesize-docs. Use it? [y/n]"
  If yes:
    Convert to spec-manifest.json format:
    - Copy modules array
    - Add spec_path: ".sdd/specs/[module-name].md"
    - Add drift_detected: false
    - Set all status: "pending"
    Write: .sdd/spec-manifest.json
    Skip to Phase 2

If not exists: Continue to Step 3
```

**Step 3: Invoke Module Discovery**
```
Task(
  description: "Discover modules in codebase",
  prompt: "Analyze codebase and detect logical module boundaries using all 5 heuristics. Return ranked list with confidence ≥50%. Project root: [pwd]",
  subagent_type: "spiral-grove:module-discovery-agent"
)
```

**Step 4: Present to User**
```
Display agent's module table

Ask: "Approve? Options: yes | add <path> | remove <path> | cancel"

Handle response:
- yes/approve/ok → Continue
- add <path> → Add to list, repeat
- remove <path> → Remove from list, repeat
- cancel/no → Exit
```

**Step 5: Create Manifest and Directory**
```
Bash: mkdir -p .sdd/specs
Bash: pwd  # Get project root

Construct JSON:
{
  "generated_at": "[ISO 8601 timestamp]",
  "project_root": "[pwd output]",
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

Write: .sdd/spec-manifest.json
```

---

## Phase 2: Parallel Specification Generation

**Step 1: Filter Modules**
```
Read: .sdd/spec-manifest.json
Filter: status === "pending" OR status === "failed"
Count: N modules to process
```

**Step 2: Spawn Agents (Batches of 10)**
```
Split into batches of 10
For each batch:

  Send SINGLE message with MULTIPLE Task calls:

  Task(
    description: "Generate spec for [module-name]",
    prompt: "Generate specification for module at path: [module_path]",
    subagent_type: "spiral-grove:module-spec-synthesizer"
  )

  Wait for all agents in batch
  Parse results (see Step 3)
```

**Step 3: Update Manifest with Drift Detection**
```
For each agent response:

  If contains "✅ Spec written to .sdd/specs/":
    Extract drift status:
      If contains "Drift: NONE":
        modules[i].drift_detected = false
        modules[i].drift_summary = null
      Else if contains "Drift: DETECTED":
        modules[i].drift_detected = true
        Extract summary after "Drift: DETECTED -"
        modules[i].drift_summary = "[summary]"

    modules[i].status = "completed"
    modules[i].error = null
    Log: "✓ [path] [DRIFT] or [CLEAN]"

  Else if contains "❌ ERROR:":
    modules[i].status = "failed"
    modules[i].error = "[error message]"
    Log: "✗ Failed [path]: [error]"
    Continue (don't stop)

Update manifest.generated_at
Write: .sdd/spec-manifest.json
```

**Step 4: Display Progress**
```
Count: successful, failed, drift_detected

Output:
## Generation Complete: [successful] / [total] modules

**Successful**: ✓ [list paths with [DRIFT] markers]
**Failed**: ✗ [list paths with errors]
**Drift Detected**: [count] modules

**Next**: Phase 3 (Summary and Recommendations)
```

---

## Phase 3: Summary and Recommendations

**Step 1: Analyze Drift**
```
Read: .sdd/spec-manifest.json

Count:
- total = modules.length
- completed = status === "completed"
- failed = status === "failed"
- drift = drift_detected === true
- clean = completed - drift

Group by drift type (if drift > 0):
- Requirements added: modules with "added" in drift_summary
- Requirements modified: modules with "modified" in drift_summary
- Requirements removed: modules with "removed" in drift_summary
```

**Step 2: Generate Recommendations**
```
Based on drift analysis:

If drift === 0:
  "All implementations match specs. No action needed."

If drift > 0 && drift < total * 0.3:
  "Minor drift detected. Review and update specs or fix implementations."
  "Priority: High-confidence modules first"

If drift >= total * 0.3:
  "Significant drift detected. Consider:"
  "1. Update specs to match implementation (accept reality)"
  "2. Plan refactoring to match specs (enforce intent)"
  "3. Document rationale for divergence"

If failed > 0:
  "Address failures: [list common causes]"
```

**Step 3: Display Final Report**
```
Output:
✅ Specification Synthesis Complete

**Generated Specs**:
- Total: [total] specs
- Clean: [clean] modules
- Drift: [drift] modules
- Failed: [failed] modules

[If drift > 0:]
**Drift Details**:
| Module | Drift Summary |
|--------|---------------|
| [path] | [summary] |
...

[If failed > 0:]
**Failed Modules**:
- [path]: [error]

**Recommendations**:
[Generated recommendations from Step 2]

**Next Steps**:
1. Review generated specs in .sdd/specs/
2. For drift: Decide on resolution strategy
3. Begin SDD workflow for future features

**Manifest**: .sdd/spec-manifest.json
```

**Step 4: Edge Cases**
```
If all drift:
  "⚠️ All modules show drift. Implementation has diverged significantly from specs."

If no tests found (common in agent errors):
  "⚠️ Modules without tests produced lower-quality specs. Consider adding tests."

If all failed:
  "❌ All modules failed. Common causes: No source files, permission issues, structure mismatch."
```

---

## Final Output

```
Read: .sdd/spec-manifest.json

Count: totalGenerated, totalFailed, drift, clean

Output:
✅ Specification Synthesis Complete

**Generated Specs**: [totalGenerated] in .sdd/specs/

**Drift Analysis**:
- Clean: [clean] modules (implementation matches spec)
- Drift: [drift] modules (implementation diverged)

[If drift > 0:]
**Modules with Drift**:
[List with summaries]

[If failed > 0:]
**Failed Modules**:
- [path]: [error]

**Recommendations**:
[From Phase 3 analysis]

**Manifest**: .sdd/spec-manifest.json

✓ Specs ready for review!
```

---

## Error Handling

| Error | Action |
|-------|--------|
| No modules detected | Exit, suggest manual path |
| Invalid module path | Exit with error |
| Agent failure | Continue, report in final output |
| Manifest corruption | Prompt to regenerate |
| No tests found | Warn, continue (lower quality) |

---

## Notes

- **Reverse engineering**: Specs describe existing behavior
- **Drift detection**: Compares intended (spec) vs actual (code)
- **Framework-agnostic**: Works on any codebase
- **Batching**: Max 10 parallel agents
- **Resumability**: Manifest tracks progress
- **Cross-command**: Can import from /synthesize-docs
- **Quality**: Better tests = better specs
