"""Invoices List Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage
from .navigation_component import NavigationComponent


class InvoicesPage(BasePage):
    """Page object for the invoices list page."""
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the invoices list page object."""
        super().__init__(page, base_url)
        self.url = f"{base_url}/invoices"
        self.navigation = NavigationComponent(page, base_url)
        self.verify_page_loaded()
    
    def verify_page_loaded(self):
        """Verify that the invoices page is loaded correctly."""
        self.page.wait_for_url("**/invoices", timeout=5000)
        assert "invoices" in self.page.url.lower()
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard page."""
        return self.navigation.navigate_to_dashboard()
    
    def navigate_to_upload(self):
        """Navigate to upload page."""
        return self.navigation.navigate_to_upload()
