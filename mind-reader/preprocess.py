#!/usr/bin/env python3
"""Preprocess history.jsonl into analysis-ready chunks."""

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import re

INPUT_FILE = Path("history.jsonl")
OUTPUT_DIR = Path("analysis_chunks")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_entries():
    with open(INPUT_FILE) as f:
        return [json.loads(line) for line in f]


def analyze_temporal(entries):
    """Extract temporal patterns."""
    data = {
        "by_hour": Counter(),
        "by_day_of_week": Counter(),
        "by_date": Counter(),
        "by_week": Counter(),
    }

    for e in entries:
        dt = datetime.fromtimestamp(e["timestamp"] / 1000)
        data["by_hour"][dt.hour] += 1
        data["by_day_of_week"][dt.strftime("%A")] += 1
        data["by_date"][dt.strftime("%Y-%m-%d")] += 1
        data["by_week"][dt.strftime("%Y-W%W")] += 1

    # Convert to sorted lists for JSON
    return {
        "by_hour": dict(sorted(data["by_hour"].items())),
        "by_day_of_week": dict(data["by_day_of_week"]),
        "by_date": dict(sorted(data["by_date"].items())),
        "by_week": dict(sorted(data["by_week"].items())),
        "total_entries": len(entries),
        "date_range": {
            "start": min(e["timestamp"] for e in entries),
            "end": max(e["timestamp"] for e in entries),
        }
    }


def analyze_projects(entries):
    """Extract project-level patterns."""
    project_data = defaultdict(lambda: {
        "count": 0,
        "prompts": [],
        "first_seen": float("inf"),
        "last_seen": 0,
    })

    for e in entries:
        proj = e.get("project", "unknown")
        # Normalize project path to just the name
        proj_name = Path(proj).name if proj else "unknown"

        project_data[proj_name]["count"] += 1
        project_data[proj_name]["prompts"].append(e["display"][:200])  # Truncate for size
        project_data[proj_name]["first_seen"] = min(
            project_data[proj_name]["first_seen"], e["timestamp"]
        )
        project_data[proj_name]["last_seen"] = max(
            project_data[proj_name]["last_seen"], e["timestamp"]
        )

    # Convert and limit prompts sample
    result = {}
    for name, data in project_data.items():
        result[name] = {
            "count": data["count"],
            "sample_prompts": data["prompts"][:50],  # Keep 50 samples
            "first_seen": datetime.fromtimestamp(data["first_seen"] / 1000).isoformat(),
            "last_seen": datetime.fromtimestamp(data["last_seen"] / 1000).isoformat(),
        }

    return dict(sorted(result.items(), key=lambda x: -x[1]["count"]))


def analyze_commands(entries):
    """Categorize and count command patterns."""
    patterns = {
        "slash_commands": Counter(),
        "bang_commands": Counter(),
        "file_references": Counter(),
        "natural_language": [],
        "short_responses": [],  # yes, no, ok, etc.
    }

    for e in entries:
        display = e["display"]

        # Slash commands
        if display.startswith("/"):
            cmd = display.split()[0] if display.split() else display
            patterns["slash_commands"][cmd] += 1
        # Bang commands
        elif display.startswith("!"):
            cmd = display.split()[0] if display.split() else display
            patterns["bang_commands"][cmd] += 1
        # File references
        elif "@" in display:
            # Extract @file patterns
            refs = re.findall(r"@[\w./\-]+", display)
            for ref in refs:
                patterns["file_references"][ref] += 1
            patterns["natural_language"].append(display[:300])
        # Short responses
        elif len(display) < 20:
            patterns["short_responses"].append(display)
        else:
            patterns["natural_language"].append(display[:300])

    return {
        "slash_commands": dict(patterns["slash_commands"].most_common(50)),
        "bang_commands": dict(patterns["bang_commands"].most_common(20)),
        "file_references": dict(patterns["file_references"].most_common(30)),
        "short_responses": Counter(patterns["short_responses"]).most_common(50),
        "natural_language_sample": patterns["natural_language"][:100],
        "natural_language_count": len(patterns["natural_language"]),
    }


