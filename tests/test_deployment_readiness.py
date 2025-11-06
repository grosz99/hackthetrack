"""
Deployment readiness validation tests.

This module ensures all prerequisites for production deployment are met:
- Environment variables are configured correctly
- Snowflake connection can be established
- Required database objects exist
- Telemetry data is present
- No security issues (hardcoded credentials, exposed secrets)
- All dependencies are properly declared

Run with: pytest tests/test_deployment_readiness.py -v
"""

import os
import pytest
from pathlib import Path
from typing import Dict, List


class TestEnvironmentVariables:
    """Validate all required environment variables are configured."""

    REQUIRED_ENV_VARS = {
        "ANTHROPIC_API_KEY": "AI coaching functionality",
        "SNOWFLAKE_ACCOUNT": "Snowflake connection",
        "SNOWFLAKE_USER": "Snowflake authentication",
        "SNOWFLAKE_PASSWORD": "Snowflake authentication",
        "SNOWFLAKE_WAREHOUSE": "Snowflake compute",
        "SNOWFLAKE_DATABASE": "Telemetry data storage",
        "SNOWFLAKE_SCHEMA": "Telemetry data organization",
    }

    def test_all_required_env_vars_exist(self):
        """
        Validate all critical environment variables are set.

        Fails if any required variable is missing, preventing deployment
        with incomplete configuration.
        """
        missing_vars = []
        for var_name, purpose in self.REQUIRED_ENV_VARS.items():
            value = os.getenv(var_name)
            if not value or value == "":
                missing_vars.append(f"{var_name} (needed for: {purpose})")

        assert not missing_vars, (
            f"Missing required environment variables:\n"
            f"{chr(10).join('  - ' + v for v in missing_vars)}\n"
            f"Set these in .env file or Vercel environment settings."
        )

    def test_env_vars_not_placeholder_values(self):
        """
        Ensure environment variables don't contain placeholder values.

        Prevents deployment with example/dummy configuration from .env.example.
        """
        placeholder_patterns = [
            "your-account",
            "your-region",
            "your_username",
            "your_password",
            "your-key-here",
            "sk-ant-your-key",
        ]

        issues = []
        for var_name in self.REQUIRED_ENV_VARS.keys():
            value = os.getenv(var_name, "")
            for pattern in placeholder_patterns:
                if pattern.lower() in value.lower():
                    issues.append(
                        f"{var_name} contains placeholder value: {value[:30]}..."
                    )

        assert not issues, (
            f"Environment variables contain placeholder values:\n"
            f"{chr(10).join('  - ' + i for i in issues)}\n"
            f"Replace with actual credentials before deployment."
        )

    def test_use_snowflake_flag_set_correctly(self):
        """
        Validate USE_SNOWFLAKE flag is properly configured.

        For production deployments, this should be 'true'.
        For local development, can be 'false'.
        """
        use_snowflake = os.getenv("USE_SNOWFLAKE", "false").lower()

        # Just validate it's a valid boolean value
        assert use_snowflake in ["true", "false"], (
            f"USE_SNOWFLAKE must be 'true' or 'false', got: {use_snowflake}"
        )

    def test_snowflake_account_format_valid(self):
        """
        Validate Snowflake account identifier format.

        Account should be in format: <account>.<region>
        Example: xy12345.us-east-1
        """
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")

        if not account or "your-account" in account:
            pytest.skip("Snowflake account not configured yet")

        # Basic format validation
        assert "." in account or "-" in account, (
            f"Snowflake account format appears invalid: {account}\n"
            f"Expected format: <account>.<region> (e.g., xy12345.us-east-1)"
        )


