# The Five Pillars of Code Quality

Detailed explanation of each quality pillar, including rationale, detection methods, and common violations.

## 1. Code Review Discipline

**Why this matters:** Code review is the bedrock of quality. Without it, every other pillar erodes. Review catches bugs, spreads knowledge, and enforces standards.

### Detection Methods

**Git history analysis:**
```bash
# Check for direct commits to main
git log --first-parent main --format="%h %s" | head -20

# Look for merge commits (indicates PR workflow)
git log --merges --oneline | head -10

# Check if commits reference issues
git log --oneline | grep -E "#[0-9]+" | wc -l
```

**Branch protection indicators:**
- `.github/` directory with workflows
- Branch protection rules in repo settings
- Pre-commit hooks in `.husky/` or `.git/hooks/`

### Common Violations

- "Quick fix" commits directly to main
- Commits with messages like "fix", "update", "wip"
- No issue/PR references in commit history
- Large commits that bundle unrelated changes

### Remediation

- Enable branch protection on main
- Require PR reviews before merge
- Use commit message templates
- Link commits to issues via conventional commits

---

## 2. Test Coverage

**Why this matters:** Coverage percentage is measurable. When code is structured for testability (small functions, single responsibility), tests that exercise the code are meaningful by definition.

### Detection Methods

**Test file presence:**
```bash
# Find source files without corresponding test files
find src -name "*.ts" | while read f; do
  test_file=$(echo "$f" | sed 's/src/tests/' | sed 's/.ts/.test.ts/')
  [ ! -f "$test_file" ] && echo "Missing: $test_file"
done
```

**Coverage tools:**
- Jest with `--coverage`
- pytest with `pytest-cov`
- Go with `go test -cover`

### Coverage Targets

| Type | Target | Rationale |
|------|--------|-----------|
| Unit tests | 80%+ | Core logic must be tested |
| Integration tests | Key paths | Golden path + known edge cases |
| Error paths | Explicit | Each catch block should have a test |

### Common Violations

- Tests that only exercise happy paths
- Tests that assert on implementation details, not behavior
- Mock-heavy tests that don't verify real integration
- Snapshot tests that are auto-accepted without review

### Test Quality Indicators

**Good test:**
```typescript
test('returns error when user not found', async () => {
  const result = await getUser('nonexistent');
  expect(result.error).toBe('USER_NOT_FOUND');
});
```

**Poor test (structural, not behavioral):**
```typescript
test('calls database', async () => {
  await getUser('any');
  expect(mockDb.query).toHaveBeenCalled();
});
```

---

## 3. Cohesion and Size

**Why this matters:** Large functions and files are harder to understand, test, and modify. Size limits are heuristics that prompt investigation, not hard rules.

### Size Thresholds

| Unit | Investigate If | Hard Limit |
|------|----------------|------------|
| Function | >100 lines | >200 lines |
| File | >800 lines | >1500 lines |
| Class | >500 lines | >1000 lines |

### Detection Methods

```bash
# Count lines per function (approximate via blank line separation)
awk '/^function|^const.*=.*=>|^async function/{name=$0} /^}/{if(NR-start>100)print name, NR-start; start=NR}' file.ts

# Count file lines
wc -l src/**/*.ts | sort -n | tail -20
```

### Acceptable Exceptions

Size limits can be exceeded when:
- The file is a data definition (constants, config)
- The function is a state machine with many cases
- Splitting would obscure the logic flow
- A comment explains why the size is justified

### Common Violations

- "God classes" that do everything
- Utility files that accumulate unrelated functions
- Functions that grew through feature additions
- Copy-paste duplication inflating size

---

## 4. Self-Documenting Code

**Why this matters:** Code is read far more often than written. Clear code reduces onboarding time, prevents bugs, and makes reviews faster.

### Detection Methods

**Naming analysis:**
- Function names should be verbs (getUser, validateInput)
- Boolean variables should be questions (isValid, hasAccess)
- Avoid abbreviations (usr → user, cfg → config)

**Comment analysis:**
```bash
# Find TODO/FIXME comments
grep -rn "TODO\|FIXME" src/

# Find comments older than 6 months (requires git blame)
git blame src/file.ts | grep -E "TODO|FIXME"
```

### When Comments Are Needed

**Required:**
- Business logic not obvious from code
- Workarounds for bugs in dependencies
- Performance optimizations that sacrifice clarity
- Regex patterns and complex algorithms

**Not needed:**
- Obvious code (// increment counter)
- Function signature documentation for trivial functions
- Change history (use git)

### Common Violations

- Function named `process` or `handle` (what does it process?)
- Variables named `data`, `result`, `temp`
- Comments that describe what, not why
- Outdated comments that contradict the code

---

## 5. Reproducible Builds

**Why this matters:** A build should produce the same output given the same input. Non-determinism makes debugging impossible and deployments risky.

### Detection Methods

**Lock file presence:**
```bash
# Check for lock files
ls -la package-lock.json yarn.lock pnpm-lock.yaml uv.lock Cargo.lock go.sum 2>/dev/null
```

**Build documentation:**
```bash
# Check README for build instructions
grep -i "build\|install\|setup" README.md
```

**CI configuration:**
```bash
# Check for CI files
ls -la .github/workflows/ .gitlab-ci.yml .circleci/ Jenkinsfile 2>/dev/null
```

### Common Violations

- Dependencies specified with `^` or `~` ranges without lock file
- Build depends on global tools not in package.json
- Different results on CI vs local
- Missing environment variable documentation

### Remediation

- Always commit lock files
- Use exact versions in production dependencies
- Document all environment variables in README
- Test builds in clean environments (Docker, CI)

---

## Pillar Interactions

The pillars reinforce each other:

- **Small, cohesive functions** → easier to test → better coverage
- **Self-documenting code** → faster reviews → better review discipline
- **Reproducible builds** → CI can run tests → coverage stays current
- **Code review** → catches violations of all pillars → maintains quality

Code review sits at the top because it's how you verify everything else.
