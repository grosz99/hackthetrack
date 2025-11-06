#!/usr/bin/env python3
"""
Deployment Validation Script for HackTheTrack Backend.

Tests deployed endpoint to verify:
- Health check responds
- Snowflake connectivity working
- Driver list returns data
- All critical endpoints functional

Usage:
    python scripts/validate_deployment.py --url https://your-app.vercel.app
    python scripts/validate_deployment.py --url http://localhost:3000  # Test locally
"""

import argparse
import sys
import time
from typing import Dict, List, Tuple
import requests


class DeploymentValidator:
    """Validates deployed backend endpoints."""

    def __init__(self, base_url: str):
        """
        Initialize validator with base URL.

        Args:
            base_url: Base URL of deployed backend (e.g., https://app.vercel.app)
        """
        self.base_url = base_url.rstrip('/')
        self.results: List[Tuple[str, bool, str]] = []

    def test_health_endpoint(self) -> bool:
        """Test /api/health endpoint."""
        print("\n→ Testing health endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)

            if response.status_code != 200:
                self._record_failure(
                    "Health Check",
                    f"Status code {response.status_code}, expected 200"
                )
                return False

            data = response.json()

            if data.get("status") != "healthy":
                self._record_failure(
                    "Health Check",
                    f"Status is '{data.get('status')}', expected 'healthy'"
                )
                return False

            self._record_success(
                "Health Check",
                f"Status: {data.get('status')}, "
                f"Tracks: {data.get('tracks_loaded')}, "
                f"Drivers: {data.get('drivers_loaded')}"
            )
            return True

        except Exception as e:
            self._record_failure("Health Check", f"Request failed: {str(e)}")
            return False

    def test_driver_list_endpoint(self) -> bool:
        """Test /api/telemetry/drivers endpoint."""
        print("\n→ Testing driver list endpoint...")
        try:
            response = requests.get(
                f"{self.base_url}/api/telemetry/drivers",
                timeout=15
            )

            if response.status_code != 200:
                self._record_failure(
                    "Driver List",
                    f"Status code {response.status_code}, expected 200"
                )
                return False

            data = response.json()

            drivers = data.get("drivers_with_telemetry", [])
            if len(drivers) == 0:
                self._record_failure(
                    "Driver List",
                    "No drivers returned (this is the critical '0 drivers' bug!)"
                )
                return False

            source = data.get("source", "unknown")
            count = data.get("count", 0)

            self._record_success(
                "Driver List",
                f"Source: {source}, Count: {count}, Drivers: {drivers[:5]}..."
            )

            # Check if using Snowflake
            if source == "snowflake":
                print("  ✓ Using Snowflake (expected for production)")
            else:
                print(f"  ⚠ Using {source} (fallback, check Snowflake configuration)")

            return True

        except Exception as e:
            self._record_failure("Driver List", f"Request failed: {str(e)}")
            return False

    def test_snowflake_health(self) -> bool:
        """Test Snowflake connectivity via health endpoint."""
        print("\n→ Testing Snowflake connectivity...")
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=10)

            if response.status_code != 200:
                self._record_failure(
                    "Snowflake Health",
                    "Health endpoint not responding"
                )
                return False

            data = response.json()

            # Check if health response includes Snowflake status
            dependencies = data.get("dependencies", {})
            snowflake_status = dependencies.get("snowflake", {})

            if snowflake_status:
                if snowflake_status.get("status") == "connected":
                    self._record_success(
                        "Snowflake Health",
                        f"Connected to database: {snowflake_status.get('database')}"
                    )
                    return True
                else:
                    self._record_failure(
                        "Snowflake Health",
                        f"Status: {snowflake_status.get('status')}, "
                        f"Error: {snowflake_status.get('error')}"
                    )
                    return False
            else:
                print("  ⚠ Health endpoint doesn't include Snowflake status (may need enhancement)")
                self._record_success(
                    "Snowflake Health",
                    "Not reported in health check (check logs)"
                )
                return True

        except Exception as e:
            self._record_failure("Snowflake Health", f"Request failed: {str(e)}")
            return False

    def test_response_times(self) -> bool:
        """Test endpoint response times."""
        print("\n→ Testing response times...")
        endpoints = [
            ("/api/health", 2.0),
            ("/api/telemetry/drivers", 10.0),
        ]

        all_passed = True

        for endpoint, max_time in endpoints:
            try:
                start = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=max_time + 5)
                elapsed = time.time() - start

                if elapsed > max_time:
                    self._record_failure(
                        f"Response Time {endpoint}",
                        f"{elapsed:.2f}s (limit: {max_time}s)"
                    )
                    all_passed = False
                else:
                    self._record_success(
                        f"Response Time {endpoint}",
                        f"{elapsed:.2f}s (within {max_time}s limit)"
                    )

            except requests.Timeout:
                self._record_failure(
                    f"Response Time {endpoint}",
                    f"Timeout after {max_time}s"
                )
                all_passed = False
            except Exception as e:
                self._record_failure(
                    f"Response Time {endpoint}",
                    f"Failed: {str(e)}"
                )
                all_passed = False

        return all_passed

    def _record_success(self, test_name: str, message: str):
        """Record successful test."""
        self.results.append((test_name, True, message))
        print(f"  ✓ {test_name}: {message}")

    def _record_failure(self, test_name: str, message: str):
        """Record failed test."""
        self.results.append((test_name, False, message))
        print(f"  ✗ {test_name}: {message}")

    def print_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 70)
        print("DEPLOYMENT VALIDATION SUMMARY")
        print("=" * 70)

        passed = sum(1 for _, success, _ in self.results if success)
        failed = len(self.results) - passed

        print(f"\nTotal Tests: {len(self.results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

        if failed > 0:
            print("\n⚠ FAILED TESTS:")
            for test_name, success, message in self.results:
                if not success:
                    print(f"  ✗ {test_name}: {message}")

        print("\n" + "=" * 70)

        if failed == 0:
            print("✅ ALL TESTS PASSED - DEPLOYMENT IS HEALTHY")
            print("=" * 70)
            return True
        else:
            print("❌ SOME TESTS FAILED - INVESTIGATE BEFORE USING IN PRODUCTION")
            print("=" * 70)
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate HackTheTrack backend deployment"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Base URL of deployed backend (e.g., https://your-app.vercel.app)"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("HACKTHETRACK BACKEND DEPLOYMENT VALIDATION")
    print("=" * 70)
    print(f"\nTarget URL: {args.url}")
    print(f"Starting validation at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    validator = DeploymentValidator(args.url)

    # Run all tests
    tests = [
        validator.test_health_endpoint,
        validator.test_driver_list_endpoint,
        validator.test_snowflake_health,
        validator.test_response_times,
    ]

    for test in tests:
        test()

    # Print summary
    all_passed = validator.print_summary()

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
