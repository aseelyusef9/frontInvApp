"""Dashboard Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage
from .navigation_component import NavigationComponent


class DashboardPage(BasePage):
    """Page object for the dashboard page."""
    
    # Locators
    HEADING = "h1:has-text('Dashboard')"
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the dashboard page object."""
        super().__init__(page, base_url)
        self.url = f"{base_url}/dashboard"
        self.navigation = NavigationComponent(page, base_url)
        self.verify_page_loaded()
    
    def verify_page_loaded(self):
        """Verify that the dashboard page is loaded correctly."""
        self.page.wait_for_url("**/dashboard", timeout=5000)
        assert "dashboard" in self.page.url.lower()
    
    def is_heading_visible(self):
        """Check if dashboard heading is visible."""
        return self.page.locator(self.HEADING).is_visible(timeout=3000)
    
    def navigate_to_upload(self):
        """Navigate to upload page."""
        return self.navigation.navigate_to_upload()
    
    def navigate_to_invoices(self):
        """Navigate to invoices page."""
        return self.navigation.navigate_to_invoices()
