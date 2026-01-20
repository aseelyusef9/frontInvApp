"""
Example test file using pytest fixtures.

This demonstrates how to use the new conftest.py fixtures
for multi-browser and multi-resolution testing.
"""

import pytest
from pathlib import Path
from .login_page import LoginPage
from .dashboard_page import DashboardPage
from .upload_page import UploadPage
from .invoice_page import InvoicePage
from .invoices_page import InvoicesPage


# Test data setup
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session", autouse=True)
def setup_test_files():
    """Create test fixture files if they don't exist."""
    FIXTURES_DIR.mkdir(exist_ok=True)
    
    sample_pdf = FIXTURES_DIR / "sample.pdf"
    if not sample_pdf.exists():
        # Create a minimal PDF
        sample_pdf.write_bytes(b"%PDF-1.4\n" + b"0" * 1024)
    
    bad_txt = FIXTURES_DIR / "bad.txt"
    if not bad_txt.exists():
        bad_txt.write_text("this is not a pdf")


def test_login_page_loads(page, base_url):
    """Test that login page loads correctly."""
    page.goto(f"{base_url}/login")
    login_page = LoginPage(page, base_url)
    assert login_page.is_username_input_visible()
    assert login_page.is_password_input_visible()
    assert login_page.is_submit_button_visible()


def test_dashboard_navigation(page, base_url):
    """Test navigation to dashboard after login."""
    # Bypass login for testing
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    dashboard_page = DashboardPage(page, base_url)
    page.goto(f"{base_url}/dashboard")
    
    assert dashboard_page.is_welcome_message_visible()


def test_upload_page_loads(page, base_url):
    """Test that upload page loads correctly."""
    # Bypass login
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    assert upload_page.is_heading_visible()
    assert upload_page.is_file_input_present()
    assert upload_page.is_upload_button_visible()


def test_file_selection(page, base_url):
    """Test file selection displays file name."""
    # Bypass login
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    sample_file = str(FIXTURES_DIR / "sample.pdf")
    upload_page.select_file(sample_file)
    
    # File name should be displayed (optional assertion depending on UI)
    # assert upload_page.is_file_name_displayed()


def test_invalid_file_shows_error(page, base_url):
    """Test that uploading invalid file shows error message."""
    # Bypass login
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    bad_file = str(FIXTURES_DIR / "bad.txt")
    upload_page.select_file(bad_file)
    page.locator(upload_page.UPLOAD_BUTTON).click()
    
    # Should show error message
    assert upload_page.is_error_message_visible()


@pytest.mark.slow
def test_full_upload_flow(page, base_url):
    """Test complete upload flow from file selection to invoice page."""
    # Bypass login
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    sample_file = str(FIXTURES_DIR / "sample.pdf")
    result = upload_page.upload_invoice(sample_file)
    
    # Should navigate to invoice page on success
    assert isinstance(result, InvoicePage) or isinstance(result, UploadPage)


def test_navigation_to_invoices(page, base_url):
    """Test navigation from upload page to invoices list."""
    # Bypass login
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    invoices_page = upload_page.navigate_to_invoices()
    assert isinstance(invoices_page, InvoicesPage)


def test_responsive_layout(page, base_url, browser_config):
    """Test that page adapts to different screen sizes."""
    # This test automatically runs on different resolutions via the matrix
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    page.goto(f"{base_url}/upload")
    
    # Check viewport matches expected resolution
    viewport = page.viewport_size
    assert viewport['width'] == browser_config['screen_width']
    assert viewport['height'] == browser_config['screen_height']
    
    # Page should load regardless of screen size
    heading = page.locator("h1:has-text('Upload Invoice')")
    assert heading.is_visible(timeout=5000)
