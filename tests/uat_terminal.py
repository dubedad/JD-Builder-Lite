#!/usr/bin/env python
"""Terminal-based UAT test suite for JD Builder Lite.

Run with: python tests/uat_terminal.py

Tests the complete user journey through API and page checks.
"""

import requests
import sys
import json
from typing import Tuple, List, Optional

BASE_URL = "http://127.0.0.1:5000"

# ANSI colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def check(condition: bool, name: str, detail: str = "") -> bool:
    """Print pass/fail for a test condition."""
    if condition:
        print(f"  {GREEN}[PASS]{RESET} {name}")
    else:
        print(f"  {RED}[FAIL]{RESET} {name}")
        if detail:
            print(f"    {YELLOW}-> {detail}{RESET}")
    return condition


def section(title: str):
    """Print section header."""
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}{title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")


def test_api_health() -> Tuple[int, int]:
    """Test API health endpoints."""
    section("1. API Health Checks")
    passed, total = 0, 0

    # Test /api/ping
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/ping", timeout=5)
        if check(r.status_code == 200 and r.json().get("status") == "ok",
                "GET /api/ping returns 200 OK"):
            passed += 1
    except Exception as e:
        check(False, "GET /api/ping", str(e))

    # Test /api/health
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if check(r.status_code == 200 and "version" in r.json(),
                "GET /api/health returns version"):
            passed += 1
    except Exception as e:
        check(False, "GET /api/health", str(e))

    return passed, total


def test_homepage() -> Tuple[int, int]:
    """Test homepage loads with expected elements."""
    section("2. Homepage (Step 1: Search)")
    passed, total = 0, 0

    try:
        r = requests.get(BASE_URL, timeout=10)
        html = r.text

        # Check page loads
        total += 1
        if check(r.status_code == 200, "Homepage returns 200"):
            passed += 1

        # Check stepper exists
        total += 1
        if check("jd-stepper" in html, "Progress stepper present"):
            passed += 1

        # Check all 5 steps exist
        total += 1
        steps = ["Search", "Select Profile", "Build JD", "Export", "Classify"]
        all_steps = all(s in html for s in steps)
        if check(all_steps, f"All 5 steps present: {', '.join(steps)}"):
            passed += 1

        # Check GC header
        total += 1
        if check("Government of Canada" in html, "GC CDTS header present"):
            passed += 1

        # Check search input
        total += 1
        if check("search" in html.lower() or "Search Canada.ca" in html,
                "Search functionality present"):
            passed += 1

    except Exception as e:
        check(False, "Homepage load", str(e))
        total += 5

    return passed, total


def test_search_api() -> Tuple[int, int]:
    """Test NOC search API."""
    section("3. Search API (Step 1 Backend)")
    passed, total = 0, 0

    # Test search with valid query
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/search?q=analyst&type=Keyword", timeout=15)
        if check(r.status_code == 200, "Search 'analyst' returns 200"):
            passed += 1
            data = r.json()

            total += 1
            if check("results" in data, "Response has 'results' field"):
                passed += 1

            total += 1
            if check(data.get("count", 0) > 0, f"Found {data.get('count', 0)} results"):
                passed += 1
    except Exception as e:
        check(False, "Search API", str(e))
        total += 2

    # Test search validation
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/search?q=a", timeout=5)  # Too short
        if check(r.status_code == 400, "Short query rejected (400)"):
            passed += 1
    except Exception as e:
        check(False, "Search validation", str(e))

    return passed, total


def test_profile_api() -> Tuple[int, int]:
    """Test profile fetch API."""
    section("4. Profile API (Step 2 Backend)")
    passed, total = 0, 0

    # Test valid NOC code (21211 = Data engineers)
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/profile?code=21211", timeout=15)
        if check(r.status_code == 200, "Profile 21232 returns 200"):
            passed += 1
            data = r.json()

            total += 1
            if check("job_title" in data or "title" in data, "Profile has title"):
                passed += 1

            total += 1
            if check("key_activities" in data or "main_duties" in data,
                    "Profile has duties/activities"):
                passed += 1
    except Exception as e:
        check(False, "Profile API", str(e))
        total += 2

    # Test invalid NOC code
    total += 1
    try:
        r = requests.get(f"{BASE_URL}/api/profile?code=abc", timeout=5)
        if check(r.status_code == 400, "Invalid code rejected (400)"):
            passed += 1
    except Exception as e:
        check(False, "Profile validation", str(e))

    return passed, total


def test_allocate_api() -> Tuple[int, int]:
    """Test allocation API (Phase 17 - Classify step)."""
    section("5. Allocation API (Step 5: Classify Backend)")
    passed, total = 0, 0

    # Test valid allocation request
    payload = {
        "position_title": "Senior Data Analyst",
        "client_service_results": "Provides analytical services to policy branches to support evidence-based decision making and program evaluation.",
        "key_activities": [
            "Analyzes large datasets using statistical methods",
            "Develops reports and dashboards for senior management",
            "Provides recommendations based on data insights",
            "Collaborates with program areas on evaluation frameworks"
        ],
        "skills": ["Statistical analysis", "Data visualization", "Python", "SQL"],
        "minimum_confidence": 0.5
    }

    total += 1
    try:
        r = requests.post(
            f"{BASE_URL}/api/allocate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Allow 60s for LLM-based allocation
        )
        if check(r.status_code == 200, "Allocation returns 200"):
            passed += 1
            data = r.json()

            total += 1
            if check("recommendations" in data, "Response has 'recommendations'"):
                passed += 1

            total += 1
            recs = data.get("recommendations", [])
            if check(len(recs) > 0, f"Got {len(recs)} recommendations"):
                passed += 1

                # Check first recommendation structure
                if recs:
                    rec = recs[0]
                    total += 1
                    if check("group_code" in rec, f"First rec: {rec.get('group_code', 'N/A')}"):
                        passed += 1

                    total += 1
                    if check("confidence_score" in rec,
                            f"Confidence: {rec.get('confidence_score', 'N/A')}"):
                        passed += 1

            total += 1
            if check("provenance_map" in data, "Response has provenance_map"):
                passed += 1

    except requests.exceptions.Timeout:
        check(False, "Allocation API", "Request timed out (>30s)")
        total += 5
    except Exception as e:
        check(False, "Allocation API", str(e))
        total += 5

    # Test validation
    total += 1
    try:
        r = requests.post(
            f"{BASE_URL}/api/allocate",
            json={"position_title": "Test"},  # Missing required fields
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if check(r.status_code == 400, "Missing fields rejected (400)"):
            passed += 1
    except Exception as e:
        check(False, "Allocation validation", str(e))

    return passed, total


def test_ui_classify_step() -> Tuple[int, int]:
    """Test Classify UI elements (Phase 17)."""
    section("6. Classify UI (Step 5 Frontend)")
    passed, total = 0, 0

    try:
        r = requests.get(BASE_URL, timeout=10)
        html = r.text

        # Check Classify step in stepper
        total += 1
        if check("Classify" in html, "Classify step in stepper"):
            passed += 1

        # Check for classify-related CSS
        total += 1
        if check("classify.css" in html, "classify.css loaded"):
            passed += 1

        # Check for results cards CSS
        total += 1
        if check("results-cards.css" in html, "results-cards.css loaded"):
            passed += 1

        # Check for evidence CSS
        total += 1
        if check("evidence.css" in html, "evidence.css loaded"):
            passed += 1

    except Exception as e:
        check(False, "Classify UI check", str(e))
        total += 4

    return passed, total


def test_export_endpoints() -> Tuple[int, int]:
    """Test export API endpoints exist."""
    section("7. Export Endpoints (Step 4)")
    passed, total = 0, 0

    # These need proper payload, just check endpoints respond
    endpoints = [
        ("/api/preview", "Preview endpoint"),
        ("/api/export/pdf", "PDF export endpoint"),
        ("/api/export/docx", "DOCX export endpoint"),
    ]

    for path, name in endpoints:
        total += 1
        try:
            r = requests.post(
                f"{BASE_URL}{path}",
                json={},  # Empty body - should get 400 not 404
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            # 400 means endpoint exists and validated input
            if check(r.status_code in [400, 200], f"{name} exists"):
                passed += 1
        except Exception as e:
            check(False, name, str(e))

    return passed, total


def main():
    """Run all UAT tests."""
    print(f"\n{BOLD}JD Builder Lite - Terminal UAT Suite{RESET}")
    print(f"Testing: {BASE_URL}")

    # Check server is running
    try:
        requests.get(f"{BASE_URL}/api/ping", timeout=3)
    except:
        print(f"\n{RED}ERROR: Server not running at {BASE_URL}{RESET}")
        print("Start the server first: python -m src.app")
        sys.exit(1)

    # Run test suites
    total_passed, total_tests = 0, 0

    test_functions = [
        test_api_health,
        test_homepage,
        test_search_api,
        test_profile_api,
        test_allocate_api,
        test_ui_classify_step,
        test_export_endpoints,
    ]

    for test_fn in test_functions:
        passed, tests = test_fn()
        total_passed += passed
        total_tests += tests

    # Summary
    section("SUMMARY")
    pct = (total_passed / total_tests * 100) if total_tests > 0 else 0
    color = GREEN if pct >= 80 else YELLOW if pct >= 60 else RED

    print(f"\n  {BOLD}Total:{RESET} {total_passed}/{total_tests} tests passed ({color}{pct:.0f}%{RESET})")

    if total_passed == total_tests:
        print(f"\n  {GREEN}{BOLD}ALL TESTS PASSED{RESET}\n")
        return 0
    else:
        failed = total_tests - total_passed
        print(f"\n  {RED}{BOLD}{failed} TESTS FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
