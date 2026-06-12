"""
utils/helpers.py
================
Shared utility functions and test data used across all test modules.

Centralising test data here means:
  • A single place to update credentials when the app changes.
  • No magic strings scattered through test files.
  • Helpers reusable by any future test module.
"""

import os
import time
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver


# ─────────────────────────────────────────────────────────────────────────────
# Test Data
# ─────────────────────────────────────────────────────────────────────────────

class Credentials:
    """
    Centralised credential store.

    VALID         – credentials that should produce a successful login.
    INVALID_*     – inputs expected to trigger error messages.
    """

    # ── Positive: known-good accounts ────────────────────────────────
    VALID = {
        "email":    "admin@qapilot.com",
        "password": "Admin@1234",
    }

    VALID_ALT = {
        "email":    "test@test.com",
        "password": "Test@1234",
    }

    # ── Negative: wrong / malformed inputs ───────────────────────────
    INVALID_BOTH = {
        "username": "wrong@invalid-domain-xyz.com",
        "password": "WrongPass!99",
    }

    INVALID_PASSWORD = {
        "username": "admin@qapilot.com",   # valid email format, wrong password
        "password": "TotallyWrong_Password_!@#",
    }

    INVALID_USERNAME = {
        "username": "nonexistent_user@xyz999.com",  # valid email format, wrong user
        "password": "Admin@1234",
    }

    SQL_INJECTION = {
        "username": "' OR '1'='1",
        "password": "' OR '1'='1",
    }

    XSS_ATTEMPT = {
        "username": "<script>alert('XSS')</script>",
        "password": "anypassword",
    }

    LONG_INPUT = {
        "username": "a" * 300,
        "password": "b" * 300,
    }

    SPACES_ONLY = {
        "username": "   ",
        "password": "   ",
    }

    SPECIAL_CHARS = {
        "username": "!@#$%^&*()",
        "password": "!@#$%^&*()",
    }


class ExpectedMessages:
    """
    Partial strings expected in various error messages.
    Using *partial* matching makes tests resilient to minor wording changes.
    """
    INVALID_CREDENTIALS   = ["invalid", "incorrect", "wrong", "error", "failed", "not found"]
    REQUIRED_FIELD        = ["required", "cannot be empty", "field is required", "please", "fill"]
    INVALID_EMAIL_FORMAT  = ["valid email", "invalid email", "email format"]


# ─────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────────────────────

def take_screenshot(driver: WebDriver, name: str) -> str:
    """
    Capture a screenshot and save it to <project>/qa_tests/screenshots/.

    Args:
        driver: Active Selenium WebDriver instance.
        name:   Descriptive name (spaces replaced with underscores).

    Returns:
        Absolute path to the saved screenshot file.
    """
    screenshots_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "screenshots"
    )
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = name.replace(" ", "_").replace("/", "-")
    filename  = f"{safe_name}_{timestamp}.png"
    filepath  = os.path.join(screenshots_dir, filename)

    driver.save_screenshot(filepath)
    print(f"\n📸  Screenshot: {filepath}")
    return filepath


def contains_any(text: str, keywords: list) -> bool:
    """
    Case-insensitive check: returns True if *text* contains ANY of the keywords.

    Args:
        text:     String to search within.
        keywords: List of substrings to look for.

    Returns:
        True if at least one keyword is found.
    """
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def wait_for_url_change(driver: WebDriver, original_url: str, timeout: int = 10) -> bool:
    """
    Poll until the browser URL differs from *original_url* or timeout expires.

    Returns:
        True if the URL changed, False if it stayed the same.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if driver.current_url != original_url:
            return True
        time.sleep(0.3)
    return False


def pause(seconds: float = 1.0) -> None:
    """Brief sleep – use sparingly; prefer explicit waits in production tests."""
    time.sleep(seconds)
