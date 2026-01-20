"""Upload Page Object."""

from playwright.sync_api import Page
from .base_page import BasePage
from .navigation_component import NavigationComponent


class UploadPage(BasePage):
    """Page object for the upload invoice page."""
    
    # Locators
    HEADING = "h1:has-text('Upload Invoice')"
    FILE_INPUT = 'input[type="file"]'
    UPLOAD_BUTTON = 'button:has-text("Upload & Extract")'
    SUCCESS_MESSAGE = 'text=/successfully/i'
    ERROR_MESSAGE = 'text=/error|unavailable|failed/i'
    FILE_NAME_DISPLAY = "text=/invoice.*\\.pdf/i"
    
    def __init__(self, page: Page, base_url: str):
        """Initialize the upload page object."""
        super().__init__(page, base_url)
        self.url = f"{base_url}/upload"
        self.navigation = NavigationComponent(page, base_url)
        self.verify_page_loaded()
    
    def verify_page_loaded(self):
        """Verify that the upload page is loaded correctly."""
        self.page.wait_for_url("**/upload", timeout=5000)
        assert "upload" in self.page.url.lower()
    
    def is_heading_visible(self):
        """Check if upload heading is visible."""
        return self.page.locator(self.HEADING).is_visible(timeout=3000)
    
    def is_file_input_present(self):
        """Check if file input exists."""
        return self.page.locator(self.FILE_INPUT).count() > 0
    
    def is_upload_button_visible(self):
        """Check if upload button is visible."""
        return self.page.locator(self.UPLOAD_BUTTON).is_visible()
    
    def select_file(self, file_path: str):
        """
        Select a file for upload.
        
        Args:
            file_path: Path to the file to upload
        """
        self.page.locator(self.FILE_INPUT).set_input_files(file_path)
    
    def is_file_name_displayed(self):
        """Check if selected file name is displayed."""
        try:
            return self.page.locator(self.FILE_NAME_DISPLAY).is_visible(timeout=3000)
        except Exception:
            return False  # Tolerate UI delays
    
    def upload_invoice(self, file_path: str):
        """
        Upload an invoice file.
        Returns InvoicePage if successful, or self if it fails/times out.
        
        Args:
            file_path: Path to the invoice file
            
        Returns:
            InvoicePage or UploadPage depending on outcome
        """
        from .invoice_page import InvoicePage
        
        self.select_file(file_path)
        self.page.locator(self.UPLOAD_BUTTON).click()
        
        # Try to detect success and navigate to invoice page
        try:
            success = self.page.locator(self.SUCCESS_MESSAGE)
            if success.is_visible(timeout=120000):
                return InvoicePage(self.page, self.base_url)
        except Exception:
            try:
                self.page.wait_for_url("**/invoice/**", timeout=120000)
                return InvoicePage(self.page, self.base_url)
            except Exception:
                # Upload might have failed or timed out
                return self
    
    def is_success_message_visible(self):
        """Check if success message is visible."""
        try:
            return self.page.locator(self.SUCCESS_MESSAGE).is_visible(timeout=5000)
        except Exception:
            return False
    
    def is_error_message_visible(self):
        """Check if error message is visible."""
        try:
            return self.page.locator(self.ERROR_MESSAGE).is_visible(timeout=2000)
        except Exception:
            return False
    
    def navigate_to_invoices(self):
        """Navigate to invoices page."""
        return self.navigation.navigate_to_invoices()
    
    def navigate_to_dashboard(self):
        """Navigate to dashboard page."""
        return self.navigation.navigate_to_dashboard()
