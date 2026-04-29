# Tags Mode Reference

Audit tag consistency and related document links across `.lore/`.

## Purpose

Tags are the semantic spine of lore. They enable discovery, connect related work, and reveal natural clusters. Tag hygiene ensures the lore-researcher can find what matters.

## Checks

### Tag Consistency

Look for similar tags that should unify:

| Pattern | Problem | Action |
|---------|---------|--------|
| `auth`, `authentication`, `authn` | Same concept, different names | Unify to one (prefer shortest clear form) |
| `api`, `apis`, `api-design` | Plural vs singular inconsistency | Standardize to singular |
| `web-socket`, `websocket`, `ws` | Formatting inconsistency | Use kebab-case form |
| `perf`, `performance` | Abbreviation vs full word | Pick one, use consistently |

**Process**:
1. Extract all unique tags from `.lore/` documents
2. Group by semantic similarity (Levenshtein distance, shared prefixes, known synonyms)
3. Flag groups with multiple variants
4. Suggest canonical form for each group

### Related Links Audit

Documents sharing 3+ tags likely should be linked:

1. Build tag-to-document index
2. For each document pair, count shared tags
3. If shared tags >= 3 and no `related:` link exists, flag for review
4. Present as "potential connections"

**Why 3?** One shared tag is coincidence. Two might be correlation. Three suggests a relationship worth making explicit.

### Tag Clusters

Identify natural groupings by co-occurrence:

1. Build co-occurrence matrix (which tags appear together)
2. Identify high-frequency pairs/triples
3. Name emergent clusters
4. Report clusters for user awareness

Example output:
```
Cluster: "auth-related"
  Tags: auth, security, login, session, oauth
  Documents: 8

Cluster: "performance"
  Tags: performance, optimization, caching, database
  Documents: 5
```

Clusters inform directory organization (see directories mode).

## Output Report

```markdown
## Tags Report

### Tag Variants (should unify)
| Variants | Occurrences | Suggested |
|----------|-------------|-----------|
| auth, authentication, authn | 12 | auth |
| api, apis | 5 | api |

### Potential Connections (3+ shared tags, no link)
| Document A | Document B | Shared Tags |
|------------|------------|-------------|
| specs/auth-flow.md | research/oauth-patterns.md | auth, security, login |
| brainstorm/caching.md | specs/performance.md | caching, performance, optimization |

### Tag Clusters
| Cluster | Tags | Document Count |
|---------|------|----------------|
| auth-related | auth, security, login, session | 8 |
| data-layer | database, query, model, schema | 6 |

### Low-Value Tags (used only once)
- `temp-fix` (specs/quick-patch.md)
- `experimental-feature` (brainstorm/wild-idea.md)
```

## Applying Changes

**Tag unification** requires document edits:
1. Present unified tag mapping to user
2. On confirmation, update all affected documents
3. Use Edit tool to replace old tag with canonical form in frontmatter

**Adding related links**:
1. Present potential connections
2. User confirms which should be linked
3. Add `related:` field or append to existing list

**Low-value tags**: Informational only. Single-use tags aren't necessarily wrong (they might be for a unique topic). Flag but don't auto-remove.

## Pass-by-pass Execution

Tags mode works in passes:

1. **Scan pass**: Extract all tags, build indices
2. **Analysis pass**: Find variants, connections, clusters
3. **Report pass**: Present findings organized by category
4. **Apply pass**: Make confirmed changes

Use TaskCreate for each pass. Don't collapse analysis and application.
