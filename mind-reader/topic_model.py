#!/usr/bin/env python3
"""Topic modeling for Claude Code usage history using BERTopic."""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from bertopic import BERTopic

INPUT_FILE = Path("history.jsonl")
OUTPUT_DIR = Path("analysis_chunks")
OUTPUT_FILE = OUTPUT_DIR / "topics.json"


def load_entries():
    """Load all entries from history.jsonl."""
    with open(INPUT_FILE) as f:
        return [json.loads(line) for line in f]


def filter_prompts(entries: list[dict]) -> tuple[list[str], list[str]]:
    """Filter to meaningful prompts for topic modeling.

    Returns:
        Tuple of (prompts, timestamps_as_weeks)
    """
    prompts = []
    weeks = []

    for e in entries:
        text = e["display"]

        # Skip slash commands - they're structural, not semantic
        if text.startswith("/"):
            continue

        # Skip very short responses (yes, no, ok, etc.)
        if len(text) < 20:
            continue

        # Skip bang commands
        if text.startswith("!"):
            continue

        prompts.append(text)

        # Convert timestamp to week for topic-over-time
        dt = datetime.fromtimestamp(e["timestamp"] / 1000)
        weeks.append(dt.strftime("%Y-W%W"))

    return prompts, weeks


def run_topic_modeling(prompts: list[str], weeks: list[str]) -> dict:
    """Run BERTopic and extract results."""
    print(f"Running BERTopic on {len(prompts)} prompts...")

    # Initialize BERTopic with reasonable defaults
    # Using a smaller embedding model for speed
    topic_model = BERTopic(
        embedding_model="all-MiniLM-L6-v2",
        min_topic_size=10,
        verbose=True,
    )

    # Fit the model
    topics, probs = topic_model.fit_transform(prompts)

    # Get topic info
    topic_info = topic_model.get_topic_info()

    # Build topics list
    topics_list = []
    for _, row in topic_info.iterrows():
        topic_id = row["Topic"]

        # Skip outlier topic (-1)
        if topic_id == -1:
            continue

        # Get keywords for this topic
        topic_words = topic_model.get_topic(topic_id)
        keywords = [word for word, _ in topic_words[:10]]

        # Get representative documents
        rep_docs = topic_model.get_representative_docs(topic_id)

        topics_list.append({
            "id": int(topic_id),
            "label": row.get("Name", f"Topic {topic_id}"),
            "count": int(row["Count"]),
            "keywords": keywords,
            "representative_docs": rep_docs[:5] if rep_docs else [],
        })

    # Calculate topic over time
    topic_over_time = calculate_topic_over_time(topics, weeks)

    # Count outliers
    outlier_count = sum(1 for t in topics if t == -1)

    return {
        "model_info": {
            "num_topics": len(topics_list),
            "num_documents": len(prompts),
            "outlier_count": outlier_count,
            "embedding_model": "all-MiniLM-L6-v2",
        },
        "topics": sorted(topics_list, key=lambda x: -x["count"]),
        "topic_over_time": topic_over_time,
    }


def calculate_topic_over_time(
    topics: list[int], weeks: list[str]
) -> dict[str, dict[str, int]]:
    """Calculate topic distribution per week."""
    weekly_topics: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for topic_id, week in zip(topics, weeks, strict=True):
        if topic_id == -1:  # Skip outliers
            continue
        weekly_topics[week][f"topic_{topic_id}"] += 1

    # Convert to regular dict and sort by week
    return {
        week: dict(topics)
        for week, topics in sorted(weekly_topics.items())
    }


def main():
    print("Loading entries...")
    entries = load_entries()
    print(f"Loaded {len(entries)} entries")

    prompts, weeks = filter_prompts(entries)
    print(f"Filtered to {len(prompts)} meaningful prompts")

    if len(prompts) < 50:
        print("Warning: Too few prompts for meaningful topic modeling")
        return

    OUTPUT_DIR.mkdir(exist_ok=True)

    results = run_topic_modeling(prompts, weeks)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {OUTPUT_FILE}")
    print(f"Discovered {results['model_info']['num_topics']} topics")
    print(f"Outliers: {results['model_info']['outlier_count']}")

    # Print top topics
    print("\nTop 5 topics:")
    for topic in results["topics"][:5]:
        print(f"  {topic['label']}: {topic['count']} docs")
        print(f"    Keywords: {', '.join(topic['keywords'][:5])}")


if __name__ == "__main__":
    main()
