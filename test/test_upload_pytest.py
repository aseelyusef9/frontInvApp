import os
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

from pages.upload_page import UploadPage
from pages.dashboard_page import DashboardPage

BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")
FIXTURES = Path(__file__).parent / "fixtures"
SHOW_UI = bool(os.environ.get("SHOW_UI", ""))


def setup_sample_files():
    FIXTURES.mkdir(exist_ok=True)

    pdf = FIXTURES / "sample.pdf"
    if not pdf.exists():
        pdf.write_bytes(b"%PDF-1.4\n" + (b"0" * 10_000))

    txt = FIXTURES / "bad.txt"
    if not txt.exists():
        txt.write_text("this is not a pdf")

    big = FIXTURES / "big.pdf"
    if not big.exists():
        big.write_bytes(b"%PDF-1.4\n" + (b"0" * (10 * 1024 * 1024 + 1024)))

def launch(show_ui=False):
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=not show_ui, slow_mo=250 if show_ui else 0)
    ctx = browser.new_context()
    page = ctx.new_page()
    return p, browser, page

def teardown(p, browser):
    try:
        browser.close()
    finally:
        p.stop()

def ensure_authenticated(page):
    page.goto(BASE_URL)
    page.evaluate("() => localStorage.setItem('isAuthenticated','true')")
    page.reload()

def test_quick_action_navigates_to_upload():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        ensure_authenticated(page)
        dash = DashboardPage(page, BASE_URL)
        upload = dash.click_quick_upload().wait_loaded()
        assert "/upload" in page.url
    finally:
        teardown(p, browser)

def test_file_input_enable_remove_and_button_state():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        ensure_authenticated(page)
        up = UploadPage(page, BASE_URL).goto("/upload")
        assert up.upload_button().is_disabled()

        sample = str(FIXTURES / "sample.pdf")
        up.set_file(sample)
        assert up.upload_button().is_enabled()

        up.click_remove_if_exists()
        assert up.upload_button().is_disabled()
    finally:
        teardown(p, browser)

def test_reject_invalid_file_type_shows_toast():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        ensure_authenticated(page)
        up = UploadPage(page, BASE_URL).goto("/upload")
        up.set_file(str(FIXTURES / "bad.txt"))
        txt = up.wait_toast(timeout=3000).lower()
        assert ("invalid" in txt) or ("pdf" in txt)
    finally:
        teardown(p, browser)

def test_large_file_shows_size_error():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        ensure_authenticated(page)
        up = UploadPage(page, BASE_URL).goto("/upload")
        up.set_file(str(FIXTURES / "big.pdf"))
        txt = up.wait_toast(timeout=3000).lower()
        assert ("size" in txt) or ("10mb" in txt)
    finally:
        teardown(p, browser)

def test_upload_failure_shows_error_toast():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        def handle(route, request):
            if request.method == "POST" and "/extract" in request.url:
                route.fulfill(status=500, body=b"Internal Error")
            else:
                route.continue_()

        page.route("**/extract", handle)
        ensure_authenticated(page)

        up = UploadPage(page, BASE_URL).goto("/upload")
        up.set_file(str(FIXTURES / "sample.pdf")).click_upload()
        txt = up.wait_toast(timeout=5000).lower()
        assert ("error" in txt) or ("failed" in txt)
    finally:
        teardown(p, browser)

def test_upload_success_navigates_to_invoice():
    setup_sample_files()
    p, browser, page = launch(show_ui=SHOW_UI)
    try:
        def handle_ok(route, request):
            if request.method == "POST" and "/extract" in request.url:
                body = json.dumps({
                    "data": {
                        "InvoiceId": "FAKE-123",
                        "VendorName": "Mock Vendor",
                        "InvoiceTotal": 123.45,
                        "Items": []
                    }
                })
                route.fulfill(status=200, body=body, headers={"Content-Type": "application/json"})
            else:
                route.continue_()

        page.route("**/extract", handle_ok)
        ensure_authenticated(page)

        up = UploadPage(page, BASE_URL).goto("/upload")
        up.set_file(str(FIXTURES / "sample.pdf")).click_upload()
        up.wait_invoice_url("FAKE-123", timeout=15000)
        assert "FAKE-123" in page.url
    finally:
        teardown(p, browser)
