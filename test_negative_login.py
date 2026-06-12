"""
tests/test_negative_login.py
============================
Suite 3 – Negative / Boundary / Security Login Scenarios
=========================================================

Verifies that the login form REJECTS invalid inputs and displays clear,
helpful (but not security-revealing) error messages.

QA Focus areas:
  ❌ TC_NEG_001 – Empty credentials (both fields blank)
  ❌ TC_NEG_002 – Empty username only
  ❌ TC_NEG_003 – Empty password only
  ❌ TC_NEG_004 – Invalid username + invalid password
  ❌ TC_NEG_005 – Valid username + wrong password
  ❌ TC_NEG_006 – Wrong username + valid password
  ❌ TC_NEG_007 – SQL Injection attempt
  ❌ TC_NEG_008 – XSS payload in username
  ❌ TC_NEG_009 – Extremely long input (buffer overflow / DoS check)
  ❌ TC_NEG_010 – Whitespace-only credentials
  ❌ TC_NEG_011 – Special characters in credentials
  ❌ TC_NEG_012 – Multiple rapid failed attempts (brute-force check)
"""

import sys
import os
import pytest
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pages.login_page import LoginPage
from utils.helpers import (
    Credentials,
    ExpectedMessages,
    take_screenshot,
    wait_for_url_change,
    contains_any,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def login_page(driver):
    """
    Navigate to the landing page AND open the login modal.
    QAPilot uses a modal — every negative test must see the modal first.
    """
    page = LoginPage(driver)
    page.open_and_show_modal()
    return page


# ─────────────────────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────────────────────

def _assert_no_login(driver, original_url: str, test_id: str) -> str:
    """
    Assert that login did NOT succeed.

    Strategy for QAPilot (modal SPA):
      - If the user is still on the login modal (email field visible) → NOT logged in ✅
      - If the URL changed to a new route → LOGGED IN ❌ (test fail)
      - If a dashboard-specific element appeared → LOGGED IN ❌ (test fail)

    Returns the error message text (if any) for further assertions.
    """
    import time as _time
    _time.sleep(2)  # brief settle to let any redirect/success play out

    current_url = driver.current_url
    url_changed = current_url != original_url

    login_page_obj = LoginPage(driver)
    error_msg      = login_page_obj.get_error_message(timeout=4)

    # Native browser HTML5 validation tooltip text
    native_validation = login_page_obj.get_browser_validation_message()

    # Check whether a dashboard-only element appeared
    try:
        dash_el = driver.find_element(*LoginPage.DASHBOARD_INDICATOR)
        dashboard_visible = dash_el.is_displayed()
    except Exception:
        dashboard_visible = False

    take_screenshot(driver, test_id)
    print(f"\n  🌐 URL changed (bad): {url_changed} → {current_url}")
    print(f"  📊 Dashboard visible: {dashboard_visible}")
    print(f"  ❌ Error message:     '{error_msg}'")
    if native_validation:
        print(f"  🔍 Browser validation: '{native_validation}'")

    login_succeeded = url_changed or dashboard_visible

    assert not login_succeeded, (
        f"{test_id}: Login SHOULD have FAILED but was detected as successful!\n"
        f"  URL changed: {url_changed} → {current_url}\n"
        f"  Dashboard visible: {dashboard_visible}"
    )
    return error_msg


# ─────────────────────────────────────────────────────────────────────────────
# Negative — Empty Field Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestEmptyFields:

    def test_TC_NEG_001_empty_username_and_password(self, driver, login_page):
        """
        TC_NEG_001 – Both Fields Empty
        --------------------------------
        Given: Both username and password are empty
        When:  Login is clicked
        Then:  Form is NOT submitted / error is displayed

        Expected: Error or browser validation prevents submission.
        """
        original_url = login_page.get_current_url()
        login_page.submit_empty_form()

        error_msg = _assert_no_login(driver, original_url, "TC_NEG_001_empty_both")

        # Either a custom error message OR the browser's native validation fires
        # (native validation prevents the form from even submitting, which is fine)
        print(f"  ℹ️  Error/validation response: '{error_msg or 'Browser native validation'}'")

    def test_TC_NEG_002_empty_username_only(self, driver, login_page):
        """
        TC_NEG_002 – Username Empty, Password Filled
        ---------------------------------------------
        Given: Username is blank, password has a valid value
        When:  Login is clicked
        Then:  Login is rejected with an appropriate message

        Expected: Error message about missing username / required field
        """
        original_url = login_page.get_current_url()

        login_page.enter_password(Credentials.VALID["password"])
        login_page.click_login()

        error_msg = _assert_no_login(driver, original_url, "TC_NEG_002_empty_username")
        print(f"  ✏️  Error message: '{error_msg}'")

    def test_TC_NEG_003_empty_password_only(self, driver, login_page):
        """
        TC_NEG_003 – Username Filled, Password Empty
        ---------------------------------------------
        Given: Username has a valid value, password is blank
        When:  Login is clicked
        Then:  Login is rejected with an appropriate message

        Expected: Error message about missing password / required field
        """
        original_url = login_page.get_current_url()

        login_page.enter_email(Credentials.VALID["email"])
        login_page.click_login()

        error_msg = _assert_no_login(driver, original_url, "TC_NEG_003_empty_password")
        print(f"  ✏️  Error message: '{error_msg}'")


# ─────────────────────────────────────────────────────────────────────────────
# Negative — Wrong Credential Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestInvalidCredentials:

    def test_TC_NEG_004_invalid_username_and_password(self, driver, login_page):
        """
        TC_NEG_004 – Both Username and Password Invalid
        ------------------------------------------------
        Given: Completely wrong username and password
        When:  Login is clicked
        Then:  An error message appears; no redirect occurs

        Expected: Error message containing "invalid", "incorrect", or similar
        """
        creds = Credentials.INVALID_BOTH
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        error_msg = _assert_no_login(driver, original_url, "TC_NEG_004_invalid_both")

        assert error_msg, (
            "No error message displayed for invalid credentials — "
            "the user receives no feedback."
        )
        print(f"  ✅ Error message confirmed: '{error_msg}'")

    def test_TC_NEG_005_valid_username_wrong_password(self, driver, login_page):
        """
        TC_NEG_005 – Correct Username, Wrong Password
        -----------------------------------------------
        Given: Valid username but incorrect password
        When:  Login is clicked
        Then:  Login rejected; error message shown

        Expected: Generic error (not 'password incorrect' — that reveals user existence)
        """
        creds = Credentials.INVALID_PASSWORD
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        error_msg = _assert_no_login(driver, original_url, "TC_NEG_005_wrong_password")

        assert error_msg, "No error shown for wrong password — UX defect."

        # Security check: message should NOT say "password is wrong" (user enumeration risk)
        reveals_field = any(phrase in error_msg.lower()
                           for phrase in ["password is wrong", "password incorrect", "wrong password"])
        if reveals_field:
            print(
                f"\n  ⚠️  SECURITY NOTE: Error message reveals which field is wrong: '{error_msg}'"
                "\n      Consider a generic message like 'Invalid credentials'."
            )
        print(f"  ✅ Error message: '{error_msg}'")

    def test_TC_NEG_006_wrong_username_valid_password(self, driver, login_page):
        """
        TC_NEG_006 – Wrong Username, Correct Password
        ----------------------------------------------
        Given: Incorrect username but valid password
        When:  Login is clicked
        Then:  Login rejected; error message shown

        Expected: Same error message as TC_NEG_005 (prevents user enumeration)
        """
        creds = Credentials.INVALID_USERNAME
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        error_msg = _assert_no_login(driver, original_url, "TC_NEG_006_wrong_username")

        assert error_msg, "No error shown for wrong username — UX defect."
        print(f"  ✅ Error message: '{error_msg}'")

    def test_TC_NEG_007_error_message_is_user_friendly(self, driver, login_page):
        """
        TC_NEG_007 – Error Message Quality Check
        ----------------------------------------
        The error message should:
          - Be visible and readable
          - Not expose technical stack traces
          - Not say "500 Internal Server Error" etc.

        Expected: A clean, friendly message
        """
        creds = Credentials.INVALID_BOTH
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])

        error_msg = LoginPage(driver).get_error_message(timeout=6)
        take_screenshot(driver, "TC_NEG_007_error_quality")

        print(f"\n  ❌ Error message: '{error_msg}'")

        if error_msg:
            # These patterns indicate stack traces leaking to the UI
            bad_patterns = ["stack", "traceback", "exception", "500", "null pointer",
                            "undefined", "cannot read property", "syntaxerror"]
            leaks_stack = any(pat in error_msg.lower() for pat in bad_patterns)
            assert not leaks_stack, (
                f"SECURITY/UX DEFECT: Error message leaks technical details: '{error_msg}'"
            )
            print("  ✅ Error message is clean — no technical stack traces.")
        else:
            print("  ℹ️  No error message shown (browser validation may have fired).")


