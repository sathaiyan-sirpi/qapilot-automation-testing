"""
tests/test_ui_elements.py
=========================
Suite 1 – UI Element Validation
================================

Verifies that every required visual element is present, correctly labelled,
and styled.  QAPilot uses a MODAL for login — the flow is:
  1. Land on https://qa-test-manager.netlify.app/
  2. Click the "Sign In" nav button → modal appears
  3. Modal contains email + password inputs and a Sign In submit button

QA Focus areas:
  ✅ TC_UI_001 – Page loads successfully and URL is correct
  ✅ TC_UI_002 – Browser <title> is set
  ✅ TC_UI_003 – Hero heading text exists on the landing page
  ✅ TC_UI_004 – Email input field is present in the modal
  ✅ TC_UI_005 – Password input field is present in the modal
  ✅ TC_UI_006 – Password field is MASKED (type='password')
  ✅ TC_UI_007 – Submit (Sign In) button is present and clickable
  ✅ TC_UI_008 – Email field has a descriptive placeholder
  ✅ TC_UI_009 – Password field has a placeholder
  ✅ TC_UI_010 – 'Forgot Password' link exists inside modal
  ✅ TC_UI_011 – 'Sign Up' tab/link exists inside modal
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pages.login_page import LoginPage
from utils.helpers import take_screenshot


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def page(driver):
    """Navigate to landing page (modal NOT yet open)."""
    p = LoginPage(driver)
    p.open()
    return p


@pytest.fixture
def modal_page(driver):
    """Navigate to landing page AND open the login modal."""
    p = LoginPage(driver)
    p.open_and_show_modal()
    return p


# ─────────────────────────────────────────────────────────────────────────────
# Suite 1A – Page-Level Tests (no modal needed)
# ─────────────────────────────────────────────────────────────────────────────

class TestPageLoad:

    def test_TC_UI_001_page_loads_successfully(self, driver, page):
        """
        TC_UI_001 – Page Load Success
        ------------------------------
        The landing page must load and the URL must include the expected base URL.

        Steps:
          1. Navigate to the QAPilot URL
          2. Assert current URL matches expected

        Expected: PASS
        """
        current_url = page.get_current_url()
        take_screenshot(driver, "TC_UI_001_page_load")

        assert LoginPage.URL in current_url, (
            f"Expected URL to contain '{LoginPage.URL}', but got '{current_url}'"
        )
        print(f"\n  🌐 URL confirmed: {current_url}")

    def test_TC_UI_002_page_has_title(self, driver, page):
        """
        TC_UI_002 – Browser Tab Title
        ------------------------------
        The page must have a non-empty title tag (important for SEO and usability).

        Expected: PASS — title should be non-empty (discovered: 'QAPilot')
        """
        title = page.get_page_title()
        take_screenshot(driver, "TC_UI_002_page_title")

        assert title, "Browser <title> is empty — SEO/UX defect."
        print(f"\n  📄 Page title: '{title}'")

    def test_TC_UI_003_page_has_hero_heading(self, driver, page):
        """
        TC_UI_003 – Hero Section Heading Exists
        -----------------------------------------
        The landing page must have a visible main heading for branding.

        Expected: PASS — heading contains meaningful text
        """
        heading = page.get_page_heading_text()
        take_screenshot(driver, "TC_UI_003_page_heading")

        assert heading, "No visible heading found on the landing page."
        print(f"\n  🏷️  Heading: '{heading}'")


# ─────────────────────────────────────────────────────────────────────────────
# Suite 1B – Modal Form Element Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestModalFormElements:

    def test_TC_UI_004_email_field_present_in_modal(self, driver, modal_page):
        """
        TC_UI_004 – Email Input Present Inside Login Modal
        ---------------------------------------------------
        After clicking 'Sign In' nav button, the email input must be visible.

        Expected: PASS
        """
        take_screenshot(driver, "TC_UI_004_email_field")
        assert modal_page.is_email_field_present(), (
            "Email input field not found inside the login modal."
        )
        print("\n  ✅ Email input field is present.")

    def test_TC_UI_005_password_field_present_in_modal(self, driver, modal_page):
        """
        TC_UI_005 – Password Input Present Inside Login Modal
        -------------------------------------------------------
        After opening the modal, a password input must be visible.

        Expected: PASS
        """
        take_screenshot(driver, "TC_UI_005_password_field")
        assert modal_page.is_password_field_present(), (
            "Password input field not found inside the login modal."
        )
        print("\n  ✅ Password input field is present.")

    def test_TC_UI_006_password_field_is_masked(self, driver, modal_page):
        """
        TC_UI_006 – Password Masking (Security Requirement)
        -----------------------------------------------------
        The password input MUST have type='password' to prevent
        shoulder-surfing and browser auto-exposure of the value.

        Expected: PASS — type attribute must equal 'password'
        """
        take_screenshot(driver, "TC_UI_006_password_masked")
        assert modal_page.is_password_masked(), (
            "SECURITY DEFECT: Password field is NOT masked — type != 'password'."
        )
        print("\n  🔒 Password field is correctly masked.")

    def test_TC_UI_007_submit_button_present_and_clickable(self, driver, modal_page):
        """
        TC_UI_007 – Submit 'Sign In' Button is Present and Clickable
        --------------------------------------------------------------
        The modal must have a clickable submit button.

        Expected: PASS
        """
        take_screenshot(driver, "TC_UI_007_submit_button")
        assert modal_page.is_submit_button_present(), (
            "Submit (Sign In) button not found or not clickable in the modal."
        )
        print("\n  ✅ Submit button is present and clickable.")

    def test_TC_UI_008_email_field_has_placeholder(self, driver, modal_page):
        """
        TC_UI_008 – Email Input Has Descriptive Placeholder
        -----------------------------------------------------
        The email field should have a placeholder that hints at the format.
        Expected placeholder: 'you@example.com'

        Expected: PASS
        """
        placeholder = modal_page.get_email_placeholder()
        take_screenshot(driver, "TC_UI_008_email_placeholder")

        print(f"\n  🔤 Email placeholder: '{placeholder}'")
        assert placeholder, (
            "Email field has no placeholder — users may not know what format is expected."
        )
        assert "@" in placeholder or "email" in placeholder.lower(), (
            f"Placeholder '{placeholder}' does not clearly indicate an email format."
        )

    def test_TC_UI_009_password_field_has_placeholder(self, driver, modal_page):
        """
        TC_UI_009 – Password Input Has Placeholder
        -------------------------------------------
        Password field should have some placeholder indication.

        Expected: Informational (placeholder may use dots to obscure length)
        """
        placeholder = modal_page.get_password_placeholder()
        take_screenshot(driver, "TC_UI_009_password_placeholder")

        print(f"\n  🔤 Password placeholder: '{placeholder}'")
        if placeholder:
            print("  ✅ Password placeholder is set.")
        else:
            print("  ℹ️  No password placeholder — ensure a label compensates.")


class TestModalNavigationElements:

    def test_TC_UI_010_forgot_password_link_in_modal(self, driver, modal_page):
        """
        TC_UI_010 – 'Forgot Password' Link Inside Modal
        -------------------------------------------------
        A 'Forgot password?' link should be present in the login modal
        for account recovery purposes.

        Expected: PASS (link found — confirmed present during exploration)
        """
        present = modal_page.is_forgot_password_link_present()
        take_screenshot(driver, "TC_UI_010_forgot_password")

        print(f"\n  🔗 Forgot Password link present: {present}")
        assert present, (
            "UX DEFECT: 'Forgot password?' link not found in the login modal — "
            "users cannot recover locked accounts."
        )

    def test_TC_UI_011_signup_tab_in_modal(self, driver, modal_page):
        """
        TC_UI_011 – 'Sign Up' Tab Inside Modal
        ----------------------------------------
        The modal should provide a 'Sign Up' tab to allow new user registration.

        Expected: PASS (tab found — confirmed present during exploration)
        """
        present = modal_page.is_register_link_present()
        take_screenshot(driver, "TC_UI_011_signup_tab")

        print(f"\n  🔗 Sign Up tab present: {present}")
        assert present, (
            "UX DEFECT: 'Sign Up' tab not found in the login modal — "
            "new users cannot register."
        )
