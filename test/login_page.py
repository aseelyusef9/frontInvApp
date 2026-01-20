"""Login Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage


class LoginPage(BasePage):
    """Page object for the login page."""
    
    # Locators
    USERNAME_INPUT = 'input[id="username"]'
    PASSWORD_INPUT = 'input[id="password"]'
    SUBMIT_BUTTON = 'button[type="submit"]'
    ERROR_MESSAGE = 'text=Invalid credentials'
    TOAST_CONTAINER = '[data-sonner-toast]'
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the login page object."""
        super().__init__(page, base_url)
        self.url = f"{base_url}/login"
    
    def navigate(self):
        """Navigate to the login page."""
        self.page.goto(self.url)
        self.verify_page_loaded()
        return self
    
    def verify_page_loaded(self):
        """Verify that the login page is loaded correctly."""
        self.page.wait_for_url("**/login", timeout=5000)
        assert "login" in self.page.url.lower()
    
    def is_username_input_visible(self):
        """Check if username input is visible."""
        return self.page.locator(self.USERNAME_INPUT).is_visible()
    
    def is_password_input_visible(self):
        """Check if password input is visible."""
        return self.page.locator(self.PASSWORD_INPUT).is_visible()
    
    def is_submit_button_visible(self):
        """Check if submit button is visible."""
        return self.page.locator(self.SUBMIT_BUTTON).is_visible()
    
    def login_as_valid_user(self, username: str, password: str):
        """
        Perform login with provided credentials.
        Returns DashboardPage on successful login.
        
        Args:
            username: Username to login with
            password: Password to login with
            
        Returns:
            DashboardPage object after successful login
        """
        from dashboard_page import DashboardPage
        
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.page.locator(self.SUBMIT_BUTTON).click()
        
        # Return the next page in the user journey
        return DashboardPage(self.page, self.base_url)
    
    def login_with_invalid_credentials(self, username: str, password: str):
        """
        Attempt login with invalid credentials.
        Stays on login page.
        
        Args:
            username: Invalid username
            password: Invalid password
            
        Returns:
            Self (LoginPage) as login fails
        """
        self.page.locator(self.USERNAME_INPUT).fill(username)
        self.page.locator(self.PASSWORD_INPUT).fill(password)
        self.page.locator(self.SUBMIT_BUTTON).click()
        return self
    
    def is_error_message_visible(self):
        """
        Check if error message is displayed.
        Checks for explicit error text or toast notifications.
        
        Returns:
            True if error message is visible, False otherwise
        """
        try:
            self.page.wait_for_selector(self.ERROR_MESSAGE, timeout=3000)
            return True
        except Exception:
            try:
                self.page.wait_for_selector(self.TOAST_CONTAINER, timeout=3000)
                toast = self.page.locator(self.TOAST_CONTAINER).first
                try:
                    text = toast.inner_text()
                    if text and ('invalid' in text.lower() or 'error' in text.lower()):
                        return True
                except Exception:
                    return True  # Toast present but text unreadable
            except Exception:
                return False
    
    def take_debug_screenshot(self, path: str):
        """Take a full-page screenshot for debugging."""
        try:
            self.page.screenshot(path=path, full_page=True)
        except Exception:
            pass  # Ignore screenshot errors
