#!/usr/bin/env python3
"""
Main hook script for mind-reader plugin.
Runs on UserPromptSubmit to check temporal and sentiment signals.
Outputs JSON nudge or empty {} to stdout.
Always exits 0 to avoid blocking Claude Code.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Handle import from different directories
try:
    from core import (
        SessionState,
        analyze_prompt,
        check_bucket_duration,
        check_bucket_rarity,
        check_duration_threshold,
        check_prompt_threshold,
        check_rolling_sentiment,
        check_unusual_hour,
        load_settings,
        read_baseline,
        read_session_state,
        update_sentiment_window,
        write_session_state,
    )
except ImportError:
    script_dir = Path(__file__).parent
    sys.path.insert(0, str(script_dir))
    from core import (
        SessionState,
        analyze_prompt,
        check_bucket_duration,
        check_bucket_rarity,
        check_duration_threshold,
        check_prompt_threshold,
        check_rolling_sentiment,
        check_unusual_hour,
        load_settings,
        read_baseline,
        read_session_state,
        update_sentiment_window,
        write_session_state,
    )


def main():
    """
    Main entry point for the mind-reader hook.

    Pipeline:
    1. Read hook input from stdin (prompt, session_id)
    2. Check if enabled and not quiet
    3. Load baseline and session state
    4. Update session state (prompt_count, sentiment)
    5. Run temporal checks
    6. Run sentiment checks
    7. Emit nudge if triggered, otherwise {}
    8. Save session state

    Always exits with code 0 to avoid blocking Claude Code.
    """
    try:
        # Step 1: Read hook input JSON from stdin
        try:
            hook_input = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON input: {e}", file=sys.stderr)
            print("{}")
            sys.exit(0)

        prompt = hook_input.get("prompt", "")
        session_id = hook_input.get("session_id", "")

        if not session_id:
            print("Warning: No session_id in hook input", file=sys.stderr)
            print("{}")
            sys.exit(0)

        # Step 2: Load settings and check if enabled
        settings = load_settings()

        if not settings.enabled:
            print("{}")
            sys.exit(0)

        if settings.is_quiet():
            print("{}")
            sys.exit(0)

        # Step 3: Load baseline and session state
        baseline = read_baseline()
        state = read_session_state(session_id)

        if state is None:
            state = SessionState(
                session_id=session_id,
                started_at=datetime.now(),
                prompt_count=0,
                sentiment_scores=[],
                last_nudge_prompt=None,
            )

        # Step 4: Update session state
        state.prompt_count += 1

        # Analyze sentiment (if VADER available)
        sentiment_score = analyze_prompt(prompt)
        if sentiment_score is not None:
            window_size = settings.sentiment.window_size
            update_sentiment_window(state, sentiment_score, window_size)

        nudge_message = None

        # Step 5: Run temporal checks (only if baseline exists and not stale)
        if baseline is not None and not baseline.is_stale():
            # Use v2 bucket-based checks if available, fallback to v1
            if baseline.has_v2_data():
                # V2: Two-stage hurdle model

                # Stage 1: Check bucket rarity (only on first prompt)
                if state.prompt_count == 1:
                    rarity_nudge = check_bucket_rarity(baseline, settings)
                    if rarity_nudge:
                        nudge_message = rarity_nudge.message

                # Stage 2: Check bucket duration
                if nudge_message is None:
                    bucket_duration_nudge = check_bucket_duration(
                        state, baseline, settings
                    )
                    if bucket_duration_nudge:
                        nudge_message = bucket_duration_nudge.message

                # Fallback to prompt count check if no bucket nudge
                if nudge_message is None:
                    prompt_nudge = check_prompt_threshold(state, baseline, settings)
                    if prompt_nudge:
                        nudge_message = prompt_nudge.message
            else:
                # V1: Legacy checks

                # Check duration
                duration_nudge = check_duration_threshold(state, baseline, settings)
                if duration_nudge:
                    nudge_message = duration_nudge.message

                # Check prompt count (only if duration didn't nudge)
                if nudge_message is None:
                    prompt_nudge = check_prompt_threshold(state, baseline, settings)
                    if prompt_nudge:
                        nudge_message = prompt_nudge.message

                # Check unusual hour (only on first prompt of session)
                if nudge_message is None and state.prompt_count == 1:
                    hour_nudge = check_unusual_hour(baseline, settings)
                    if hour_nudge:
                        nudge_message = hour_nudge.message

        # Step 6: Run sentiment checks (only if no temporal nudge)
        if nudge_message is None:
            sentiment_nudge = check_rolling_sentiment(state, settings)
            if sentiment_nudge:
                nudge_message = sentiment_nudge.message
                state.last_nudge_prompt = state.prompt_count

        # Step 7: Save session state (before output to avoid double output on failure)
        write_session_state(state)

        # Step 8: Emit nudge or empty response
        output = {"systemMessage": nudge_message} if nudge_message else {}
        print(json.dumps(output))

    except Exception as e:
        # Catch-all: log error but exit gracefully
        print(f"Error in mind-reader hook: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc(file=sys.stderr)
        print("{}")

    # Always exit 0 to avoid blocking Claude Code
    sys.exit(0)


if __name__ == "__main__":
    main()
