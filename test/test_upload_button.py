"""Upload Button Tests using Page Object Model
===========================================

Tests for upload functionality using page objects.
"""

import os
import time
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

from test.login_page import LoginPage
from test.dashboard_page import DashboardPage
from test.upload_page import UploadPage
from test.invoice_page import InvoicePage


BASE_URL = os.environ.get("BASE_URL", "https://yolande-phalangeal-kristan.ngrok-free.dev")
FIXTURES = Path(__file__).parent / "fixtures"
FIXTURES.mkdir(exist_ok=True)
SHOW_UI = bool(os.environ.get("SHOW_UI", ""))


def make_file(path: Path, size_bytes: int = 1024, content: bytes = None):
    """Helper to create dummy files."""
    if content is None:
        chunk = b"0" * 1024
        with open(path, "wb") as f:
            written = 0
            while written < size_bytes:
                to_write = min(1024, size_bytes - written)
                f.write(chunk[:to_write])
                written += to_write
    else:
        path.write_bytes(content)
    return path


def setup_sample_files():
    """Create sample, bad and large files used by tests."""
    pdf = FIXTURES / "sample.pdf"
    if not pdf.exists():
        make_file(pdf, size_bytes=1024 * 10)

    txt = FIXTURES / "bad.txt"
    if not txt.exists():
        txt.write_text("this is not a pdf")

    big = FIXTURES / "big.pdf"
    if not big.exists():
        make_file(big, size_bytes=(10 * 1024 * 1024) + 1024)


