"""
pages/login_page.py
===================
Page Object Model (POM) for the QAPilot Login Modal.

QAPilot (https://qa-test-manager.netlify.app/) is a Single Page Application
with a modal-based login.  The flow is:

  1. Landing page loads
  2. User clicks "Sign In" button in the nav header
  3. A modal overlay appears with email + password fields
  4. On successful login, the modal closes and the dashboard is shown

Key discovery notes:
  - Input fields have NO id or name — located by type/placeholder
  - Email input:    type='email',    placeholder='you@example.com'
  - Password input: type='password', placeholder='••••••••'
  - Submit button:  text='Sign In' (inside the modal, not the nav button)
  - Empty-form submission triggers native browser validation
  - Error messages appear as a <div> or <p> inside the modal on wrong credentials
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class LoginPage:
    """
    Encapsulates all interactions with the QAPilot login modal.

    Typical usage:
        page = LoginPage(driver)
        page.open()          # navigate to landing page
        page.open_modal()    # click the "Sign In" nav button to reveal modal
        page.login("test@test.com", "Test@1234")
    """

    # ── URL ──────────────────────────────────────────────────────────
    URL = "https://qa-test-manager.netlify.app/"

    # ── Locators ─────────────────────────────────────────────────────

    # Nav-bar "Sign In" button that opens the modal
    SIGNIN_NAV_BUTTON = (
        By.XPATH,
        "//header//button[normalize-space(text())='Sign In'] | "
        "//nav//button[normalize-space(text())='Sign In'] | "
        "//button[normalize-space(text())='Sign In'][not(ancestor::form)]"
    )

    # Email input inside the modal
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")

    # Password input inside the modal
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")

    # Submit "Sign In" button inside the modal form
    SUBMIT_BUTTON = (
        By.XPATH,
        "//form//button[normalize-space(text())='Sign In'] | "
        "//button[@type='submit' and normalize-space(text())='Sign In'] | "
        "//button[contains(@class,'bg-blue') and normalize-space(text())='Sign In']"
    )

    # Close (×) button of the modal
    MODAL_CLOSE_BUTTON = (By.XPATH, "//button[normalize-space(text())='×']")

    # "Forgot password?" link inside the modal
    FORGOT_PASSWORD = (By.XPATH, "//button[contains(text(),'Forgot password')]")

    # "Sign Up" tab inside the modal
    SIGNUP_TAB = (By.XPATH, "//button[normalize-space(text())='Sign Up']")

    # Error / feedback element that appears on bad credentials
    # (QAPilot renders this dynamically inside the modal)
    ERROR_CONTAINER = (
        By.XPATH,
        "//*[contains(@class,'error') or contains(@class,'alert') or "
        "contains(@class,'text-red') or contains(@class,'invalid') or "
        "@role='alert' or (contains(@class,'text-') and "
        "contains(translate(normalize-space(.),'INVALID','invalid'),'invalid'))]"
    )

    # Modal overlay / dialog wrapper
    MODAL_WRAPPER = (By.CSS_SELECTOR, "[class*='modal'], [class*='overlay'], [class*='dialog'], [class*='fixed']")

    # Page heading (hero section)
    PAGE_HEADING = (By.CSS_SELECTOR, "h1, h2.text-5xl, h2.text-4xl, .text-5xl")

    # Dashboard element — confirms successful login:
    # These texts/elements ONLY appear when the user is authenticated.
    # Avoid "Sign In" / "Sign Up" since those appear on the landing page too.
    DASHBOARD_INDICATOR = (
        By.XPATH,
        "//*[("
        "  normalize-space(text())='Dashboard' or "
        "  normalize-space(text())='Log Out' or "
        "  normalize-space(text())='Logout' or "
        "  normalize-space(text())='Sign Out' or "
        "  normalize-space(text())='My Projects' or "
        "  normalize-space(text())='Test Cases' or "
        "  normalize-space(text())='New Project'"
        ") and not(ancestor::*[@style='display:none'])]"
    )

    WAIT_TIMEOUT = 15

    # ─────────────────────────────────────────────────────────────────
    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait   = WebDriverWait(driver, self.WAIT_TIMEOUT)

    # ── Navigation ───────────────────────────────────────────────────
    def open(self) -> "LoginPage":
        """Load the landing page and wait for it to be ready."""
        self.driver.get(self.URL)
        self._wait_for_page_ready()
        return self

    def open_modal(self) -> "LoginPage":
        """
        Click the 'Sign In' button in the navigation bar to reveal the
        login modal overlay.
        """
        signin_btn = self.wait.until(
            EC.element_to_be_clickable(self.SIGNIN_NAV_BUTTON)
        )
        signin_btn.click()
        # Wait for the email input to appear inside the modal
        self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
        return self

    def open_and_show_modal(self) -> "LoginPage":
        """Convenience: navigate to landing page then open the login modal."""
        self.open()
        self.open_modal()
        return self

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_page_title(self) -> str:
        return self.driver.title

    # ── Element accessors ─────────────────────────────────────────────
    def _find_visible(self, locator: tuple) -> WebElement:
        return self.wait.until(EC.visibility_of_element_located(locator))

    def _find_clickable(self, locator: tuple) -> WebElement:
        return self.wait.until(EC.element_to_be_clickable(locator))

    def get_email_field(self) -> WebElement:
        return self._find_visible(self.EMAIL_INPUT)

    def get_password_field(self) -> WebElement:
        return self._find_visible(self.PASSWORD_INPUT)

    def get_submit_button(self) -> WebElement:
        return self._find_clickable(self.SUBMIT_BUTTON)

    # ── High-level actions ────────────────────────────────────────────
    def enter_email(self, email: str) -> None:
        """Clear then type into the email field."""
        field = self.get_email_field()
        field.clear()
        field.send_keys(email)

    def enter_password(self, password: str) -> None:
        """Clear then type into the password field."""
        field = self.get_password_field()
        field.clear()
        field.send_keys(password)

    # Alias kept for backward compat with test files
    def enter_username(self, value: str) -> None:
        self.enter_email(value)

    def click_submit(self) -> None:
        """Click the modal's Sign In / submit button."""
        # Fallback: use JS click if regular click is intercepted
        try:
            self.get_submit_button().click()
        except Exception:
            btn = self.driver.find_element(*self.SUBMIT_BUTTON)
            self.driver.execute_script("arguments[0].click();", btn)

    # Alias for test backward compat
    def click_login(self) -> None:
        self.click_submit()

    def login(self, email: str, password: str) -> None:
        """
        Full login action: type email ➜ type password ➜ click submit.
        Does NOT assert the outcome.
        """
        self.enter_email(email)
        self.enter_password(password)
        self.click_submit()

    def submit_empty_form(self) -> None:
        """Click Submit without entering any text (triggers browser validation)."""
        self.click_submit()

    # ── State queries ─────────────────────────────────────────────────
    def get_error_message(self, timeout: int = 5) -> str:
        """
        Return the visible error message text, or '' if none appears.
        Also checks for browser validation tooltip via JS.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.visibility_of_element_located(self.ERROR_CONTAINER))
            return el.text.strip()
        except TimeoutException:
            pass
        return ""

    def get_browser_validation_message(self) -> str:
        """
        Return the browser's native HTML5 validation message for the email field.
        Useful when no custom error container exists.
        """
        try:
            field = self.driver.find_element(*self.EMAIL_INPUT)
            return self.driver.execute_script(
                "return arguments[0].validationMessage;", field
            )
        except Exception:
            return ""

    def get_password_validation_message(self) -> str:
        """Native validation message for password field."""
        try:
            field = self.driver.find_element(*self.PASSWORD_INPUT)
            return self.driver.execute_script(
                "return arguments[0].validationMessage;", field
            )
        except Exception:
            return ""

    def is_email_field_present(self) -> bool:
        try:
            self._find_visible(self.EMAIL_INPUT)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_password_field_present(self) -> bool:
        try:
            self._find_visible(self.PASSWORD_INPUT)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_submit_button_present(self) -> bool:
        try:
            self._find_clickable(self.SUBMIT_BUTTON)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    # Alias
    def is_username_field_present(self) -> bool:
        return self.is_email_field_present()

    def is_login_button_present(self) -> bool:
        return self.is_submit_button_present()

    def is_password_masked(self) -> bool:
        """Returns True if the password field type='password' (ensures masking)."""
        field = self.get_password_field()
        return field.get_attribute("type") == "password"

    def get_email_placeholder(self) -> str:
        return self.get_email_field().get_attribute("placeholder") or ""

    def get_password_placeholder(self) -> str:
        return self.get_password_field().get_attribute("placeholder") or ""

    # Aliases for backward compat
    def get_username_placeholder(self) -> str:
        return self.get_email_placeholder()

    def get_page_heading_text(self) -> str:
        try:
            return self._find_visible(self.PAGE_HEADING).text.strip()
        except (TimeoutException, NoSuchElementException):
            return ""

    def is_forgot_password_link_present(self) -> bool:
        try:
            self.driver.find_element(*self.FORGOT_PASSWORD)
            return True
        except NoSuchElementException:
            return False

    def is_register_link_present(self) -> bool:
        try:
            self.driver.find_element(*self.SIGNUP_TAB)
            return True
        except NoSuchElementException:
            return False

    def get_email_field_value(self) -> str:
        return self.get_email_field().get_attribute("value") or ""

    def get_password_field_value(self) -> str:
        return self.get_password_field().get_attribute("value") or ""

    # Alias
    def get_username_field_value(self) -> str:
        return self.get_email_field_value()

    def is_login_success(self, timeout: int = 8) -> bool:
        """
        Returns True only if a POSITIVE login indicator is observed:
          - A dashboard/dashboard-related element appears (Logout, Projects, etc.)
          - OR the URL changes away from the login page

        Does NOT count modal closure alone (which also happens during
        browser native validation) as a success signal.
        """
        original_url = self.driver.current_url
        deadline = time.time() + timeout
        while time.time() < deadline:
            # Positive: URL changed (SPA may hash-route to /dashboard)
            if self.driver.current_url != original_url:
                return True
            # Positive: dashboard/authenticated element visible
            try:
                el = self.driver.find_element(*self.DASHBOARD_INDICATOR)
                if el.is_displayed():
                    return True
            except NoSuchElementException:
                pass
            time.sleep(0.3)
        return False

    def get_success_message(self, timeout: int = 5) -> str:
        """Look for any success-flavoured message."""
        try:
            wait = WebDriverWait(self.driver, timeout)
            el = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@class,'success') or contains(@class,'green')]")
            ))
            return el.text.strip() if el.is_displayed() else ""
        except TimeoutException:
            return ""

    def is_dashboard_or_redirect(self) -> bool:
        """Alias to check login success without specifying timeout."""
        return self.is_login_success(timeout=5)

    def modal_is_open(self) -> bool:
        """Check if the login modal is currently visible."""
        try:
            return self.get_email_field().is_displayed()
        except Exception:
            return False

    # ── Internals ─────────────────────────────────────────────────────
    def _wait_for_page_ready(self, timeout: int = 20) -> None:
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
