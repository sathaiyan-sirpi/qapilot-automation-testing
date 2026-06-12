"""
conftest.py
===========
Pytest configuration and shared fixtures.

This module provides:
- WebDriver setup/teardown via a session-scoped or function-scoped fixture
- Browser options (headless / headed mode)
- Screenshot capture on test failure
"""

import os
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────
BASE_URL = "https://qa-test-manager.netlify.app/"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
IMPLICIT_WAIT = 10          # seconds – fallback wait for element lookups
PAGE_LOAD_TIMEOUT = 30      # seconds – max time to wait for a page load


def pytest_addoption(parser):
    """Register a --headless CLI flag (default: headed so you can watch tests)."""
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run Chrome in headless mode (no browser window)",
    )


@pytest.fixture(scope="function")
def driver(request):
    """
    Function-scoped Chrome WebDriver fixture.

    Each test gets a fresh browser session so tests remain isolated.
    On failure the fixture captures a screenshot automatically.
    """
    # ── Browser options ───────────────────────────────────────────────
    chrome_options = Options()

    if request.config.getoption("--headless"):
        chrome_options.add_argument("--headless=new")     # Chrome ≥ 112

    chrome_options.add_argument("--window-size=1440,900")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # ── Driver initialisation ─────────────────────────────────────────
    service = Service(ChromeDriverManager().install())
    browser = webdriver.Chrome(service=service, options=chrome_options)
    browser.implicitly_wait(IMPLICIT_WAIT)
    browser.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    yield browser   # ← test body runs here

    # ── Teardown: capture screenshot if the test failed ───────────────
    if request.node.rep_call.failed if hasattr(request.node, "rep_call") else False:
        _capture_screenshot(browser, request.node.name)

    browser.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook that attaches test outcome info to the request node so the
    driver fixture can detect failures and capture screenshots.
    """
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _capture_screenshot(browser: webdriver.Chrome, test_name: str) -> None:
    """Save a timestamped PNG screenshot to the screenshots/ folder."""
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_name}_{timestamp}.png"
    path = os.path.join(SCREENSHOTS_DIR, filename)
    browser.save_screenshot(path)
    print(f"\n📸 Screenshot saved: {path}")
