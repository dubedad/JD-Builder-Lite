# Testing Patterns

**Analysis Date:** 2026-03-04

## Test Framework

**Runner:**
- Pytest (based on test file structure and import patterns)
- Playwright for browser-based E2E tests
- Custom terminal-based UAT harness

**Config:**
- No `pytest.ini` or `pyproject.toml` test configuration found
- Tests discovered by naming convention: `test_*.py` and `*_test.py`

**Run Commands:**
```bash
pytest tests/test_uat_screenshots.py -v --headed
# Run playwright-based screenshot tests with browser visible

python tests/uat_terminal.py
# Run terminal-based UAT test suite
```

**Dependencies:**
- `pytest` (inferred from test structure)
- `pytest-playwright` (for browser automation)
- `playwright` (Chromium browser testing)
- Custom test utilities in test files

## Test File Organization

**Location:**
- Separate directory: `tests/` at project root
- Tests NOT co-located with source code

**Naming:**
- Test files: `test_uat_screenshots.py`, `uat_terminal.py`
- Test classes: `TestClassificationFlow` (follows PascalCase, test-specific)
- Test functions: `test_full_classification_flow()` (snake_case with `test_` prefix)

**Structure:**
```
tests/
├── test_uat_screenshots.py       # Playwright browser automation tests
├── uat_terminal.py               # Custom terminal-based UAT harness
└── screenshots/                  # Generated screenshot output (git-ignored)
```

## Test Structure

**Suite Organization:**
```python
# From tests/test_uat_screenshots.py
class TestClassificationFlow:
    """Test the Classification Step 1 flow with screenshots."""

    def test_full_classification_flow(self, page: Page):
        """Complete flow: Search -> Select Profile -> Select Activity -> Classify"""
        # Setup
        page.goto(BASE_URL, timeout=60000)
        page.wait_for_load_state("networkidle")

        # Action
        search_input = page.locator("#search-input")
        search_input.fill("analyst")
        page.locator("#search-button").click()

        # Assert (implicit via screenshot)
        save_screenshot(page, "02_search_results")
```

**Patterns:**
- Test classes group related scenarios: `TestClassificationFlow` contains full flow test
- Fixtures for setup: `@pytest.fixture(scope="function") def page(browser):`
- Page objects and locators via Playwright: `page.locator("#search-input")`, `page.wait_for_selector()`
- Screenshots as visual assertions: `save_screenshot(page, "02_search_results")`
- Terminal tests use custom `check()` helper: `check(condition, name, detail="")`

```python
# From tests/uat_terminal.py - custom assertion pattern
def check(condition: bool, name: str, detail: str = "") -> bool:
    """Print pass/fail for a test condition."""
    if condition:
        print(f"  {GREEN}[PASS]{RESET} {name}")
    else:
        print(f"  {RED}[FAIL]{RESET} {name}")
        if detail:
            print(f"    {YELLOW}-> {detail}{RESET}")
    return condition
```

## Mocking

**Framework:** Not explicitly used in sampled tests
- Playwright handles browser state/mocking via its API
- Real HTTP calls made to test server: `requests.get(f"{BASE_URL}/api/ping")`
- No `unittest.mock` or `pytest-mock` patterns observed

**What to Mock:**
- External API calls in unit tests (not seen in current test suite)
- Database operations (recommend using fixtures for test database)
- File I/O operations

**What NOT to Mock:**
- Browser behavior (Playwright handles this)
- Flask application routes (test against real server)
- Pydantic model validation (test with actual models)

## Fixtures and Factories

**Test Data:**
```python
# From tests/test_uat_screenshots.py
@pytest.fixture(scope="function")
def page(browser):
    """Create a new page for each test."""
    context = browser.new_context(viewport={"width": 1400, "height": 900})
    page = context.new_page()
    yield page
    context.close()
```

**Location:**
- Defined in test files themselves
- No separate `conftest.py` or fixtures module found

