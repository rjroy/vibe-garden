# Waystone Plugin

AI Code Quality Audit plugin for Claude Code.

## Structure

```
waystone/
├── .claude-plugin/plugin.json    # Plugin manifest
├── commands/                     # User-invoked slash commands
│   ├── audit-init.md            # Build audit checklist
│   ├── audit-run.md             # Process checklist with agents
│   ├── audit-dead-code.md       # Find unreachable code
│   └── audit-recheck.md         # Deep-dive research on flagged files
├── agents/                       # Specialized audit agents
│   ├── structural-auditor.md    # Size, logging, tests, secrets
│   ├── semantic-auditor.md      # Code matches purpose
│   ├── api-contract-auditor.md  # Docs consulted (quick pass)
│   └── spec-tracer.md           # Links code to specs
└── skills/                       # Quality criteria loaders
    ├── quality-universal/       # Loads docs/rules/
    └── quality-project/         # Project-specific overrides
```

## Runtime Artifacts

Created in target projects at `.audit/`:
- `checklist.md` - Files to audit (from audit-init)
- `reports/` - Per-file audit findings

## Quality Rules Convention

Projects define quality rules in `docs/rules/` as markdown files. See the quality-universal skill for expected format.

## Development

When modifying agents or commands:
1. Test with `claude --plugin-dir /path/to/waystone`
2. Verify commands appear in `/help`
3. Test agents trigger appropriately
