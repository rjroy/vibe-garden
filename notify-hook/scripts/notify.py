#!/usr/bin/env python3
"""
Main hook script for notify-hook plugin.
Orchestrates: config load → filter → sanitize → rate limit → dispatch.
Stdlib only - no external dependencies.
"""

import json
import sys
from pathlib import Path

# Import our modules
try:
    from lib import load_config, sanitize_message, should_filter_message, is_rate_limited
    from git import generate_topic
    from backends import dispatch_all
except ImportError:
    # Handle running from different directories
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from lib import load_config, sanitize_message, should_filter_message, is_rate_limited
    from git import generate_topic
    from backends import dispatch_all


def main():
    """
    Main entry point for notification hook.

    Pipeline:
    1. Read hook input from stdin
    2. Load configuration
    3. Filter message (exit early if filtered)
    4. Sanitize message (privacy rules)
    5. Check rate limits (per backend)
    6. Dispatch to enabled backends

    Always exits with code 0 to avoid blocking Claude Code.
    """
    try:
        # Step 1: Read hook input JSON from stdin
        try:
            hook_input = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(0)  # Exit gracefully, don't block Claude

        # Extract message from hook input
        raw_message = hook_input.get('message', '')
        if not raw_message:
            print("Warning: No message in hook input", file=sys.stderr)
            sys.exit(0)

        # Step 2: Load configuration
        try:
            config = load_config()
        except Exception as e:
            print(f"Warning: Failed to load config, using defaults: {e}", file=sys.stderr)
            # Continue with defaults
            from lib import Config, DEFAULT_CONFIG
            config = Config.from_dict(DEFAULT_CONFIG)

        # Step 3: Apply message filter
        if should_filter_message(raw_message, config):
            print(f"Filtered out: {raw_message[:50]}...", file=sys.stderr)
            sys.exit(0)

        # Step 4: Sanitize message (privacy rules)
        sanitized_message = sanitize_message(raw_message, config)
        if not sanitized_message:
            print("Warning: Message was completely sanitized (empty)", file=sys.stderr)
            sys.exit(0)

        # Step 5: Generate topic for ntfy.sh
        try:
            topic = generate_topic(config)
        except Exception as e:
            print(f"Warning: Failed to generate topic: {e}", file=sys.stderr)
            topic = "claude-unknown-unknown"

        # Step 6: Check rate limits and dispatch
        backends_config = config.backends
        dispatched_count = 0

        # Check if globally disabled
        if not any(backend.get("enabled", False) for backend in backends_config.values()):
            print("Info: All backends disabled", file=sys.stderr)
            sys.exit(0)

        # Dispatch to backends
        for backend_name in ["ntfy", "discord", "slack"]:
            backend_config = backends_config.get(backend_name, {})

            if not backend_config.get("enabled", False):
                continue

            # Check rate limit for this backend
            if is_rate_limited(backend_name, config):
                print(f"Rate limited: {backend_name}", file=sys.stderr)
                continue

            dispatched_count += 1

        # Actually dispatch
        if dispatched_count > 0:
            try:
                results = dispatch_all(sanitized_message, backends_config, topic)

                # Log summary
                success_count = sum(1 for success in results.values() if success)
                print(f"Dispatched to {success_count}/{dispatched_count} backends", file=sys.stderr)

            except Exception as e:
                print(f"Warning: Dispatch failed: {e}", file=sys.stderr)
        else:
            print("Info: No backends available (all disabled or rate limited)", file=sys.stderr)

    except Exception as e:
        # Catch-all: log error but exit gracefully
        print(f"Error in notify hook: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    # Always exit 0 to avoid blocking Claude Code
    sys.exit(0)


if __name__ == "__main__":
    main()
