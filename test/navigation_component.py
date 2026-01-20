"""Navigation Component - Reusable navigation bar component."""

from playwright.sync_api import Page


class NavigationComponent:
    """Component representing the navigation bar."""
    
    # Navigation links
    DASHBOARD_LINK = 'nav a[href="/dashboard"]'
    UPLOAD_LINK = 'nav a[href="/upload"]'
    INVOICES_LINK = 'nav a[href="/invoices"]'
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the navigation component."""
        self.page = page
        self.base_url = base_url
    
    def is_upload_link_visible(self):
        """Check if upload link is visible in navigation."""
        return self.page.locator(self.UPLOAD_LINK).first.is_visible()
    
    def is_invoices_link_visible(self):
        """Check if invoices link is visible in navigation."""
        return self.page.locator(self.INVOICES_LINK).first.is_visible()
    
    def is_dashboard_link_visible(self):
        """Check if dashboard link is visible in navigation."""
        return self.page.locator(self.DASHBOARD_LINK).first.is_visible()
    
    def navigate_to_upload(self):
        """Navigate to upload page via navigation bar."""
        from upload_page import UploadPage
        self.page.locator(self.UPLOAD_LINK).first.click()
        return UploadPage(self.page, self.base_url)
    
    def navigate_to_invoices(self):
        """Navigate to invoices page via navigation bar."""
        from invoices_page import InvoicesPage
        self.page.locator(self.INVOICES_LINK).first.click()
        return InvoicesPage(self.page, self.base_url)
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard page via navigation bar."""
        from dashboard_page import DashboardPage
        self.page.locator(self.DASHBOARD_LINK).first.click()
        return DashboardPage(self.page, self.base_url)
