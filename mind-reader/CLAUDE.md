# mind-reader

Analyzes Claude Code usage history to generate insights about work patterns, project focus, and interaction style.

## Usage

1. Copy `~/.claude/history.jsonl` to this directory
2. Run `/analyze` or `/analyze path/to/history.jsonl`

## Structure

```
mind-reader/
├── history.jsonl          # Input: Claude Code history
├── preprocess.py          # Splits JSONL into analysis chunks
├── analysis_chunks/       # Generated JSON files for each analysis track
│   ├── temporal.json
│   ├── projects.json
│   ├── commands.json
│   ├── sessions.json
│   ├── complexity.json
│   └── content_themes.json
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
| Themes | content_themes.json | Topics, activities, personality |

## Running Manually

```bash
# Preprocess
python3 preprocess.py

# Then use Claude to analyze chunks and generate report
```
