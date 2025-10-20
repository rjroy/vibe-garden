# Courier MCP Test Suite

Comprehensive test suite for Courier MCP covering unit tests, integration tests, and acceptance tests.

## Test Structure

```
tests/
├── conftest.py                  # Pytest fixtures and configuration
├── test_auth.py                 # Authentication module tests
├── test_gmail_service.py        # Gmail service layer tests
├── test_export.py               # Markdown export and formatting tests
├── test_server.py               # MCP server and tool handler tests
├── test_acceptance.py           # Spec acceptance criteria tests
├── test_integration.py          # Integration tests with real Gmail API (optional)
└── fixtures/                    # Test data and sample messages
```

## Running Tests

### Run All Unit Tests

```bash
cd courier-mcp
pytest -m unit
```

### Run Acceptance Tests

```bash
pytest -m acceptance
```

### Run Integration Tests (Requires Gmail Credentials)

```bash
# Set up credentials first (see docs/SETUP.md)
export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json

pytest -m integration
```

### Run All Tests

```bash
pytest
```

### Run with Coverage Report

```bash
pytest --cov=courier_mcp --cov-report=term-missing
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
pytest tests/test_gmail_service.py -v
```

### Run Specific Test

```bash
pytest tests/test_auth.py::TestGmailAuthenticator::test_init_missing_credentials_path
```

## Test Markers

Tests are organized with pytest markers:

- `@pytest.mark.unit` - Fast unit tests with mocked dependencies
- `@pytest.mark.integration` - Integration tests with real Gmail API (requires credentials)
- `@pytest.mark.acceptance` - Acceptance tests mapping to spec requirements
- `@pytest.mark.slow` - Tests that take >5 seconds to run
- `@pytest.mark.asyncio` - Async tests (automatically handled by pytest-asyncio)

### Filter by Marker

```bash
# Run only unit tests
pytest -m unit

# Run only acceptance tests
pytest -m acceptance

# Run all except slow tests
pytest -m "not slow"

# Run integration tests only if credentials available
pytest -m integration
```

## Test Coverage

Current test coverage by module:

| Module | Unit Tests | Integration Tests | Acceptance Tests |
|--------|-----------|------------------|------------------|
| auth.py | ✅ | ✅ | - |
| gmail_service.py | ✅ | ✅ | - |
| export.py | ✅ | - | ✅ |
| server.py | ✅ | ✅ | ✅ |

## Writing Tests

### Unit Test Example

```python
import pytest
from unittest.mock import MagicMock, patch

@pytest.mark.unit
def test_my_function(mock_gmail_service, temp_export_dir):
    """Test description."""
    # Arrange
    mock_gmail_service.users().labels().list().execute.return_value = {...}

    # Act
    result = my_function()

    # Assert
    assert result is not None
```

### Async Test Example

```python
import pytest

@pytest.mark.unit
@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await my_async_function()
    assert result is not None
```

### Using Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_gmail_service` - Mocked Gmail API service
- `mock_credentials` - Mocked OAuth credentials
- `temp_export_dir` - Temporary directory for file export tests
- `sample_label_list` - Sample Gmail labels.list() response
- `sample_messages_list` - Sample Gmail messages.list() response
- `sample_message_full` - Sample Gmail messages.get() response with full details
- `mock_config` - Mock configuration object

## Debugging Tests

### Run with Verbose Output

```bash
pytest -vv
```

### Show Print Statements

```bash
pytest -s
```

### Stop on First Failure

```bash
pytest -x
```

### Run Last Failed Tests

```bash
pytest --lf
```

### Debug with PDB

```bash
pytest --pdb
```

## Integration Test Setup

Integration tests require real Gmail credentials:

1. **Create Gmail Credentials**
   - Follow `docs/SETUP.md` to create OAuth credentials
   - Download `credentials.json`

2. **Set Environment Variable**
   ```bash
   export GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
   ```

3. **Run Integration Tests**
   ```bash
   pytest -m integration
   ```

4. **First Run**
   - Browser will open for OAuth flow
   - Grant access to Gmail
   - `token.pickle` is saved automatically

⚠️ **Note**: Integration tests will make real API calls to Gmail. Use a test account if possible.

## CI/CD Integration

For continuous integration:

```bash
# Run unit and acceptance tests (no credentials needed)
pytest -m "unit or acceptance"

# Generate coverage report
pytest --cov=courier_mcp --cov-report=xml --cov-report=term
```

## Acceptance Test Mapping

Acceptance tests map directly to spec requirements (`.sdd/specs/courier-mcp.md`):

| Test | Spec Requirement | File |
|------|------------------|------|
| `test_at01_basic_retrieval_10_markdown_files` | AT-1: Basic retrieval | `test_acceptance.py` |
| `test_at02_search_syntax_filtering` | AT-2: Search syntax | `test_acceptance.py` |
| `test_at03_date_filtering` | AT-3: Date filtering | `test_acceptance.py` |
| `test_at04_no_overwrites_collision_handling` | AT-4: No overwrites | `test_acceptance.py` |
| `test_at05_rate_limit_handling_within_timeout` | AT-5: Rate limit handling | `test_acceptance.py` |
| `test_at06_attachment_metadata_no_binary` | AT-6: Attachment metadata | `test_acceptance.py` |
| `test_at07_folder_discovery` | AT-7: Folder discovery | `test_acceptance.py` |
| `test_at08_timeout_resilience_partial_results` | AT-8: Timeout resilience | `test_acceptance.py` |
| `test_at09_context_efficiency_concise_output` | AT-9: Context efficiency | `test_acceptance.py` |
| `test_at10_empty_results` | AT-10: Empty results | `test_acceptance.py` |

## Troubleshooting

### Import Errors

```bash
# Install package in editable mode
pip install -e .
```

### Async Test Errors

```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio
```

### Gmail API Errors in Integration Tests

- Verify `GMAIL_CREDENTIALS_PATH` is set correctly
- Check `credentials.json` is valid JSON
- Delete `token.pickle` and re-authenticate if token is stale

## Next Steps

- Add more edge case tests
- Increase test coverage to >90%
- Add performance benchmarks
- Add mutation testing with `mutmut`
