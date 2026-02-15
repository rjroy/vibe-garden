---
title: Implementation notes: simplify-skill
date: 2026-02-15
status: complete
tags: [implementation, notes, simplify, cleanup, orchestration]
source: .lore/plans/simplify-skill.md
modules: [lore-development]
---

# Implementation Notes: Simplify Skill

## Progress
- [x] Phase 1: Create Skill Structure
- [x] Phase 2: Implement Input Detection Logic
- [x] Phase 3: Implement Notes File Creation
- [x] Phase 4: Implement Agent Selection
- [x] Phase 5-8: Implement Cleanup Orchestration, Testing, Failure Diagnosis, and Code Review
- [x] Phase 9: Integrate with Implement Skill
- [x] Phase 10: Validate Against Spec

## Log

### Phase 1: Create Skill Structure
- Dispatched: Create `lore-development/skills/simplify/SKILL.md` with frontmatter and section headers (When to Use, Input, Process, Output, Context)
- Result: Skill structure created following patterns from prep-plan and implement skills. Includes third-person description, three input modes (git changes, file patterns, notes files), orchestration process, notes guidance, and escalation rules.
- Tests: N/A (structural phase)
- Review: Initial review found missing trigger phrases in frontmatter description. Fixed by adding explicit conversational triggers ("simplify this", "clean up this code", etc.). Re-review confirms skill is ready.

### Phase 2: Implement Input Detection Logic
- Dispatched: Add three input modes to Initialize section: git changes via `git status --porcelain`, file patterns via Glob, notes file parsing via Read. Include binary filtering and empty list handling.
- Result: Input detection logic added to Process section with argument parsing, git status parsing with deletion filtering, file pattern globbing, and notes file log parsing. Binary file filtering procedure defined once and referenced by all modes.
- Tests: N/A (logic instructions, not executable code)
- Review: Initial review found critical issues with instruction clarity (missing argument parsing, vague git status parsing, unclear binary filtering, no existence checks). Fixed by adding explicit step-by-step instructions for argument parsing, git status parsing with rename handling, shared binary filtering procedure with error handling, and file existence checks for all modes. Re-review confirms all critical issues resolved.

### Phase 3: Implement Notes File Creation
- Dispatched: Add notes file identifier logic (git-changes, sanitized pattern, base name), template structure, and update instructions to Initialize, Output, and Process sections.
- Result: Notes file identifier logic added for all three input modes. Complete template structure added to Output section with frontmatter schema reference. Update instructions added specifying when to update each section (Files Processed during init, Cleanup Agents Run after selection, Results after each step, Failures when needed). Status progression from `active` to `complete` documented.
- Tests: N/A (template and instructions, not executable code)
- Review: Initial review found minor formatting inconsistencies with spec (Files Processed should be bullet list, Failures should use subheadings, "session-id" should be "identifier"). Fixed template formatting to match spec exactly. Re-review confirms spec compliance.

### Phase 4: Implement Agent Selection
- Dispatched: Add agent selection logic to Initialize section: always include code-simplifier, check registry for additional agents in Code Quality section, graceful fallback if registry missing.
- Result: Agent selection logic added with three steps: (1) mandatory code-simplifier, (2) registry check for Code Quality section agents with "simplif" matching, (3) fallback to default agent only if registry missing/malformed. Records selected agents in notes file.
- Tests: N/A (logic instructions, not executable code)
- Review: Initial review found critical ambiguities (multi-agent handling unclear, no verification after Edit, malformed registry not handled, heading format vague). Fixed by adding explicit "add ALL matching agents" with deduplication, verification step after Edit, malformed registry fallback, and precise heading format ("## Code Quality", H2, case-sensitive). Re-review confirms all issues resolved.

### Phases 5-8: Implement Cleanup Orchestration, Testing, Failure Diagnosis, and Code Review
- Dispatched: Add Execute Files section with cleanup agent dispatch, test execution, test failure diagnosis, code review dispatch, and review failure handling. Implement one-pass enforcement, iteration limits, and notes updates after each step.
- Result: Complete Execute Files section added with sequential agent dispatch (blocking calls, wait between agents), notes update stacking with examples, test execution with failure diagnosis cycle, code review with correction cycle, iteration limits (max 2 attempts before escalation), agent selection for fixes (last modifier or default to code-simplifier).
- Tests: N/A (orchestration instructions, not executable code)
- Review: Initial review found critical execution gaps (blocking/sequential enforcement unclear, one-pass vs correction cycles contradictory, notes stacking without examples, iteration limits not inline, agent selection for fixes ambiguous, file list source unclear). Fixed by adding explicit blocking/wait instructions, clarifying one-pass applies to simplification only (corrections allowed), adding stacking examples, inlining iteration limits, specifying agent routing with fallback, and clarifying file list source. Minor follow-up fixes removed circular file list reference and redundant Escalation Rules pointers. Re-review confirms all critical issues resolved.

### Phase 9: Integrate with Implement Skill
- Dispatched: Add suggestion to implement skill's Finalize section to recommend running simplify on the notes file after successful completion.
- Result: Added plain text suggestion in implement skill (lore-development/skills/implement/SKILL.md) after status update to complete. Suggestion format: "Implementation complete. Run `/simplify .lore/notes/<artifact-name>.md` to clean up the code for clarity." with clear placeholder substitution instruction.
- Tests: N/A (text suggestion, not executable code)
- Review: Review confirms correct placement (after successful completion), plain output format (not interactive), correct notes filename reference, clear actionable wording. Fully satisfies REQ-SIMPLIFY-21 and REQ-SIMPLIFY-22.

### Phase 10: Validate Against Spec
- Dispatched: Validate implementation against spec using plan-reviewer agent. Check all 22 requirements are addressed.
- Result: Validator identified critical input format issue (flag-based vs positional args), testing architecture marked as divergence (later confirmed as correct per implement skill pattern), missing failure diagnosis workflow (automated retries vs user-facing), and registry schema mismatch (Code Quality vs cleanup category).
- Tests: N/A (validation phase)
- Review: User confirmed testing delegation matches implement skill pattern (correct), automated retries preferred over user-facing diagnosis (acceptable divergence), and flags are overcomplicated. Fixed input parsing to use positional args (no args → git changes, pattern → file patterns, .lore/notes path → notes mode). Other divergences documented as approved architectural decisions.
- Resolution: Critical input format issue fixed. Testing delegation validated as correct. Automated retry architecture approved. Registry uses Code Quality section until cleanup category exists (acceptable interim solution).

## Divergence

- **Testing architecture**: Spec implies direct Bash execution of tests. Implementation delegates testing to agent via Task tool. This matches the implement skill pattern (see lore-development/skills/implement/SKILL.md line 119) and is the correct orchestrator approach. (approved)

- **Failure diagnosis workflow**: Spec defines user-facing diagnosis with git diff analysis and AskUserQuestion (3 options: fix cleanup/fix tests/abort). Implementation uses automated retry loops with diagnosis agent that escalates after 2 attempts. User confirmed automated retries are preferred for natural language invocation workflow. (approved)

- **Registry schema**: Spec references "cleanup" category in agent registry. Implementation looks for "Code Quality" section because cleanup category doesn't exist yet (noted as STUB dependency in spec). This is an acceptable interim solution until cleanup category is added to registry schema. (approved)