**Base URLs:**
```python
# Hardcoded in test files for easy customization
BASE_URL = "http://127.0.0.1:5000"
```

## Coverage

**Requirements:** No coverage tool configured (no `.coveragerc`, no pytest-cov in requirements)

**View Coverage:** Not applicable - no coverage measurement configured

## Test Types

**Unit Tests:**
- Not found in sampled test suite
- Expected approach: Test individual functions with isolated inputs
- Use Pydantic models for validation testing
- Test edge cases in `src/matching/confidence.py`, `src/matching/classifier.py`

**Integration Tests:**
- Not explicitly present but expected for API routes
- Would test: full `/api/search` flow with database lookup
- Would test: classification pipeline (shortlisting → LLM → confidence → evidence)

**E2E Tests:**
- **Playwright Screenshot Tests** (`tests/test_uat_screenshots.py`):
  - Full user journey from search to classification
  - Visual verification via screenshots
  - Tests browser UI interactions: clicks, form fills, waiting for elements
  - Runs against real Flask application
  - Scope: Homepage → Search → Profile Selection → Activity Selection → Classification

- **Terminal UAT Tests** (`tests/uat_terminal.py`):
  - Checks HTTP endpoints and page structure
  - Uses `requests` library for direct API testing
  - Tests: health checks, homepage loads, all stepper steps present
  - Terminal output with ANSI colors for pass/fail reporting
  - Runs before/alongside Playwright tests for quick verification

## Common Patterns

**Async Testing:**
Not applicable (no async/await patterns in Python codebase)

**Error Testing:**
```python
# From tests/uat_terminal.py - check pattern
total += 1
try:
    r = requests.get(f"{BASE_URL}/api/ping", timeout=5)
    if check(r.status_code == 200 and r.json().get("status") == "ok",
            "GET /api/ping returns 200 OK"):
        passed += 1
except Exception as e:
    check(False, "GET /api/ping", str(e))
```

**Waiting for Elements:**
```python
# From tests/test_uat_screenshots.py
page.wait_for_load_state("networkidle")
page.wait_for_selector("#search-button:has-text('Search')", timeout=30000)
page.wait_for_selector(".oasis-card", timeout=30000)
```

**Screenshot Capture:**
```python
def save_screenshot(page: Page, name: str):
    """Save screenshot with timestamp."""
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"📸 Screenshot saved: {path}")
```

## Test Execution Examples

**From `tests/test_uat_screenshots.py`:**
```python
def test_full_classification_flow(self, page: Page):
    """Complete flow: Search -> Select Profile -> Select Activity -> Classify"""

    # Step 1: Load homepage
    page.goto(BASE_URL, timeout=60000)
    page.wait_for_load_state("networkidle")
    save_screenshot(page, "01_homepage")

    # Step 2: Search for a job
    search_input = page.locator("#search-input")
    search_input.fill("analyst")
    page.locator("#search-button").click()
    # Wait for search to complete (button changes from "Searching..." back to "Search")
    page.wait_for_selector("#search-button:has-text('Search')", timeout=30000)
    time.sleep(2)  # Wait for results to render
    save_screenshot(page, "02_search_results")

    # Step 3: Select first profile
    page.wait_for_selector(".oasis-card", timeout=30000)
    first_result = page.locator(".oasis-card").first
    first_result.click()
    page.wait_for_load_state("networkidle")
    time.sleep(1)
    save_screenshot(page, "03_profile_loaded")
```

**From `tests/uat_terminal.py`:**
```python
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

    return passed, total
```

## Test Characteristics

**Focus Areas:**
- User-facing flows (E2E): Search, profile selection, classification
- API endpoints: health checks, search, profile fetch
- Page structure and HTML elements
- Visual UI state at key steps

**No unit tests found** - all tests are integration/E2E level

**No test database isolation** - tests run against real application state

**No mocking** - real HTTP calls and browser interactions

---

*Testing analysis: 2026-03-04*
