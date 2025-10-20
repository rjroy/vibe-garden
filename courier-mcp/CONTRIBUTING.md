# Contributing to Courier MCP

Thank you for considering contributing to Courier MCP! This guide will help you get started.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Running Tests](#running-tests)
4. [Code Style](#code-style)
5. [Making Changes](#making-changes)
6. [Pull Request Process](#pull-request-process)
7. [Reporting Bugs](#reporting-bugs)
8. [Feature Requests](#feature-requests)

---

## Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Git**: Latest version
- **Gmail Account**: For testing
- **Google Cloud Project**: With Gmail API enabled

### Clone Repository

```bash
git clone https://github.com/rjroy/vibe-garden.git
cd vibe-garden/courier-mcp
```

### Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv server/venv

# Activate (Linux/macOS)
source server/venv/bin/activate

# Activate (Windows)
server\venv\Scripts\activate

# Install dependencies (editable mode)
pip install -e .
```

### Configure OAuth Credentials

Follow [docs/SETUP.md](docs/SETUP.md) to set up Gmail OAuth:

1. Create Google Cloud project
2. Enable Gmail API
3. Download `credentials.json`
4. Set environment variable:
   ```bash
   export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
   ```

### Verify Installation

```bash
# Test imports
python -c "import courier_mcp; print('OK')"

# Run tests
pytest tests/ -v

# Run server manually
python -m courier_mcp
```

---

## Project Structure

```
courier-mcp/
├── .claude-plugin/           # Claude Code plugin manifest
│   └── plugin.json
├── server/
│   ├── src/courier_mcp/      # Main source code
│   │   ├── __init__.py
│   │   ├── __main__.py       # Entry point
│   │   ├── server.py         # MCP server & tool handlers
│   │   ├── config.py         # Configuration management
│   │   ├── auth.py           # OAuth authentication
│   │   ├── gmail_service.py  # Gmail API service layer
│   │   ├── export.py         # Markdown formatting & file writes
│   │   ├── errors.py         # Exception classes
│   │   └── logger.py         # Logging utilities
│   ├── scripts/              # Launcher scripts
│   │   └── courier.sh        # MCP server launcher
│   ├── tests/                # Test suite
│   │   ├── conftest.py       # Pytest fixtures
│   │   ├── test_auth.py      # Authentication tests
│   │   ├── test_config.py    # Configuration tests
│   │   ├── test_gmail_service.py  # Gmail service tests
│   │   ├── test_export.py    # Export/formatting tests
│   │   ├── test_server.py    # MCP server tests
│   │   ├── test_acceptance.py     # Spec acceptance tests
│   │   └── test_integration.py    # Integration tests (optional)
│   ├── setup.py              # Package configuration
│   ├── requirements.txt      # Production dependencies
│   └── requirements-dev.txt  # Development dependencies
├── docs/                     # Documentation
│   ├── SETUP.md
│   ├── USAGE.md
│   ├── API.md
│   ├── TROUBLESHOOTING.md
│   └── E2E_TEST_RESULTS.md
├── skills/                   # Claude Skills
│   └── courier-setup-helper/
│       └── SKILL.md
├── courier.config            # Default configuration (YAML)
├── pytest.ini                # Pytest configuration
├── README.md                 # Main documentation
└── CONTRIBUTING.md           # This file
```

---

## Running Tests

### All Tests

```bash
pytest tests/ -v
```

### Unit Tests Only

```bash
pytest tests/ -v -m unit
```

### Acceptance Tests

```bash
pytest tests/test_acceptance.py -v
```

### Integration Tests (Requires Gmail Credentials)

```bash
# Set credentials first
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

# Run integration tests
pytest tests/ -v -m integration
```

### With Coverage

```bash
pytest tests/ --cov=courier_mcp --cov-report=html
# View coverage: open htmlcov/index.html
```

### Test Markers

- `unit`: Unit tests (no external dependencies)
- `integration`: Integration tests (requires Gmail API)
- `acceptance`: Acceptance tests (map to spec requirements)
- `slow`: Slow tests (> 1 second)

---

## Code Style

### Python Style Guide

Follow **PEP 8** with these tools:

```bash
# Format code (Black)
black server/src/

# Lint code (Pylint)
pylint server/src/courier_mcp/

# Type checking (MyPy)
mypy server/src/courier_mcp/
```

### Code Conventions

1. **Type Hints**: Use type annotations for all functions
   ```python
   def fetch_messages(
       self,
       search_query: str,
       label_id: str | None = None,
       max_results: int = 10
   ) -> list[Message]:
       ...
   ```

2. **Docstrings**: Use Google-style docstrings
   ```python
   def format_message(message: dict[str, Any]) -> str:
       """Format Gmail message to markdown with YAML frontmatter.

       Args:
           message: Gmail API message dict with full payload

       Returns:
           Markdown string with YAML frontmatter

       Raises:
           ExportError: If message format is invalid
       """
       ...
   ```

3. **Error Handling**: Use custom exception classes
   ```python
   # Good
   raise AuthenticationError("Invalid credentials")

   # Bad
   raise Exception("Invalid credentials")
   ```

4. **Logging**: Use structured logging
   ```python
   logger.info(f"Exported {count} messages in {duration}s")
   logger.debug(f"Message ID: {message_id}, Size: {size} bytes")
   logger.error(f"Failed to fetch message {message_id}: {error}")
   ```

5. **Async/Await**: Use async for I/O-bound operations
   ```python
   async def fetch_message_details(self, message_ids: list[str]) -> tuple[list[dict], list[dict]]:
       tasks = [self._fetch_single_message(msg_id) for msg_id in message_ids]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       ...
   ```

---

## Making Changes

### Branching Strategy

All work is done on feature branches following the vibe-garden conventions:

1. **Design Phase Branches** (Spec, Plan, Breakdown):
   - Branch name: `<project>-design`
   - Example: `courier-mcp-design`

2. **Implementation Phase Branches** (Task Execution):
   - Branch name: `<feature>-tasks`
   - Example: `courier-mcp-tasks`

3. **General Maintenance Branches**:
   - Branch name: `vibe-garden-update-YYYY-MM-DD`
   - Example: `vibe-garden-update-2025-10-19`

### Workflow

```bash
# Create feature branch
git checkout -b my-feature-tasks

# Make changes
# ...

# Run tests
pytest tests/ -v

# Format code
black server/src/

# Commit changes
git add .
git commit -m "Add feature X"

# Push branch
git push origin my-feature-tasks

# Create pull request on GitHub
```

### Commit Messages

Follow conventional commit format:

```
<type>: <description>

<body (optional)>

🤖 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code restructuring (no behavior change)
- `perf`: Performance improvement
- `chore`: Maintenance tasks

**Examples**:
```
feat: Add attachment metadata extraction

fix: Resolve config initialization bug (BUG-001)

docs: Update SETUP.md with Windows instructions

test: Add acceptance tests for spec AT-01 through AT-10
```

---

## Pull Request Process

### Before Submitting

1. **Run all tests**: `pytest tests/ -v`
2. **Check code style**: `black --check server/src/`
3. **Update documentation** if needed
4. **Add tests** for new features
5. **Update CHANGELOG** (if exists)

### PR Template

```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Test improvement

## Testing
- [ ] All tests pass
- [ ] Added new tests (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Docstrings added/updated
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

### Review Process

1. **Automated checks**: GitHub Actions run tests and linters
2. **Code review**: Maintainer reviews code
3. **Requested changes**: Address feedback
4. **Approval**: Maintainer approves PR
5. **Merge**: Squash and merge to main

---

## Reporting Bugs

### Bug Report Template

Use [GitHub Issues](https://github.com/rjroy/vibe-garden/issues/new) with this format:

```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Error Message
```json
{
  "error": "...",
  "message": "..."
}
```

## Environment
- OS: Linux/macOS/Windows
- Python Version: 3.10/3.11/3.12
- Courier MCP Version: 1.1.0
- Gmail Account Type: Personal/Workspace

## Logs
```
[Last 50 lines from courier-mcp.log]
```

## Additional Context
Any other relevant information
```

### Security Issues

For security vulnerabilities, **do not** open a public issue. Email: gsdwig@gmail.com

---

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
What feature would you like to see?

## Use Case
Why is this feature needed? How will it be used?

## Proposed Solution
How do you think it should work?

## Alternatives Considered
Any alternative solutions you've thought about?

## Additional Context
Screenshots, examples, etc.
```

### Roadmap

See [README.md - Roadmap](README.md#roadmap-v20) for planned features.

---

## Development Tips

### Debugging

```bash
# Run server with debug logging
export COURIER_LOG_LEVEL=DEBUG
python -m courier_mcp

# Monitor logs in real-time
tail -f courier-mcp.log

# Use breakpoints (pdb)
import pdb; pdb.set_trace()
```

### Testing Specific Functions

```python
# Test single function
pytest tests/test_export.py::TestMessageFormatting::test_format_message_to_markdown -v

# Test with print statements
pytest tests/ -v -s

# Re-run failed tests
pytest --lf
```

### Mocking Gmail API

See `tests/conftest.py` for fixture examples:

```python
@pytest.fixture
def mock_gmail_service(mocker):
    """Mock Gmail API service."""
    mock = mocker.Mock()
    mock.users().labels().list().execute.return_value = {...}
    return mock
```

---

## Release Process

(For maintainers)

1. Update version in `setup.py` and `plugin.json`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Tag release: `git tag -a v1.2.0 -m "Release v1.2.0"`
5. Push tag: `git push origin v1.2.0`
6. Create GitHub release with changelog
7. Announce in discussions

---

## Questions?

- **Documentation**: [docs/](docs/)
- **GitHub Discussions**: [github.com/rjroy/vibe-garden/discussions](https://github.com/rjroy/vibe-garden/discussions)
- **Issues**: [github.com/rjroy/vibe-garden/issues](https://github.com/rjroy/vibe-garden/issues)
- **Email**: gsdwig@gmail.com

---

**Thank you for contributing to Courier MCP! 🚀**
