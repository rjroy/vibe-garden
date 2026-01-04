# mind-reader

Analyzes Claude Code usage history to generate insights about work patterns, project focus, and interaction style.

## Usage

1. Copy `~/.claude/history.jsonl` to this directory
2. Install dependencies: `uv sync --group ml`
3. Run `/analyze` or `/analyze path/to/history.jsonl`

## Structure

```
mind-reader/
├── history.jsonl          # Input: Claude Code history
├── preprocess.py          # Splits JSONL into analysis chunks (fast, no deps)
├── topic_model.py         # BERTopic topic modeling (requires ml group)
├── analysis_chunks/       # Generated JSON files for each analysis track
│   ├── temporal.json
│   ├── projects.json
│   ├── commands.json
│   ├── sessions.json
│   ├── complexity.json
│   └── topics.json        # BERTopic discovered topics
└── USAGE_REPORT.md        # Output: Generated insights report
```

## Analysis Dimensions

| Track | File | Questions Answered |
|-------|------|-------------------|
| Temporal | temporal.json | Peak hours, day-of-week, trends |
| Projects | projects.json | Focus areas, project types, lifecycle |
| Commands | commands.json | Slash commands, file refs, style |
| Sessions | sessions.json | Length, depth, workflow patterns |
| Complexity | complexity.json | Prompt length, verbosity triggers |
| Topics | topics.json | BERTopic clusters, topic evolution over time |

## Running Manually

```bash
# Install ML dependencies (one-time)
uv sync --group ml

# Preprocess (fast, basic statistics)
python3 preprocess.py

# Topic modeling (slower, requires ML deps)
python3 topic_model.py

# Then use Claude to analyze chunks and generate report
```

## Dependencies

The project uses dependency groups to keep the base install light:
- **dev**: pytest, ruff (for development)
- **ml**: bertopic, sentence-transformers (for topic modeling)

Topic modeling pulls in torch and transformers, which are large (~1GB+). Only install if you want topic analysis.
