# Backend Deployment Validation Suite

## Overview

This validation suite ensures rock-solid backend connectivity and deployment reliability for the HackTheTrack platform. It provides comprehensive pre-deployment checks for Snowflake integration, API endpoints, security compliance, and system readiness.

## Quick Start

### Run Full Validation

```bash
# From backend directory
python scripts/pre_deployment_check.py
```

### Run Specific Test Categories

```bash
# Run all tests
pytest tests/ -v

# Run only deployment readiness tests
pytest tests/test_deployment_readiness.py -v

# Run only Snowflake integration tests
pytest tests/test_snowflake_integration.py -v

# Run only API endpoint tests
pytest tests/test_telemetry_endpoints.py -v

# Skip integration tests (faster)
pytest tests/ -v -m "not integration"

# Run only integration tests
pytest tests/ -v -m "integration"
```

## Test Suite Structure

### 1. Deployment Readiness Tests (`test_deployment_readiness.py`)

Validates all prerequisites for production deployment:

- **Environment Variables**: Ensures all required variables are set and not placeholder values
- **Snowflake Connectivity**: Tests connection establishment, database/schema access
- **Data Presence**: Verifies telemetry table exists and contains data
- **Security Compliance**: Scans for hardcoded credentials and .gitignore compliance
- **Dependencies**: Validates requirements.txt completeness

**Critical Tests:**
- `test_all_required_env_vars_exist` - Blocks deployment if any required variable missing
- `test_telemetry_data_not_empty` - Prevents "0 drivers" production issue
- `test_no_hardcoded_credentials_in_code` - Security check

### 2. Snowflake Integration Tests (`test_snowflake_integration.py`)

Comprehensive testing of Snowflake service:

- **Connection Lifecycle**: Establishment, failure modes, cleanup
- **Query Execution**: Data retrieval, parameterization, performance
- **Error Handling**: Network timeouts, authentication failures, graceful degradation
- **Caching**: LRU cache behavior and efficiency

**Critical Tests:**
- `test_connection_succeeds_with_valid_credentials` - Validates real connectivity
- `test_returns_real_drivers` - Ensures driver list population works
- `test_query_performance_acceptable` - Prevents slow queries (<5s requirement)

### 3. API Endpoint Tests (`test_telemetry_endpoints.py`)

Tests critical API endpoints that integrate with Snowflake:

- **Driver List Endpoint** (`/api/telemetry/drivers`): Tests Snowflake and local CSV fallback
- **Coaching Endpoint** (`/api/telemetry/coaching`): Tests telemetry analysis with both data sources
- **Health Check** (`/api/health`): Validates monitoring endpoint
- **Error Handling**: Ensures graceful degradation and proper error responses

**Critical Tests:**
- `test_falls_back_to_local_on_snowflake_error` - Resilience testing
- `test_response_includes_source_field` - Debugging visibility
- `test_real_endpoint_returns_drivers` - Integration validation

## Pre-Deployment Check Script

The `pre_deployment_check.py` script orchestrates all validations and provides a clear go/no-go decision.

### Usage

```bash
# Full validation (recommended)
python scripts/pre_deployment_check.py

# Skip integration tests (faster, for development)
python scripts/pre_deployment_check.py --skip-integration

# Verbose output
python scripts/pre_deployment_check.py -v
```

### Exit Codes

- **0**: All checks passed - **SAFE TO DEPLOY**
- **1**: One or more checks failed - **DEPLOYMENT BLOCKED**

### What It Checks

1. **Environment Setup**: Python version, .env file, requirements.txt
2. **Environment Variables**: All required vars set with real values
3. **Dependencies**: All imports declared in requirements.txt
4. **Security**: No hardcoded credentials, .env in .gitignore
5. **Snowflake Integration**: Connection, schema, data presence (if credentials configured)
6. **API Endpoints**: Critical endpoints functional
7. **Vercel Configuration**: vercel.json valid (if present)

## Test Markers

Tests are categorized using pytest markers:

- `@pytest.mark.integration` - Requires external services (Snowflake)
- `@pytest.mark.unit` - Pure unit tests, no external dependencies
- `@pytest.mark.slow` - Tests taking >1 second

### Run by Marker

```bash
# Only integration tests
pytest -m integration

# Skip integration tests
pytest -m "not integration"

# Only slow tests
pytest -m slow
```

## Fixtures

The test suite includes reusable fixtures in `conftest.py`:

### Environment Fixtures

- `test_env_vars`: Safe test values for all environment variables
- `mock_env_vars`: Auto-sets test environment variables
- `real_env_check`: Detects if real credentials are available

### Snowflake Fixtures

- `mock_snowflake_connection`: Mocked Snowflake connection for unit tests
- `sample_telemetry_data`: Realistic telemetry DataFrame
- `clean_snowflake_cache`: Clears LRU cache between tests

### API Fixtures

- `client`: FastAPI TestClient for endpoint testing

### Example Usage

