"""
UAT Screenshot Test - Captures screenshots at each step for visual review.

Run with: pytest tests/test_uat_screenshots.py -v --headed
Screenshots saved to: tests/screenshots/

Requires: pip install playwright pytest-playwright
         playwright install chromium
"""
import pytest
from playwright.sync_api import Page, expect
from pathlib import Path
import time

# Screenshot output directory
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

BASE_URL = "http://localhost:5000"


def save_screenshot(page: Page, name: str):
    """Save screenshot with timestamp."""
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    print(f"📸 Screenshot saved: {path}")


@pytest.fixture(scope="function")
def page(browser):
    """Create a new page for each test."""
    context = browser.new_context(viewport={"width": 1400, "height": 900})
    page = context.new_page()
    yield page
    context.close()


class TestClassificationFlow:
    """Test the Classification Step 1 flow with screenshots."""

    def test_full_classification_flow(self, page: Page):
        """Complete flow: Search -> Select Profile -> Select Activity -> Classify"""

        # Step 1: Load homepage
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        save_screenshot(page, "01_homepage")

        # Step 2: Search for a job
        search_input = page.locator("#search-input")
        search_input.fill("policy analyst")
        page.locator("#search-button").click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)  # Wait for results to render
        save_screenshot(page, "02_search_results")

        # Step 3: Select first profile
        first_result = page.locator(".oasis-card").first
        first_result.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save_screenshot(page, "03_profile_loaded")

        # Step 4: Select a key activity (first checkbox in key_activities section)
        key_activities_section = page.locator('[data-section="key_activities"]')
        if key_activities_section.count() > 0:
            first_checkbox = key_activities_section.locator('input[type="checkbox"]').first
            first_checkbox.click()
            time.sleep(0.5)
            save_screenshot(page, "04_activity_selected")

        # Step 5: Check stepper state
        save_screenshot(page, "05_stepper_state")

        # Step 6: Click Classify (Step 5 in stepper)
        classify_btn = page.locator('.jd-stepper__btn[data-step="5"]')
        if classify_btn.is_enabled():
            classify_btn.click()
            # Wait for classification to complete (may take a while)
            page.wait_for_selector("#classify-section:not(.hidden)", timeout=60000)
            time.sleep(2)  # Let results render
            save_screenshot(page, "06_classification_loading")

            # Wait for results or error
            try:
                page.wait_for_selector(".recommendation-card, .classify-error", timeout=120000)
                time.sleep(1)
                save_screenshot(page, "07_classification_results")
            except:
                save_screenshot(page, "07_classification_timeout")
        else:
            save_screenshot(page, "06_classify_btn_disabled")

        # Step 7: Expand first recommendation card if exists
        first_card = page.locator(".recommendation-card").first
        if first_card.count() > 0:
            first_card.click()
            time.sleep(0.5)
            save_screenshot(page, "08_card_expanded")

        print(f"\n✅ All screenshots saved to: {SCREENSHOT_DIR}")


class TestStepperNavigation:
    """Test stepper navigation states."""

    def test_stepper_enables_correctly(self, page: Page):
        """Verify stepper buttons enable/disable at correct times."""

        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")

        # Initial state - only step 1 enabled
        step5_btn = page.locator('.jd-stepper__btn[data-step="5"]')
        assert step5_btn.is_disabled(), "Step 5 should be disabled initially"
        save_screenshot(page, "stepper_01_initial")

        # After search
        page.locator("#search-input").fill("analyst")
        page.locator("#search-button").click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save_screenshot(page, "stepper_02_after_search")

        # After selecting profile
        page.locator(".oasis-card").first.click()
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        save_screenshot(page, "stepper_03_after_profile")

        # After selecting activity
        checkbox = page.locator('[data-section="key_activities"] input[type="checkbox"]').first
        if checkbox.count() > 0:
            checkbox.click()
            time.sleep(1)
            save_screenshot(page, "stepper_04_after_selection")

            # Check if Step 5 is now enabled
            is_enabled = not step5_btn.is_disabled()
            print(f"Step 5 enabled after selection: {is_enabled}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])
