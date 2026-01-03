---
description: Deep-dive research on API contract for flagged file
argument-hint: <file-path>
allowed-tools: Read, Glob, Grep, Bash, WebFetch, WebSearch, Write
---

# API Contract Recheck

Perform deep research on a file flagged for recheck by the api-contract-auditor.

**Target file:** $ARGUMENTS

If no file provided:
- Check `.audit/summary.md` for files needing recheck
- List them and ask user to specify one
- Do not proceed without a specific file

## Purpose

The api-contract-auditor flagged this file as RECHECK because:
- Mixed signals about documentation evidence
- Unclear if API usage is informed or guessed
- Needs actual documentation fetch and comparison

This command does the expensive research the quick audit skipped.

## Process

### 1. Identify External APIs

Read the target file and identify all external API calls:
- Third-party library imports
- HTTP calls to external services
- SDK usage (AWS, Stripe, database clients, etc.)

For each API, note:
- Library/service name
- Specific methods/endpoints called
- Error handling patterns used
- Return type handling

### 2. Fetch Documentation

For each identified API:

**Check local docs first:**
- Look in `docs/research/` for cached documentation
- Check if documentation is less than 1 week old

**Fetch if needed:**
- Use WebSearch to find official documentation
- Use WebFetch to retrieve relevant pages
- Focus on:
  - Method signatures
  - Return types
  - Error types and codes
  - Rate limits
  - Authentication requirements

**Cache fetched docs:**
- Save to `docs/research/[api-name].md`
- Include frontmatter with download date

### 3. Compare Implementation

For each API call in the code, compare against documentation:

**Check error handling:**
- Does code handle documented error types?
- Are error codes matched correctly?
- Is retry logic appropriate for error category?

**Check return types:**
- Are response types handled correctly?
- Is null/undefined handling aligned with docs?
- Are optional fields treated as optional?

**Check authentication:**
- Is auth configured per documentation?
- Are required headers/tokens included?

**Check rate limits:**
- Is rate limiting implemented if documented?
- Are backoff strategies appropriate?

### 4. Identify Discrepancies

For each mismatch, categorize:

**Critical:**
- Error handling doesn't match documented errors
- Return type assumptions are wrong
- Authentication is incorrect

**Warning:**
- Rate limiting not implemented but documented
- Optional fields treated as required
- Deprecated methods in use

**Advisory:**
- Could use more specific error types
- Documentation suggests better patterns

### 5. Generate Detailed Report

Create report at `.audit/recheck/[file-hash].md`:

```markdown
# API Contract Recheck: [file path]

Analyzed: [timestamp]
APIs Found: [count]
Discrepancies: [count]

## APIs Analyzed

### [API Name 1]
**Documentation Source:** [URL or local path]
**Methods Used:**
- `methodName()` at line N

**Documentation Says:**
- Returns: [type]
- Errors: [error types]
- Rate Limit: [if any]

**Implementation Does:**
- Handles errors: [how]
- Handles return: [how]

**Verdict:** ALIGNED | MISALIGNED | PARTIAL

**Issues:**
- Line N: [specific issue]

### [API Name 2]
[repeat structure]

## Summary

| API | Verdict | Critical | Warnings |
|-----|---------|----------|----------|
| Stripe | PARTIAL | 1 | 2 |
| AWS S3 | ALIGNED | 0 | 1 |

## Recommendations

1. [Priority action with file:line reference]
2. [Secondary action]
3. [Nice to have]

## Documentation Cached

New documentation saved to:
- docs/research/stripe-api.md
- docs/research/aws-s3.md
```

## Output

After analysis:
1. Report verdict for each API
2. Highlight critical discrepancies
3. Show path to detailed report
4. Update `.audit/checklist.md` to mark file as rechecked

## Limitations

**Private/internal APIs:**
- Cannot fetch documentation for internal services
- Note as "documentation not available"
- Recommend internal documentation be created

**Rapidly changing APIs:**
- Documentation may be outdated
- Note version checked against
- Recommend version pinning

**Complex SDKs:**
- May not catch all method calls
- Focus on primary usage patterns
- Note coverage level in report

## Context Management

This command intentionally processes ONE file at a time because:
- Documentation fetching is expensive
- Each API needs thorough analysis
- Context window must hold code + docs + analysis

If multiple files need recheck, run command once per file.
