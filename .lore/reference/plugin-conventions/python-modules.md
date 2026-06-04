---
title: Python module structure in vibe-garden plugins
date: 2026-04-25
status: approved
tags: [plugin-conventions, python, imports, packaging]
modules: [mind-reader, notify-hook]
---

# Python Module Structure in vibe-garden Plugins

Two execution contexts run plugin Python: pytest (during development) and Claude Code (at runtime). They configure imports differently, and both must work. Everything below exists to keep that true.

## Plugin script execution contract

When Claude Code runs a hook script, the runtime context differs from local development:

- **Working directory** is `$CLAUDE_PROJECT_DIR` (the user's project), not the plugin's directory.
- **Script lives at** `~/.claude/plugins/cache/<org>/<plugin>/<version>/scripts/<name>.py`, invoked via `${CLAUDE_PLUGIN_ROOT}` in `hooks.json`.
- **Python path** is the system default. Claude Code does not add the plugin's `scripts/` to `sys.path`.

Sibling-file or sub-package imports do not "just work." Every Python entry-point script in a vibe-garden plugin needs an explicit `sys.path` setup at the top of the file.

## Two patterns: flat vs package

**Flat (notify-hook):** entry-point and helpers as sibling files in `scripts/`. Use when the plugin has ≤3-4 modules total. Imports look like `from lib import ...` after `sys.path` is patched.

**Package (mind-reader):** entry-points in `scripts/`, helpers in `scripts/<package>/` with `__init__.py`. Use when the plugin has more modules or wants explicit grouping. Imports look like `from core import ...` after `sys.path` is patched to include `scripts/`.

Both patterns require `sys.path` manipulation; the difference is only whether helpers live in sibling files or a sub-package. Start flat. Promote to package when you'd otherwise add a fifth helper file.

## The try/except import wrapper is load-bearing

Every entry-point script begins:

```python
try:
    from <module> import <name>
except ImportError:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from <module> import <name>
```

The plain import works under pytest because `[tool.pytest.ini_options].pythonpath = ["scripts"]` puts `scripts/` on `sys.path` for tests. At runtime, no such configuration exists, so the import fails and the fallback patches `sys.path` from `__file__`. Removing either branch breaks one of the two execution contexts.

Do not "simplify" this wrapper away. If a tool flags it as redundant, the tool is wrong about the runtime.

## `pyproject.toml`'s `pythonpath` is dev-only

The `[tool.pytest.ini_options].pythonpath = ["scripts"]` line configures **pytest** to find the plugin's modules. It does **not** affect runtime. Claude Code invokes hook scripts directly, not through pytest, and ignores `pyproject.toml` entirely.

A contributor who hits an import error at runtime may add or modify `pythonpath` in `pyproject.toml` and find that tests still pass while the hook still fails. The dev/runtime distinction has to be held in your head; the config file does not surface it. If runtime imports break, fix the script's `sys.path` manipulation (above), not `pyproject.toml`.