```python
def test_with_mock_env(mock_env_vars):
    # Environment variables automatically set
    assert os.getenv("SNOWFLAKE_ACCOUNT") == "test-account.us-east-1"

def test_snowflake_query(mock_snowflake_connection, sample_telemetry_data):
    # Mock connection and data ready to use
    pass
```

## Deployment Workflow

### 1. Local Development

```bash
# Before committing changes
pytest tests/ -v

# Quick validation (skip integration)
python scripts/pre_deployment_check.py --skip-integration
```

### 2. Pre-Deployment (Required)

```bash
# Full validation with real Snowflake
python scripts/pre_deployment_check.py

# Exit code 0 = Safe to deploy
# Exit code 1 = Fix issues before deploying
```

### 3. CI/CD Integration

Add to your CI pipeline (GitHub Actions, etc.):

```yaml
- name: Install dependencies
  run: pip install -r requirements.txt

- name: Install test dependencies
  run: pip install pytest pytest-cov

- name: Run deployment validation
  run: python scripts/pre_deployment_check.py --skip-integration
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    SNOWFLAKE_ACCOUNT: ${{ secrets.SNOWFLAKE_ACCOUNT }}
    SNOWFLAKE_USER: ${{ secrets.SNOWFLAKE_USER }}
    SNOWFLAKE_PASSWORD: ${{ secrets.SNOWFLAKE_PASSWORD }}
```

### 4. Vercel Environment Variables

Ensure these are set in Vercel dashboard:

**Required:**
- `ANTHROPIC_API_KEY`
- `USE_SNOWFLAKE=true`
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_WAREHOUSE`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`

**Validation:**
```bash
# List Vercel env vars (requires Vercel CLI)
vercel env ls

# Pull env vars to .env.production
vercel env pull .env.production
```

## Common Issues and Solutions

### Issue: "Missing Snowflake credentials"

**Solution:**
1. Copy `.env.example` to `.env`
2. Fill in real Snowflake credentials
3. Never commit `.env` to git

### Issue: "Table TELEMETRY_DATA not found"

**Solution:**
1. Run upload script: `python upload_to_snowflake.py`
2. Verify table exists: Check Snowflake console
3. Check schema name matches environment variable

### Issue: "No drivers with telemetry data"

**Solution:**
1. Upload CSV files to Snowflake
2. Verify `vehicle_number` column has data
3. Check CSV files exist in `data/telemetry/` for local fallback

### Issue: "Connection timeout"

**Solution:**
1. Check network connectivity to Snowflake
2. Verify IP whitelisting (if applicable)
3. Check warehouse is running (not suspended)
4. Consider increasing timeout settings

### Issue: "Tests fail with real credentials"

**Solution:**
1. Verify credentials are correct in Snowflake console
2. Check user has required permissions (USAGE, SELECT)
3. Ensure warehouse, database, and schema names are correct
4. Test connection using Snowflake's SnowSQL CLI

## Performance Targets

All tests should meet these performance targets:

- **Snowflake Connection**: <2 seconds to establish
- **Driver List Query**: <5 seconds to execute
- **Telemetry Data Query**: <5 seconds for typical dataset
- **API Endpoints**: <1 second response time
- **Full Test Suite**: <30 seconds (excluding integration)

If tests exceed these targets, investigate:
- Snowflake warehouse size
- Network latency
- Query optimization
- Connection pooling

## Security Best Practices

The validation suite enforces these security standards:

1. **No Hardcoded Credentials**: All secrets must use environment variables
2. **Secret Management**: .env file must be in .gitignore
3. **Parameterized Queries**: All SQL queries use parameters, never string interpolation
4. **Error Sanitization**: No credential exposure in error messages
5. **Connection Cleanup**: All connections properly closed to prevent leaks

## Monitoring Integration

The validation suite supports monitoring systems:

### Health Check Endpoint

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "tracks_loaded": 15,
  "drivers_loaded": 25
}
```

### Snowflake Health Check

```python
from app.services.snowflake_service import snowflake_service

status = snowflake_service.check_connection()
# Returns: {"status": "connected", "version": "...", "database": "..."}
```

## Continuous Improvement

### Adding New Tests

1. Create test in appropriate test file
2. Use descriptive test names: `test_<what>_<condition>_<expected>`
3. Add docstring explaining what is tested and why
4. Use appropriate markers (`@pytest.mark.integration`, etc.)
5. Add to pre-deployment check if critical

### Test Coverage

Run with coverage reporting:

```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term-missing
```

Target: 80%+ coverage for critical paths (Snowflake service, API routes)

## Support

### Running Tests in Debug Mode

```bash
# Show local variables in failures
pytest tests/ --showlocals

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/test_snowflake_integration.py::TestSnowflakeConnection::test_connection_succeeds_with_valid_credentials -v
```

### Verbose Output

```bash
# Maximum verbosity
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Show test durations
pytest tests/ --durations=10
```

## Conclusion

This validation suite ensures zero-tolerance for backend fragility. Every deployment must pass all checks. Use it religiously to maintain production reliability and prevent the "0 drivers" issue.

**Remember: If the pre-deployment check fails, DO NOT DEPLOY.**