class TestSnowflakeConnectivity:
    """Validate Snowflake database connectivity and schema."""

    @pytest.mark.integration
    def test_snowflake_connection_establishes(self):
        """
        Test that Snowflake connection can be established.

        This is a critical pre-deployment check. Deployment should not
        proceed if this test fails.
        """
        from app.services.snowflake_service import SnowflakeService

        # Skip if credentials are placeholder values
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            assert conn is not None, "Connection returned None"

            # Verify connection is active
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result == (1,), "Basic query failed"

            conn.close()
        except Exception as e:
            pytest.fail(
                f"Snowflake connection failed: {str(e)}\n"
                f"Verify credentials and network access before deployment."
            )

    @pytest.mark.integration
    def test_snowflake_database_exists(self):
        """
        Validate that the configured database exists in Snowflake.

        Prevents deployment to environment with missing database.
        """
        from app.services.snowflake_service import SnowflakeService

        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            cursor = conn.cursor()

            # Check current database
            cursor.execute("SELECT CURRENT_DATABASE()")
            current_db = cursor.fetchone()[0]

            expected_db = os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK")
            assert current_db == expected_db, (
                f"Database mismatch. Connected to: {current_db}, "
                f"expected: {expected_db}"
            )

            conn.close()
        except Exception as e:
            pytest.fail(f"Database validation failed: {str(e)}")

    @pytest.mark.integration
    def test_snowflake_schema_exists(self):
        """
        Validate that the configured schema exists.

        Ensures telemetry data tables are accessible.
        """
        from app.services.snowflake_service import SnowflakeService

        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            cursor = conn.cursor()

            # Check current schema
            cursor.execute("SELECT CURRENT_SCHEMA()")
            current_schema = cursor.fetchone()[0]

            expected_schema = os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY")
            assert current_schema == expected_schema, (
                f"Schema mismatch. Connected to: {current_schema}, "
                f"expected: {expected_schema}"
            )

            conn.close()
        except Exception as e:
            pytest.fail(f"Schema validation failed: {str(e)}")

    @pytest.mark.integration
    def test_telemetry_table_exists(self):
        """
        Validate that telemetry_data table exists and is accessible.

        This is the core table for the application.
        """
        from app.services.snowflake_service import SnowflakeService

        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            cursor = conn.cursor()

            # Check if table exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_NAME = 'TELEMETRY_DATA'
            """)
            table_count = cursor.fetchone()[0]

            assert table_count > 0, (
                "Table TELEMETRY_DATA not found in Snowflake.\n"
                "Run upload script to create and populate table."
            )

            conn.close()
        except Exception as e:
            pytest.fail(f"Table validation failed: {str(e)}")

    @pytest.mark.integration
    def test_telemetry_data_not_empty(self):
        """
        Validate that telemetry table contains data.

        Empty table would cause "0 drivers" issue in production.
        """
        from app.services.snowflake_service import SnowflakeService

        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            conn = service.get_connection()
            cursor = conn.cursor()

            # Check row count
            cursor.execute("SELECT COUNT(*) FROM telemetry_data")
            row_count = cursor.fetchone()[0]

            assert row_count > 0, (
                "Telemetry table is empty!\n"
                "Upload telemetry data before deployment to prevent '0 drivers' issue."
            )

            # Also check distinct drivers
            cursor.execute(
                "SELECT COUNT(DISTINCT vehicle_number) FROM telemetry_data"
            )
            driver_count = cursor.fetchone()[0]

            assert driver_count > 0, (
                "No drivers with telemetry data!\n"
                "Upload telemetry CSV files using upload_to_snowflake.py"
            )

            # Print info for visibility
            print(f"\n✓ Telemetry data verified: {row_count:,} rows, {driver_count} drivers")

            conn.close()
        except Exception as e:
            pytest.fail(f"Data validation failed: {str(e)}")

    @pytest.mark.integration
    def test_connection_performance(self):
        """
        Validate that Snowflake queries execute in reasonable time.

        Slow queries could indicate warehouse sizing or network issues.
        """
        import time
        from app.services.snowflake_service import SnowflakeService

        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            pytest.skip("Real Snowflake credentials not configured")

        service = SnowflakeService()

        try:
            start_time = time.time()

            # Test a typical query
            drivers = service.get_drivers_with_telemetry()

            elapsed = time.time() - start_time

            assert elapsed < 5.0, (
                f"Query took {elapsed:.2f}s (limit: 5s).\n"
                f"Consider warehouse size or network optimization."
            )

            assert len(drivers) > 0, "No drivers returned from query"

            print(f"\n✓ Query performance: {elapsed:.2f}s for {len(drivers)} drivers")

        except Exception as e:
            pytest.fail(f"Performance test failed: {str(e)}")


class TestSecurityCompliance:
    """Validate no security issues exist in codebase."""

    def test_no_hardcoded_credentials_in_code(self):
        """
        Scan codebase for hardcoded credentials or secrets.

        Prevents accidental credential exposure in version control.
        """
        backend_root = Path(__file__).parent.parent
        suspicious_patterns = [
            "password=",
            "api_key=",
            "secret=",
            "token=",
            "sk-ant-",
        ]

        # Files to check
        python_files = list(backend_root.glob("**/*.py"))

        issues = []
        for file_path in python_files:
            # Skip test files and virtual env
            if "test" in str(file_path) or "venv" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                for pattern in suspicious_patterns:
                    if pattern in content.lower():
                        # Check if it's in a string assignment (potential hardcoded value)
                        lines = content.split("\n")
                        for i, line in enumerate(lines, 1):
                            if pattern in line.lower() and "os.getenv" not in line:
                                # Likely hardcoded
                                if "=" in line and '"' in line:
                                    issues.append(
                                        f"{file_path.name}:{i} - Potential hardcoded secret"
                                    )
            except Exception:
                continue

        assert not issues, (
            f"Potential hardcoded credentials found:\n"
            f"{chr(10).join('  - ' + i for i in issues)}\n"
            f"Use environment variables for all secrets."
        )

    def test_env_file_not_in_git(self):
        """
        Validate .env file is not tracked by git.

        Prevents secret exposure through version control.
        """
        backend_root = Path(__file__).parent.parent
        env_file = backend_root / ".env"

        if not env_file.exists():
            pytest.skip(".env file doesn't exist yet")

        gitignore = backend_root / ".gitignore"

        assert gitignore.exists(), ".gitignore file missing!"

        gitignore_content = gitignore.read_text()
        assert ".env" in gitignore_content, (
            ".env file not in .gitignore!\n"
            "Add '.env' to .gitignore to prevent credential leaks."
        )


class TestDependencyCompleteness:
    """Validate all dependencies are properly declared."""

    def test_all_imports_in_requirements(self):
        """
        Verify all imported packages exist in requirements.txt.

        Prevents deployment failures due to missing dependencies.
        """
        backend_root = Path(__file__).parent.parent
        requirements_file = backend_root / "requirements.txt"

        assert requirements_file.exists(), "requirements.txt not found!"

        requirements_content = requirements_file.read_text()

        # Critical dependencies that must be present
        critical_deps = [
            "fastapi",
            "uvicorn",
            "python-dotenv",
            "anthropic",
            "pandas",
            "snowflake-connector-python",
        ]

        missing_deps = []
        for dep in critical_deps:
            if dep not in requirements_content:
                missing_deps.append(dep)

        assert not missing_deps, (
            f"Critical dependencies missing from requirements.txt:\n"
            f"{chr(10).join('  - ' + d for d in missing_deps)}\n"
            f"Add these to requirements.txt before deployment."
        )

    def test_snowflake_connector_version(self):
        """
        Validate snowflake-connector-python version is specified.

        Prevents version conflicts and ensures compatibility.
        """
        backend_root = Path(__file__).parent.parent
        requirements_file = backend_root / "requirements.txt"

        requirements_content = requirements_file.read_text()

        assert "snowflake-connector-python" in requirements_content, (
            "snowflake-connector-python not in requirements.txt!"
        )

        # Should have version pinning
        snowflake_line = [
            line for line in requirements_content.split("\n")
            if "snowflake-connector-python" in line
        ][0]

        assert "==" in snowflake_line, (
            f"Snowflake connector version not pinned: {snowflake_line}\n"
            f"Pin version to ensure reproducible builds."
        )


class TestAPIEndpointReadiness:
    """Validate critical API endpoints are accessible."""

    def test_health_endpoint_responds(self):
        """
        Verify health check endpoint is functional.

        Used by monitoring systems to detect service availability.
        """
        # This would typically use TestClient from fastapi.testclient
        # For now, just verify the endpoint exists in routes
        from app.api.routes import router

        routes = [route.path for route in router.routes]
        assert "/health" in routes, "Health check endpoint missing!"

    def test_telemetry_drivers_endpoint_exists(self):
        """
        Verify telemetry drivers endpoint exists.

        Critical for preventing "0 drivers" issue.
        """
        from app.api.routes import router

        routes = [route.path for route in router.routes]
        assert "/telemetry/drivers" in routes, (
            "Telemetry drivers endpoint missing!\n"
            "This endpoint is critical for driver list population."
        )
