#!/usr/bin/env python3
"""
Pre-Deployment Validation Script for HackTheTrack Backend

This script performs comprehensive validation before production deployment:
1. Environment variable validation
2. Snowflake connectivity tests
3. Database schema validation
4. Data presence verification
5. Security compliance checks
6. Dependency verification

Run this script before every deployment to ensure system readiness.

Usage:
    python scripts/pre_deployment_check.py
    python scripts/pre_deployment_check.py --skip-integration  # Skip slow tests

Exit codes:
    0 - All checks passed, ready for deployment
    1 - One or more checks failed, deployment blocked
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict
import argparse
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class DeploymentValidator:
    """Orchestrates all pre-deployment validation checks."""

    def __init__(self, skip_integration: bool = False):
        self.skip_integration = skip_integration
        self.results: List[Tuple[str, bool, str]] = []
        self.start_time = datetime.now()

    def print_header(self):
        """Print validation header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}HackTheTrack Backend - Pre-Deployment Validation{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
        print(f"Skip Integration Tests: {self.skip_integration}\n")

    def print_section(self, title: str):
        """Print section header."""
        print(f"\n{Colors.BOLD}{'─'*70}{Colors.END}")
        print(f"{Colors.BOLD}{title}{Colors.END}")
        print(f"{Colors.BOLD}{'─'*70}{Colors.END}")

    def record_result(self, check_name: str, passed: bool, message: str = ""):
        """Record check result."""
        self.results.append((check_name, passed, message))

        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {status} - {check_name}")
        if message:
            print(f"        {message}")

    def run_pytest_category(self, category: str, test_path: str, markers: str = "") -> bool:
        """
        Run pytest tests for a specific category.

        Args:
            category: Display name for test category
            test_path: Path to test file or directory
            markers: Pytest markers to filter tests

        Returns:
            True if all tests passed, False otherwise
        """
        backend_root = Path(__file__).parent.parent
        full_test_path = backend_root / test_path

        if not full_test_path.exists():
            self.record_result(
                category,
                False,
                f"Test file not found: {test_path}"
            )
            return False

        # Build pytest command
        cmd = ["pytest", str(full_test_path), "-v", "--tb=short"]

        if markers:
            cmd.extend(["-m", markers])

        # Add coverage if available
        try:
            subprocess.run(["pytest", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.record_result(
                category,
                False,
                "pytest not installed. Run: pip install pytest"
            )
            return False

        # Run tests
        print(f"\n  Running {category}...")
        result = subprocess.run(
            cmd,
            cwd=backend_root,
            capture_output=True,
            text=True
        )

        passed = result.returncode == 0

        if passed:
            # Count passed tests from output
            if "passed" in result.stdout:
                import re
                match = re.search(r'(\d+) passed', result.stdout)
                if match:
                    count = match.group(1)
                    self.record_result(category, True, f"{count} tests passed")
                else:
                    self.record_result(category, True)
            else:
                self.record_result(category, True)
        else:
            # Extract failure info
            if "failed" in result.stdout or "error" in result.stdout:
                # Show first few lines of failure
                lines = result.stdout.split('\n')
                failure_lines = [l for l in lines if 'FAILED' in l or 'ERROR' in l]
                failure_msg = '; '.join(failure_lines[:3]) if failure_lines else "See output above"
                self.record_result(category, False, failure_msg)
            else:
                self.record_result(category, False, "Tests failed - see output above")

            # Print full output for debugging
            print(f"\n{Colors.YELLOW}Test Output:{Colors.END}")
            print(result.stdout)
            if result.stderr:
                print(f"\n{Colors.RED}Test Errors:{Colors.END}")
                print(result.stderr)

        return passed

    def check_environment_setup(self) -> bool:
        """Validate environment and dependencies."""
        self.print_section("1. Environment Setup")

        all_passed = True

        # Check Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.record_result(
                "Python Version",
                True,
                f"Python {python_version.major}.{python_version.minor}.{python_version.micro}"
            )
        else:
            self.record_result(
                "Python Version",
                False,
                f"Python {python_version.major}.{python_version.minor} < 3.8 (required)"
            )
            all_passed = False

        # Check .env file exists
        backend_root = Path(__file__).parent.parent
        env_file = backend_root / ".env"

        if env_file.exists():
            self.record_result(".env File Exists", True)
        else:
            self.record_result(
                ".env File Exists",
                False,
                "Create .env from .env.example"
            )
            all_passed = False

        # Check requirements.txt exists
        req_file = backend_root / "requirements.txt"
        if req_file.exists():
            self.record_result("requirements.txt Found", True)
        else:
            self.record_result("requirements.txt Found", False)
            all_passed = False

        return all_passed

    def check_environment_variables(self) -> bool:
        """Run environment variable validation tests."""
        self.print_section("2. Environment Variables")

        return self.run_pytest_category(
            "Environment Variables",
            "tests/test_deployment_readiness.py",
            "not integration"
        )

    def check_dependencies(self) -> bool:
        """Run dependency validation tests."""
        self.print_section("3. Dependencies")

        return self.run_pytest_category(
            "Dependency Validation",
            "tests/test_deployment_readiness.py::TestDependencyCompleteness"
        )

    def check_security(self) -> bool:
        """Run security compliance tests."""
        self.print_section("4. Security Compliance")

        return self.run_pytest_category(
            "Security Checks",
            "tests/test_deployment_readiness.py::TestSecurityCompliance"
        )

    def check_snowflake_integration(self) -> bool:
        """Run Snowflake integration tests."""
        self.print_section("5. Snowflake Integration")

        if self.skip_integration:
            self.record_result(
                "Snowflake Integration Tests",
                True,
                "Skipped (--skip-integration flag)"
            )
            return True

        # Check if real credentials are configured
        account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        if "your-account" in account or not account:
            self.record_result(
                "Snowflake Integration Tests",
                True,
                "Skipped (credentials not configured)"
            )
            return True

        # Run integration tests
        return self.run_pytest_category(
            "Snowflake Integration Tests",
            "tests/test_deployment_readiness.py::TestSnowflakeConnectivity",
            "integration"
        )

    def check_api_endpoints(self) -> bool:
        """Run API endpoint tests."""
        self.print_section("6. API Endpoints")

        return self.run_pytest_category(
            "API Endpoint Tests",
            "tests/test_telemetry_endpoints.py",
            "not integration"
        )

    def check_vercel_configuration(self) -> bool:
        """Validate Vercel configuration if applicable."""
        self.print_section("7. Vercel Configuration")

        backend_root = Path(__file__).parent.parent
        vercel_json = backend_root / "vercel.json"

        if vercel_json.exists():
            self.record_result("vercel.json Found", True)

            # Check if it's valid JSON
            try:
                import json
                with open(vercel_json) as f:
                    json.load(f)
                self.record_result("vercel.json Valid", True)
            except json.JSONDecodeError as e:
                self.record_result("vercel.json Valid", False, str(e))
                return False
        else:
            self.record_result(
                "vercel.json Found",
                True,
                "Not found (optional for Vercel deployment)"
            )

        return True

    def print_summary(self):
        """Print validation summary."""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}Validation Summary{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}\n")

        passed_count = sum(1 for _, passed, _ in self.results if passed)
        failed_count = len(self.results) - passed_count

        print(f"Total Checks: {len(self.results)}")
        print(f"{Colors.GREEN}Passed: {passed_count}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed_count}{Colors.END}")
        print(f"Duration: {duration:.2f}s")

        if failed_count == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.END}")
            print(f"{Colors.GREEN}System is ready for deployment!{Colors.END}\n")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ DEPLOYMENT BLOCKED{Colors.END}")
            print(f"{Colors.RED}Fix the following issues before deploying:{Colors.END}\n")

            for check_name, passed, message in self.results:
                if not passed:
                    print(f"  {Colors.RED}• {check_name}{Colors.END}")
                    if message:
                        print(f"    {message}")

            print()
            return 1

    def run_all_checks(self) -> int:
        """
        Run all validation checks.

        Returns:
            0 if all checks passed, 1 if any failed
        """
        self.print_header()

        # Run all check categories
        checks = [
            self.check_environment_setup,
            self.check_environment_variables,
            self.check_dependencies,
            self.check_security,
            self.check_snowflake_integration,
            self.check_api_endpoints,
            self.check_vercel_configuration,
        ]

        for check_func in checks:
            try:
                check_func()
            except Exception as e:
                self.record_result(
                    check_func.__name__,
                    False,
                    f"Unexpected error: {str(e)}"
                )

        return self.print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Pre-deployment validation for HackTheTrack backend"
    )
    parser.add_argument(
        "--skip-integration",
        action="store_true",
        help="Skip integration tests (faster, but less thorough)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Change to backend directory
    backend_root = Path(__file__).parent.parent
    os.chdir(backend_root)

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print(f"{Colors.YELLOW}Warning: python-dotenv not installed{Colors.END}")
        print("Install with: pip install python-dotenv")

    # Run validation
    validator = DeploymentValidator(skip_integration=args.skip_integration)
    exit_code = validator.run_all_checks()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
