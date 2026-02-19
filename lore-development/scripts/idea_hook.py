#!/usr/bin/env python3
"""
Hook script for /idea capture in lore-development plugin.
Intercepts prompts starting with "/idea " and appends to daily ideas file.
Outputs block decision JSON or empty {} to stdout.
Always exits 0 to avoid blocking Claude Code.
"""

import json
import sys
from datetime import date
from pathlib import Path

PREFIX = "/idea "


def main():
    try:
        try:
            hook_input = json.load(sys.stdin)
        except (json.JSONDecodeError, ValueError):
            print("{}")
            sys.exit(0)

        prompt = hook_input.get("prompt", "")
        cwd = hook_input.get("cwd", "")

        if not prompt.startswith(PREFIX):
            print("{}")
            sys.exit(0)

        idea_text = prompt[len(PREFIX) :].strip()
        if not idea_text:
            print("{}")
            sys.exit(0)

        if not cwd:
            print("Warning: No cwd in hook input", file=sys.stderr)
            print("{}")
            sys.exit(0)

        today = date.today().isoformat()
        ideas_dir = Path(cwd) / ".lore" / "ideas"
        ideas_dir.mkdir(parents=True, exist_ok=True)

        daily_file = ideas_dir / f"{today}.md"
        if daily_file.exists():
            with open(daily_file, "a") as f:
                f.write(f"- {idea_text}\n")
        else:
            with open(daily_file, "w") as f:
                f.write(f"# {today}\n\n- {idea_text}\n")

        output = {
            "decision": "block",
            "reason": f"Idea saved to .lore/ideas/{today}.md",
        }
        print(json.dumps(output))

    except Exception as e:
        print(f"Error in idea hook: {e}", file=sys.stderr)
        print("{}")

    sys.exit(0)


if __name__ == "__main__":
    main()
