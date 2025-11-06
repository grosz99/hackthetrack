#!/usr/bin/env python3
"""
Railway Deployment Validation Script

Tests all critical endpoints after Railway deployment to ensure:
- Backend is accessible
- CORS is configured correctly
- All API endpoints work
- Snowflake connection is active
- Anthropic API is functional
"""

import sys
import requests
import json
from typing import Dict, List, Tuple
from urllib.parse import urljoin


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class RailwayValidator:
    """Validates Railway deployment health and functionality."""

    def __init__(self, railway_url: str, frontend_url: str = None):
        """
        Initialize validator with Railway backend URL.

        Args:
            railway_url: Railway backend URL (e.g., https://your-app.railway.app)
            frontend_url: Optional frontend URL for CORS testing
        """
        self.railway_url = railway_url.rstrip('/')
        self.frontend_url = frontend_url.rstrip('/') if frontend_url else None
        self.results: List[Tuple[str, bool, str]] = []

    def print_header(self, text: str):
        """Print a formatted header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

    def print_test(self, name: str, passed: bool, message: str = ""):
        """Print test result with color coding."""
        icon = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
        status = f"{Colors.GREEN}PASS{Colors.END}" if passed else f"{Colors.RED}FAIL{Colors.END}"
        print(f"{icon} {name:<50} [{status}]")
        if message:
            print(f"  {Colors.YELLOW}→ {message}{Colors.END}")
        self.results.append((name, passed, message))

    def test_root_endpoint(self) -> bool:
        """Test root endpoint (/)."""
        try:
            response = requests.get(f"{self.railway_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "name" in data and "version" in data:
                    self.print_test("Root Endpoint", True, f"API: {data['name']} v{data['version']}")
                    return True
            self.print_test("Root Endpoint", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Root Endpoint", False, str(e))
            return False

    def test_health_endpoint(self) -> bool:
        """Test /api/health endpoint."""
        try:
            response = requests.get(f"{self.railway_url}/api/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "unknown")
                tracks = data.get("tracks_loaded", 0)
                drivers = data.get("drivers_loaded", 0)

                if status == "healthy":
                    self.print_test(
                        "Health Check",
                        True,
                        f"Status: {status}, Tracks: {tracks}, Drivers: {drivers}"
                    )
                    return True
            self.print_test("Health Check", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Health Check", False, str(e))
            return False

    def test_tracks_endpoint(self) -> bool:
        """Test /api/tracks endpoint."""
        try:
            response = requests.get(f"{self.railway_url}/api/tracks", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.print_test("Tracks Endpoint", True, f"Loaded {len(data)} tracks")
                    return True
            self.print_test("Tracks Endpoint", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Tracks Endpoint", False, str(e))
            return False

    def test_drivers_endpoint(self) -> bool:
        """Test /api/drivers endpoint."""
        try:
            response = requests.get(f"{self.railway_url}/api/drivers", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    self.print_test("Drivers Endpoint", True, f"Loaded {len(data)} drivers")
                    return True
            self.print_test("Drivers Endpoint", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Drivers Endpoint", False, str(e))
            return False

    def test_telemetry_drivers(self) -> bool:
        """Test /api/telemetry/drivers endpoint (Snowflake)."""
        try:
            response = requests.get(f"{self.railway_url}/api/telemetry/drivers", timeout=15)
            if response.status_code == 200:
                data = response.json()
                source = data.get("source", "unknown")
                count = data.get("count", 0)
                health = data.get("health", "unknown")

                message = f"Source: {source}, Count: {count}, Health: {health}"
                if health == "healthy" and count > 0:
                    self.print_test("Telemetry Drivers (Snowflake)", True, message)
                    return True
                else:
                    self.print_test("Telemetry Drivers (Snowflake)", False, message)
                    return False
            self.print_test("Telemetry Drivers (Snowflake)", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Telemetry Drivers (Snowflake)", False, str(e))
            return False

    def test_cors(self) -> bool:
        """Test CORS configuration."""
        if not self.frontend_url:
            self.print_test("CORS Check", False, "Frontend URL not provided (skipping)")
            return False

        try:
            headers = {
                "Origin": self.frontend_url,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type"
            }
            response = requests.options(f"{self.railway_url}/api/health", headers=headers, timeout=10)

            cors_origin = response.headers.get("access-control-allow-origin", "")
            cors_methods = response.headers.get("access-control-allow-methods", "")

            if cors_origin and cors_methods:
                self.print_test("CORS Configuration", True, f"Origin: {cors_origin}")
                return True
            else:
                self.print_test("CORS Configuration", False, "CORS headers missing")
                return False
        except Exception as e:
            self.print_test("CORS Configuration", False, str(e))
            return False

    def test_prediction_endpoint(self) -> bool:
        """Test /api/predict endpoint."""
        try:
            payload = {
                "driver_number": 13,
                "track_id": "road_atlanta"
            }
            response = requests.post(
                f"{self.railway_url}/api/predict",
                json=payload,
                timeout=15
            )
            if response.status_code == 200:
                data = response.json()
                fit_score = data.get("circuit_fit_score", 0)
                predicted_finish = data.get("predicted_finish", 0)
                self.print_test(
                    "Prediction Endpoint",
                    True,
                    f"Fit: {fit_score:.0f}/100, Finish: {predicted_finish:.1f}"
                )
                return True
            self.print_test("Prediction Endpoint", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("Prediction Endpoint", False, str(e))
            return False

    def test_ai_chat_endpoint(self) -> bool:
        """Test /api/chat endpoint (Anthropic API)."""
        try:
            payload = {
                "message": "Quick test - what's important?",
                "driver_number": 13,
                "track_id": "road_atlanta",
                "history": []
            }
            response = requests.post(
                f"{self.railway_url}/api/chat",
                json=payload,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                message = data.get("message", "")
                if len(message) > 0:
                    preview = message[:60] + "..." if len(message) > 60 else message
                    self.print_test("AI Chat (Anthropic)", True, f"Response: {preview}")
                    return True
            self.print_test("AI Chat (Anthropic)", False, f"Status: {response.status_code}")
            return False
        except Exception as e:
            self.print_test("AI Chat (Anthropic)", False, str(e))
            return False

    def run_all_tests(self):
        """Run all validation tests."""
        self.print_header("RAILWAY DEPLOYMENT VALIDATION")
        print(f"Backend URL: {Colors.BOLD}{self.railway_url}{Colors.END}")
        if self.frontend_url:
            print(f"Frontend URL: {Colors.BOLD}{self.frontend_url}{Colors.END}")
        print()

        # Core API Tests
        self.print_header("Core API Tests")
        self.test_root_endpoint()
        self.test_health_endpoint()
        self.test_tracks_endpoint()
        self.test_drivers_endpoint()

        # Data Source Tests
        self.print_header("Data Source Tests")
        self.test_telemetry_drivers()

        # Prediction Tests
        self.print_header("Prediction & AI Tests")
        self.test_prediction_endpoint()
        self.test_ai_chat_endpoint()

        # CORS Tests
        if self.frontend_url:
            self.print_header("CORS Tests")
            self.test_cors()

        # Summary
        self.print_summary()

    def print_summary(self):
        """Print test summary."""
        self.print_header("TEST SUMMARY")

        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        print()

        if failed > 0:
            print(f"{Colors.RED}{Colors.BOLD}❌ DEPLOYMENT VALIDATION FAILED{Colors.END}")
            print(f"{Colors.YELLOW}Review failed tests above and fix issues.{Colors.END}")
            sys.exit(1)
        else:
            print(f"{Colors.GREEN}{Colors.BOLD}✅ DEPLOYMENT VALIDATION PASSED{Colors.END}")
            print(f"{Colors.GREEN}All systems operational!{Colors.END}")
            sys.exit(0)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Usage: python validate_railway_deployment.py <RAILWAY_URL> [FRONTEND_URL]{Colors.END}")
        print(f"\nExample:")
        print(f"  python validate_railway_deployment.py https://your-app.railway.app")
        print(f"  python validate_railway_deployment.py https://your-app.railway.app https://your-frontend.vercel.app")
        sys.exit(1)

    railway_url = sys.argv[1]
    frontend_url = sys.argv[2] if len(sys.argv) > 2 else None

    validator = RailwayValidator(railway_url, frontend_url)
    validator.run_all_tests()


if __name__ == "__main__":
    main()