# ─────────────────────────────────────────────────────────────────────────────
# Negative — Security & Boundary Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestSecurityAndBoundary:

    def test_TC_NEG_008_sql_injection_attempt(self, driver, login_page):
        """
        TC_NEG_008 – SQL Injection in Login Fields
        -------------------------------------------
        Given: SQL injection payloads as credentials
        When:  Login is submitted
        Then:  Login FAILS; no server error is exposed; system remains stable

        Expected: PASS (login rejected), FAIL if injection succeeds
        Security Risk: HIGH if login succeeds with SQL injection
        """
        creds = Credentials.SQL_INJECTION
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        take_screenshot(driver, "TC_NEG_008_sql_injection")

        url_changed = wait_for_url_change(driver, original_url, timeout=5)
        error_msg   = login_page.get_error_message(timeout=5)

        print(f"\n  💉 SQL Injection payload attempted")
        print(f"  🌐 URL changed (DANGEROUS if True): {url_changed}")
        print(f"  ❌ Error message: '{error_msg}'")

        assert not url_changed, (
            "🚨 CRITICAL SECURITY DEFECT: SQL Injection payload logged in successfully! "
            "The application is vulnerable to SQL injection."
        )
        # Check that the server didn't crash with a 5xx-class error page
        # Note: native browser validation may show 'syntax error' in tooltip, so we
        # ONLY look at the app-rendered HTML, not the native validation message.
        page_src = driver.page_source.lower()
        is_crashed =
         (
            "internal server error" in page_src
            or "<h1>500</h1>" in page_src
            or "traceback" in page_src
        )
        assert not is_crashed, (
            "⚠️ Server 500 error page exposed after SQL injection attempt."
        )
        print("  ✅ SQL injection safely handled — no server crash or successful auth.")

    def test_TC_NEG_009_xss_payload_in_username(self, driver, login_page):
        """
        TC_NEG_009 – XSS (Cross-Site Scripting) Payload
        -------------------------------------------------
        Given: A <script> tag as the username value
        When:  Login is submitted
        Then:  The script must NOT execute; login must be rejected

        Expected: PASS (payload rejected/escaped), FAIL if alert pops up
        Security Risk: HIGH if XSS executes
        """
        creds = Credentials.XSS_ATTEMPT
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        take_screenshot(driver, "TC_NEG_009_xss_attempt")

        # Check no JS alert dialog appeared (which would mean XSS succeeded)
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            alert = WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert.dismiss()
            pytest.fail("🚨 CRITICAL: XSS payload executed — alert dialog appeared!")
        except Exception:
            pass  # No alert appeared — XSS was blocked

        url_changed = wait_for_url_change(driver, original_url, timeout=5)
        assert not url_changed, "XSS payload should NOT have resulted in successful login."
        print("\n  ✅ XSS payload safely rejected — no script execution detected.")

    def test_TC_NEG_010_long_input_boundary(self, driver, login_page):
        """
        TC_NEG_010 – Extremely Long Input (300 characters)
        ---------------------------------------------------
        Given: 300-character strings in both fields
        When:  Login is submitted
        Then:  Application handles gracefully — no crash, timeout, or server error

        Expected: Login rejected cleanly, page remains stable
        Boundary: Tests against buffer overflow / DoS conditions
        """
        creds = Credentials.LONG_INPUT
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        take_screenshot(driver, "TC_NEG_010_long_input")

        url_changed = wait_for_url_change(driver, original_url, timeout=10)

        # The page should still be responsive
        assert driver.title is not None, "Page appears to have crashed after long input."
        assert not url_changed, "Long input should not result in successful login."

        print("\n  ✅ Long input handled gracefully — no crash or unexpected login.")

    def test_TC_NEG_011_whitespace_only_credentials(self, driver, login_page):
        """
        TC_NEG_011 – Whitespace-Only Credentials
        -----------------------------------------
        Given: Username and password are only spaces ('   ')
        When:  Login is submitted
        Then:  Login rejected; app should NOT treat whitespace as valid credentials

        Expected: Error or browser validation fires
        """
        creds = Credentials.SPACES_ONLY
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        take_screenshot(driver, "TC_NEG_011_whitespace_only")

        url_changed = wait_for_url_change(driver, original_url, timeout=5)
        assert not url_changed, (
            "DEFECT: Whitespace-only credentials were accepted — input validation is missing."
        )
        print("\n  ✅ Whitespace-only credentials correctly rejected.")

    def test_TC_NEG_012_special_characters_in_credentials(self, driver, login_page):
        """
        TC_NEG_012 – Special Characters in Credentials
        -----------------------------------------------
        Given: Special characters (!@#$%^&*()) as username and password
        When:  Login is submitted
        Then:  Application handles them gracefully — no crash

        Expected: Login rejected; no server error or JS error
        """
        creds = Credentials.SPECIAL_CHARS
        original_url = login_page.get_current_url()

        login_page.login(creds["username"], creds["password"])
        take_screenshot(driver, "TC_NEG_012_special_chars")

        url_changed = wait_for_url_change(driver, original_url, timeout=5)
        assert not url_changed, "Special characters should not produce a login success."

        # Ensure page is still alive
        assert "error" not in driver.title.lower() if driver.title else True, (
            "Page title shows an error after special character input."
        )
        print("\n  ✅ Special characters handled gracefully.")

    def test_TC_NEG_013_multiple_rapid_failed_attempts(self, driver, login_page):
        """
        TC_NEG_013 – Multiple Rapid Failed Login Attempts (Brute-Force Check)
        -----------------------------------------------------------------------
        Given: 5 consecutive invalid login attempts in quick succession
        When:  Each attempt is made
        Then:  All are rejected; optionally an account-lockout message appears

        Expected: All rejected; system remains stable; optional lockout noted
        Security Risk: If no rate limiting exists, brute-force is feasible
        """
        creds = Credentials.INVALID_BOTH
        lockout_keywords = ["locked", "blocked", "too many", "temporarily", "disabled", "limit"]

        for attempt in range(1, 6):
            # Re-open the page AND modal each time to get a clean form
            login_page_obj = LoginPage(driver)
            login_page_obj.open_and_show_modal()
            login_page_obj.login(creds["username"], creds["password"])

            login_succeeded = login_page_obj.is_login_success(timeout=5)
            error_msg       = login_page_obj.get_error_message(timeout=4)

            print(f"\n  🔁 Attempt {attempt}: Error='{error_msg}' | Login succeeded={login_succeeded}")
            assert not login_succeeded, f"Attempt {attempt}: Invalid credentials accepted!"

            # Check for lockout messages (informational)
            if contains_any(error_msg, lockout_keywords):
                print(f"  🔒 Account lockout triggered after attempt {attempt}.")
                break
            else:
                time.sleep(0.5)  # Small delay between attempts

        take_screenshot(driver, "TC_NEG_013_brute_force")
        # Final informational note
        print(
            "\n  ℹ️  If no lockout was triggered after 5 attempts, "
            "consider adding rate limiting / CAPTCHA for security."
        )
        assert True  # Outcome is documented, not hard-blocked
