---
title: Python module structure in Claude Code plugins
date: 2026-01-31
status: resolved
tags: [plugin, python, module-structure, packaging]
modules: [mind-reader]
related: [.lore/work/retros/mind-reader/mind-reader-init-failure.md]
---

# Brainstorm: Python Module Structure in Claude Code Plugins

## Context

The mind-reader plugin failed to initialize because its Python scripts import from a `lib` module that doesn't exist. The retro captured the symptoms; this brainstorm explores the underlying patterns and constraints.

## Plugin Execution Context

When Claude Code runs a hook script, the context differs from local development:

- **Working directory**: The user's project directory (`$CLAUDE_PROJECT_DIR`)
- **Script location**: Plugin cache at `~/.claude/plugins/cache/<org>/<plugin>/<version>/`
- **Python path**: Default system path (no special plugin configuration)

The script's `__file__` resolves correctly, but Python won't automatically find sibling modules. Scripts must explicitly manipulate `sys.path`.

## Patterns from Working Plugins

### Pattern 1: Flat modules (notify-hook)

```
scripts/
  notify.py      # Entry point
  lib.py         # Single utility file
  backends.py    # Another utility file
```

Import approach:
```python
try:
    from lib import load_config
except ImportError:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from lib import load_config
```

Works because `lib.py` is a sibling file in the same directory.

### Pattern 2: Package structure (audio-analysis)

```
scripts/
  audio/
    analyze_beats.py  # Entry point
  shared/
    __init__.py       # Exports public interface
    errors.py
    validation.py
    output.py
```

Import approach:
```python
# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared import validate_audio_file, output_success
```

Works because:
1. Scripts are in subdirectory (`scripts/audio/`)
2. Path manipulation goes up to `scripts/`
3. `shared/` is a proper package with `__init__.py`

### What mind-reader attempted

```
scripts/
  hook.py          # Entry point
  baseline.py      # Entry point
  lib/             # Expected package (doesn't exist)
    __init__.py
    state.py
    settings.py
    ...
```

The code structure assumes pattern 2, but the package doesn't exist. The path manipulation adds `scripts/` to sys.path, which is correct. The missing piece is the `lib/` package itself.

## Ideas Explored

### What if we use pattern 1 (flat modules)?

Flatten everything into single files in `scripts/`:
- `scripts/state.py`
- `scripts/settings.py`
- `scripts/sentiment.py`
- `scripts/temporal.py`

**Trade-offs:**
- Simpler import mechanics
- Harder to organize as codebase grows
- Breaks the existing test structure (tests import from `lib.*`)

### What if we use pattern 2 (package structure)?

Create `scripts/lib/` as a proper Python package:
- `scripts/lib/__init__.py` (exports public interface)
- `scripts/lib/state.py`
- `scripts/lib/settings.py`
- etc.

**Trade-offs:**
- Matches existing import statements and test structure
- Cleaner organization
- Requires understanding the package boundary

### What if the tests are the spec?

The test files (`test_state.py`, `test_sentiment.py`, etc.) describe the expected public interface. They import specific functions and classes. We could treat these as the specification and implement to match.

**Observation:** Test file names mirror module structure. The imports in tests define the contract.

### What if plugin packaging validated imports?

Future improvement: Before publishing a plugin, validate that all import statements resolve. This would catch the current issue at publish time rather than runtime.

**Implementation ideas:**
- Static analysis of Python files for import statements
- Attempted import in isolated environment
- Check that imported modules exist in cache structure

## pyproject.toml vs Runtime

The current pyproject.toml has:
```toml
[tool.pytest.ini_options]
pythonpath = ["scripts"]
```

This configures pytest to find modules, but does nothing for runtime execution. The hook is executed directly by Claude Code, not by pytest. This is a common confusion: dev tooling configuration doesn't affect production runtime.

## Open Questions

1. **Should mind-reader use flat or package structure?**
   - Package seems right given test structure and existing imports

2. **How does the shebang interact with venv?**
   - The init skill updates shebangs to use plugin venv Python
   - Does the venv's site-packages affect import resolution?

3. **Should vibe-garden have a shared pattern for Python plugins?**
   - notify-hook uses flat
   - mind-reader would use package
   - Worth documenting a standard?

4. **What validation should happen at publish time?**
   - Import validation
   - Test execution
   - Structure checks

## Next Steps

1. Create `scripts/lib/` package structure matching test expectations
2. Implement modules with interfaces inferred from test imports
3. Document the pattern for future Python plugin development
4. Consider adding pre-publish validation to vibe-garden
