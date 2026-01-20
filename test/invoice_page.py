"""Invoice Detail Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage
from .navigation_component import NavigationComponent


class InvoicePage(BasePage):
    """Page object for the invoice detail page."""
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the invoice detail page object."""
        super().__init__(page, base_url)
        self.navigation = NavigationComponent(page, base_url)
        # Note: We don't call verify_page_loaded here as the URL is dynamic
    
    def verify_page_loaded(self):
        """Verify that an invoice page is loaded correctly."""
        # Invoice pages have dynamic URLs like /invoice/123
        assert "invoice" in self.page.url.lower()
    
    def navigate_to_invoices(self):
        """Navigate to invoices list page."""
        return self.navigation.navigate_to_invoices()
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard page."""
        return self.navigation.navigate_to_dashboard()
