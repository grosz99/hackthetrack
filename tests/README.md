# Backend Test Suite

## Quick Reference

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Files
```bash
# Deployment readiness
pytest tests/test_deployment_readiness.py -v

# Snowflake integration
pytest tests/test_snowflake_integration.py -v

# API endpoints
pytest tests/test_telemetry_endpoints.py -v
```

### Run by Category
```bash
# Unit tests only (fast)
pytest tests/ -m "not integration" -v

# Integration tests only (requires Snowflake)
pytest tests/ -m integration -v
```

### Pre-Deployment Validation
```bash
# Full validation
python scripts/pre_deployment_check.py

# Skip integration tests
python scripts/pre_deployment_check.py --skip-integration
```

## Test Files

### `test_deployment_readiness.py`
Validates system is ready for production deployment:
- Environment variables configured
- Snowflake connection works
- Database schema exists
- Telemetry data present
- No security issues
- Dependencies complete

**When to run**: Before every deployment

### `test_snowflake_integration.py`
Comprehensive Snowflake service testing:
- Connection lifecycle
- Query execution
- Error handling
- Performance validation
- Cache behavior

**When to run**: When changing Snowflake integration code

### `test_telemetry_endpoints.py`
API endpoint testing:
- `/api/telemetry/drivers` endpoint
- `/api/telemetry/coaching` endpoint
- Snowflake and local CSV fallback
- Error handling

**When to run**: When modifying API routes or data loading

## Test Fixtures

See `conftest.py` for available fixtures:
- `test_env_vars` - Test environment variables
- `mock_snowflake_connection` - Mocked Snowflake connection
- `sample_telemetry_data` - Sample telemetry DataFrame
- `client` - FastAPI test client

## Installation

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Or install individually
pip install pytest pytest-cov pytest-asyncio httpx scipy
```

## Configuration

Tests are configured in `pytest.ini` at the backend root.

Key settings:
- Tests auto-discovered in `tests/` directory
- Integration tests marked with `@pytest.mark.integration`
- Short traceback format for readability
- Warnings disabled by default

## Writing New Tests

### Test Naming Convention
```python
def test_<what>_<condition>_<expected>():
    """
    Clear docstring explaining:
    - What is being tested
    - Why this test is important
    - What failure indicates
    """
    # Test implementation
```

### Example Test
```python
def test_driver_list_returns_sorted_results(client):
    """
    Verify driver list is sorted for consistent UI display.

    Unsorted list would cause confusing driver selection experience.
    """
    response = client.get("/api/telemetry/drivers")
    drivers = response.json()["drivers_with_telemetry"]

    assert drivers == sorted(drivers), "Drivers must be sorted"
```

### Using Markers
```python
@pytest.mark.integration
def test_real_snowflake_connection():
    """Tests requiring real Snowflake connection."""
    pass

@pytest.mark.slow
def test_expensive_operation():
    """Tests taking >1 second."""
    pass
```

## Troubleshooting

### Tests fail with "No module named 'app'"
**Solution**: Run tests from backend directory
```bash
cd backend
pytest tests/ -v
```

### Integration tests skip automatically
**Reason**: Real Snowflake credentials not configured
**Solution**: Set credentials in `.env` file

### "pytest not found"
**Solution**: Install test dependencies
```bash
pip install -r requirements-dev.txt
```

### Tests fail with import errors
**Solution**: Install main dependencies first
```bash
pip install -r requirements.txt
```

## Coverage Reports

Generate coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

View report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

Target: 80%+ coverage for critical modules

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        cd backend
        pytest tests/ -v -m "not integration"

    - name: Run pre-deployment check
      run: |
        cd backend
        python scripts/pre_deployment_check.py --skip-integration
```

## Best Practices

1. **Run tests before committing**
   ```bash
   pytest tests/ -m "not integration" -v
   ```

2. **Run full validation before deploying**
   ```bash
   python scripts/pre_deployment_check.py
   ```

3. **Keep tests fast**
   - Use mocks for external services in unit tests
   - Mark slow tests with `@pytest.mark.slow`
   - Skip integration tests in CI if needed

4. **Write descriptive test names**
   - Bad: `test_driver_endpoint()`
   - Good: `test_driver_endpoint_returns_sorted_list_from_snowflake()`

5. **Document why tests exist**
   - Add docstrings explaining what failure indicates
   - Link to issues or requirements when applicable

## Support

For issues or questions:
1. Check `DEPLOYMENT_VALIDATION.md` for detailed documentation
2. Review test docstrings for context
3. Run tests with `--showlocals` for debugging
4. Check `conftest.py` for available fixtures
