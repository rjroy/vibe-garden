---
name: install-formula
description: Install the reusable lore-development Beads formula into the current project. Use when a project should run the lore-development workflow through bd molecules.
---

# Install Formula

Install the plugin's `lore-development` Beads formula into the current project.

## Process

1. From this skill's base directory, resolve the plugin root two levels up. The
   source formula is at `../../formulas/lore-development.formula.toml`.
2. Confirm the current directory is the intended project root. Do not install into
   a parent directory or a different checkout without the user's explicit path.
3. Create `.beads/formulas/` if it does not exist.
4. If `.beads/formulas/lore-development.formula.toml` does not exist, copy the
   source formula there.
5. If it already exists, compare it with the plugin formula. Report that it is
   already installed when identical. If it differs, stop and ask whether the user
   wants to replace it. Never overwrite a project-owned formula silently.
6. Run `bd formula show .beads/formulas/lore-development.formula.toml --json` and
   verify that the parsed result contains the required variables and workflow
   steps, with human gates on `approve-design` and `approve-plan`. Intent is
   conversational context, not an approval gate.
7. Explain how to use the installed formula. `bd mol pour` can cook a formula
   from the project formula search path directly:

```bash
bd mol pour lore-development --var topic="..." --var artifact_name="..."
```

## Approval Semantics

Do not replace human gates with an `approved` variable. Variables provide work
inputs; they do not establish that a person made a decision. A human gate remains
open until a person resolves it with `bd gate resolve <gate-id>`.

The formula gates design and implementation-plan approval, not intent. Intent is
a conversational record of what and why, not a contract requiring approval.
Implementation proceeds without a routine approval gate. If the implementation
skill encounters a concrete safety or compatibility concern or a stuck correction
loop, it must escalate to the user rather than inventing an approval value.

## Safety

- Do not modify an existing formula without explicit user permission.
- Do not create or close molecule steps while installing the formula.
- Do not claim that a gate was approved based on a variable, prompt assumption, or
  agent judgment.