def analyze_sessions(entries):
    """Analyze session-level patterns."""
    sessions = defaultdict(list)
    no_session = []

    for e in entries:
        sid = e.get("sessionId")
        if sid:
            sessions[sid].append(e)
        else:
            no_session.append(e)

    session_stats = []
    for sid, sess_entries in sessions.items():
        sess_entries.sort(key=lambda x: x["timestamp"])
        duration_ms = sess_entries[-1]["timestamp"] - sess_entries[0]["timestamp"]
        session_stats.append({
            "session_id": sid[:8],  # Truncate for readability
            "prompt_count": len(sess_entries),
            "duration_minutes": round(duration_ms / 1000 / 60, 1),
            "project": Path(sess_entries[0].get("project", "unknown")).name,
            "first_prompt": sess_entries[0]["display"][:100],
            "prompts_sample": [e["display"][:100] for e in sess_entries[:10]],
        })

    session_stats.sort(key=lambda x: -x["prompt_count"])

    return {
        "total_sessions": len(sessions),
        "entries_without_session": len(no_session),
        "avg_prompts_per_session": round(
            sum(s["prompt_count"] for s in session_stats) / len(session_stats), 1
        ) if session_stats else 0,
        "avg_duration_minutes": round(
            sum(s["duration_minutes"] for s in session_stats) / len(session_stats), 1
        ) if session_stats else 0,
        "longest_sessions": session_stats[:20],
        "session_size_distribution": Counter(
            "1-5" if s["prompt_count"] <= 5 else
            "6-15" if s["prompt_count"] <= 15 else
            "16-30" if s["prompt_count"] <= 30 else
            "31-50" if s["prompt_count"] <= 50 else
            "50+"
            for s in session_stats
        ),
    }


def analyze_complexity(entries):
    """Analyze prompt complexity."""
    lengths = [len(e["display"]) for e in entries]

    complexity_data = {
        "length_stats": {
            "min": min(lengths),
            "max": max(lengths),
            "avg": round(sum(lengths) / len(lengths), 1),
            "median": sorted(lengths)[len(lengths) // 2],
        },
        "length_buckets": Counter(
            "tiny (<10)" if l < 10 else
            "short (10-50)" if l < 50 else
            "medium (50-200)" if l < 200 else
            "long (200-500)" if l < 500 else
            "very_long (500+)"
            for l in lengths
        ),
        "with_file_refs": sum(1 for e in entries if "@" in e["display"]),
        "with_code_blocks": sum(1 for e in entries if "```" in e["display"]),
        "longest_prompts": [
            {"length": len(e["display"]), "preview": e["display"][:500], "project": Path(e.get("project", "")).name}
            for e in sorted(entries, key=lambda x: -len(x["display"]))[:10]
        ],
    }

    return complexity_data


def analyze_content_themes(entries):
    """Extract content themes from prompts."""
    # Sample diverse prompts for theme analysis
    long_prompts = [e for e in entries if len(e["display"]) > 50]

    # Group by apparent intent
    themes = {
        "questions": [],
        "commands": [],
        "continuations": [],
        "reviews": [],
        "file_work": [],
        "debugging": [],
        "other": [],
    }

    keywords = {
        "questions": ["?", "how", "what", "why", "can you", "does", "is there"],
        "commands": ["create", "add", "remove", "delete", "update", "fix", "implement", "write"],
        "continuations": ["continue", "yes", "ok", "proceed", "go ahead", "do it"],
        "reviews": ["review", "check", "look at", "analyze"],
        "file_work": ["@", "file", "read", "edit"],
        "debugging": ["error", "bug", "fix", "broken", "not working", "fail"],
    }

    for e in entries:
        display = e["display"].lower()
        categorized = False

        for theme, kws in keywords.items():
            if any(kw in display for kw in kws):
                themes[theme].append(e["display"][:200])
                categorized = True
                break

        if not categorized:
            themes["other"].append(e["display"][:200])

    return {
        "theme_counts": {k: len(v) for k, v in themes.items()},
        "theme_samples": {k: v[:30] for k, v in themes.items()},
        "all_prompts_sample": [e["display"] for e in long_prompts[:150]],
    }


def main():
    print("Loading entries...")
    entries = load_entries()
    print(f"Loaded {len(entries)} entries")

    analyses = [
        ("temporal", analyze_temporal),
        ("projects", analyze_projects),
        ("commands", analyze_commands),
        ("sessions", analyze_sessions),
        ("complexity", analyze_complexity),
        ("content_themes", analyze_content_themes),
    ]

    for name, func in analyses:
        print(f"Running {name} analysis...")
        result = func(entries)
        output_path = OUTPUT_DIR / f"{name}.json"
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  -> {output_path}")

    print("Done!")


if __name__ == "__main__":
    main()