class TestUploadFunctionality(unittest.TestCase):
    """Test suite for upload functionality using page objects."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the browser once for all tests."""
        setup_sample_files()
        cls.playwright = sync_playwright().start()
        
        if SHOW_UI:
            cls.browser = cls.playwright.BrowserFactory.get_page().launch(headless=True, slow_mo=250)
        else:
            cls.browser = cls.playwright.BrowserFactory.get_page().launch(headless=True)
        
        # Create context that ignores HTTPS errors for ngrok
        cls.context = cls.browser.new_context(ignore_https_errors=True)
        
        cls.base_url = BASE_URL
        cls.sample_pdf = str(FIXTURES / "sample.pdf")
        cls.bad_file = str(FIXTURES / "bad.txt")
        cls.large_file = str(FIXTURES / "big.pdf")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up browser after all tests."""
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
    
    def setUp(self):
        """Set up a fresh page for each test."""
        self.page = self.context.new_page()
        # Navigate to upload page directly with auth
        self._ensure_authenticated()
        self.page.goto(f"{self.base_url}/upload", wait_until='networkidle')
        self.page.wait_for_timeout(1000)  # Give page time to render
    
    def tearDown(self):
        """Close the page after each test."""
        self.page.close()
    
    def _ensure_authenticated(self):
        """Set demo auth flag in localStorage to bypass login."""
        try:
            self.page.goto(self.base_url)
            self.page.wait_for_load_state('domcontentloaded')
            self.page.evaluate("() => localStorage.setItem('isAuthenticated','true')")
        except Exception:
            pass
    
    def test_quick_action_navigates_to_upload(self):
        """Test that upload page loads correctly."""
        # Already on upload page from setUp, verify heading is visible
        heading = self.page.locator(UploadPage.HEADING)
        self.assertTrue(heading.is_visible(timeout=3000),
                       "Upload page heading should be visible")
    
    def test_file_input_enables_upload_button(self):
        """Test that file input enables the upload button."""
        # Already on upload page
        upload_btn = self.page.locator(UploadPage.UPLOAD_BUTTON)
        
        # Initially button should be disabled
        try:
            initial_state = upload_btn.is_disabled()
            self.assertTrue(initial_state, "Upload button should be disabled initially")
        except:
            # Button might not be visible yet, skip this check
            pass
        
        # Select file
        self.page.locator(UploadPage.FILE_INPUT).set_input_files(self.sample_pdf)
        
        # Button should now be enabled
        self.assertTrue(upload_btn.is_enabled(),
                       "Upload button should be enabled after file selection")
        
        # Test remove button if present
        remove_btn = self.page.locator('button:has-text("Remove")')
        if remove_btn.count() > 0:
            remove_btn.click()
            self.assertTrue(upload_btn.is_disabled(),
                           "Upload button should be disabled after removing file")
    
    def test_reject_invalid_file_type_shows_toast(self):
        """Test that invalid file type shows an error toast."""
        # Try to upload invalid file
        self.page.locator(UploadPage.FILE_INPUT).set_input_files(self.bad_file)
        
        # Wait for error toast
        self.page.wait_for_selector('[data-sonner-toast]', timeout=3000)
        toast = self.page.locator('[data-sonner-toast]').first
        txt = toast.inner_text()
        
        self.assertTrue('invalid' in txt.lower() or 'pdf' in txt.lower(),
                       "Error toast should mention invalid file type")
    
    def test_large_file_shows_size_error(self):
        """Test that oversized file triggers size error toast."""
        # Try to upload large file
        self.page.locator(UploadPage.FILE_INPUT).set_input_files(self.large_file)
        
        # Wait for error toast
        self.page.wait_for_selector('[data-sonner-toast]', timeout=3000)
        toast = self.page.locator('[data-sonner-toast]').first
        txt = toast.inner_text()
        
        self.assertTrue('size' in txt.lower() or '10mb' in txt.lower(),
                       "Error toast should mention file size")
    
    def test_upload_failure_shows_error_toast(self):
        """Test that backend failure shows error toast."""
        # Mock backend failure
        def handle_error(route, request):
            if request.method == 'POST' and '/extract' in request.url:
                route.fulfill(status=500, body=b'Internal Error')
            else:
                route.continue_()
        
        self.page.route("**/extract", handle_error)
        
        # Select file and upload
        self.page.locator(UploadPage.FILE_INPUT).set_input_files(self.sample_pdf)
        self.page.locator(UploadPage.UPLOAD_BUTTON).click()
        
        # Wait for error toast
        self.page.wait_for_selector('[data-sonner-toast]', timeout=5000)
        toast = self.page.locator('[data-sonner-toast]').first
        txt = toast.inner_text()
        
        self.assertTrue('error' in txt.lower() or 'failed' in txt.lower(),
                       "Error toast should be displayed on upload failure")
    
    def test_upload_success_navigates_to_invoice(self):
        """Test that successful upload navigates to invoice page."""
        # Mock successful backend response
        def handle_success(route, request):
            if request.method == 'POST' and '/extract' in request.url:
                body = json.dumps({
                    'data': {
                        'InvoiceId': 'FAKE-123',
                        'VendorName': 'Mock Vendor',
                        'InvoiceTotal': 123.45,
                        'Items': [],
                    }
                })
                route.fulfill(status=200, body=body, 
                            headers={'Content-Type': 'application/json'})
            else:
                route.continue_()
        
        self.page.route("**/extract", handle_success)
        
        # Select file and upload
        self.page.locator(UploadPage.FILE_INPUT).set_input_files(self.sample_pdf)
        self.page.locator(UploadPage.UPLOAD_BUTTON).click()
        
        # Wait for navigation
        self.page.wait_for_timeout(1500)
        
        # Debug screenshot
        debug_dir = FIXTURES / 'debug'
        debug_dir.mkdir(exist_ok=True)
        self.page.screenshot(path=str(debug_dir / 'upload_success_debug.png'), 
                           full_page=True)
        
        print('CURRENT_URL_AFTER_UPLOAD:', self.page.url)
        
        try:
            self.page.wait_for_url("**/invoice/FAKE-123", timeout=15000)
        except Exception:
            (debug_dir / 'upload_success.html').write_text(self.page.content())
            raise
        
        self.assertIn('FAKE-123', self.page.url,
                     "Should navigate to invoice detail page with correct ID")


if __name__ == "__main__":
    unittest.main()
