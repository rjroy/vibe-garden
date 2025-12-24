---
version: 1.0.0
status: Approved
created: 2025-12-24
last_updated: 2025-12-24
authored_by:
  - Ronald Roy <gsdwig@gmail.com>
parent_issue: https://github.com/rjroy/vibe-garden/issues/39
---

# Compass Rose GitHub API Scripts Specification

## Executive Summary

The Compass Rose plugin currently embeds complex GraphQL queries as inline guidance within command markdown files. The LLM must interpret and execute these patterns on each invocation, leading to token waste, inconsistent execution, and frequent errors due to the complexity of GitHub's GraphQL API.

This specification defines a set of Python scripts that encapsulate GitHub Project API operations, providing reliable, tested abstractions that commands can invoke directly. The scripts will be implemented as a skill within the compass-rose plugin.

## User Story

As a developer using Compass Rose commands, I want GitHub Project operations to execute reliably without token overhead, so that commands respond faster and produce consistent results.

## Stakeholders

- **Primary**: Developers using Compass Rose for project management
- **Secondary**: Claude Code (reduced token usage, simpler command prompts)
- **Tertiary**: Plugin maintainers (reduced command complexity)

## Success Criteria

1. Commands invoke scripts instead of embedding GraphQL guidance
2. All scripts return consistent JSON output format
3. Pagination handled automatically (no manual cursor management)
4. Error messages include error code, description, and remediation steps

## Functional Requirements

### Core Scripts

- **REQ-F-1**: System provides operation to list open issues for configured project with automatic pagination
- **REQ-F-2**: System provides operation to retrieve single issue by number with full details
- **REQ-F-3**: System provides operation to update Status field of an issue by number
- **REQ-F-4**: System provides operation to add existing repository issue to configured project

### Output Format

- **REQ-F-5**: All operations return structured data with success/failure indication
- **REQ-F-6**: Issue data includes: number, title, body, url, state, labels, status, priority, size
- **REQ-F-7**: Error responses include: error code, human-readable message, and actionable details

### Configuration

- **REQ-F-8**: System reads project config from `.compass-rose/config.json`
- **REQ-F-9**: Config must specify owner type ("user" or "organization") to differentiate GitHub API endpoints
- **REQ-F-10**: System validates config presence and required fields, returning specific field violations on error

### Authentication & Error Handling

- **REQ-F-11**: System authenticates with GitHub API using existing `gh` CLI credentials
- **REQ-F-12**: System detects authentication failures and provides remediation guidance
- **REQ-F-13**: System returns specific error codes for: config missing, config invalid, issue not found, invalid status value, field not found in project
- **REQ-F-14**: System handles GitHub API rate limiting and provides retry-after information

## Non-Functional Requirements

- **REQ-NF-1** (Performance): Single-issue operations complete in under 500ms under normal network conditions
- **REQ-NF-2** (Reliability): System handles transient API failures gracefully with success rate >99% under normal conditions
- **REQ-NF-3** (Testability): All functionality verifiable through automated testing
- **REQ-NF-4** (Portability): Compatible with Python 3.12+ using only standard library

## Explicit Constraints (DO NOT)

- Do NOT require pip-installed dependencies (stdlib only)
- Do NOT cache project metadata (always fetch fresh from API)
- Do NOT implement write operations beyond status update and project-add
- Do NOT embed GraphQL queries in command markdown files (scripts replace this pattern)

## Technical Context

- **Existing Stack**: `gh` CLI for GitHub authentication, Python 3.12+
- **Integration Points**: Compass Rose command markdown files
- **Related Issue**: Replaces `gh project item-list` which silently truncates (see PR #38)
- **Existing Config**: `.compass-rose/config.json` with project.owner and project.number fields

## Acceptance Tests

1. **List Issues**: List operation returns all issues with correct fields, handles >100 items via pagination
2. **Get Single Issue**: Get operation returns issue with title, body, status, priority, size
3. **Get Invalid Issue**: Get operation returns "issue not found" error for non-existent issue number
4. **Update Status**: Update operation changes status and returns confirmation
5. **Update Invalid Status**: Update operation returns "invalid status value" error for unknown status
6. **Add to Project**: Add operation adds issue to configured project
7. **Missing Config**: Operations return "config missing" error when `.compass-rose/config.json` absent
8. **Invalid Owner Type**: Operations return "invalid config" error when owner_type not "user" or "organization"
9. **Auth Failure**: Operations detect unauthenticated `gh` and provide `gh auth login` guidance
10. **Rate Limited**: Operations return "rate limited" error with retry-after when GitHub returns 429

## Open Questions

- [x] Script location → Skill within compass-rose plugin
- [x] Org vs user projects → Explicit `owner_type` in config
- [x] API access method → Via `gh` CLI for authentication handling

## Out of Scope

- Issue creation (use `gh issue create` directly)
- Comment management
- Label management
- Milestone operations
- Cross-repository operations

---

**Next Phase**: Once approved, use `/spiral-grove:plan-generation` to create technical implementation plan.
