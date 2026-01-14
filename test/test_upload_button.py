import os
import time
import json
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")
FIXTURES = Path(__file__).parent / "fixtures"
FIXTURES.mkdir(exist_ok=True)
SHOW_UI = bool(os.environ.get("SHOW_UI", ""))

import os  # import os for environment access and file operations
import time  # import time for potential waits (unused but kept for clarity)
import json  # import json to build mock responses
from pathlib import Path  # import Path for filesystem path helpers
from playwright.sync_api import sync_playwright  # import sync_playwright to control browsers


BASE_URL = os.environ.get("BASE_URL", "http://localhost:3000")  # base URL for the frontend under test
FIXTURES = Path(__file__).parent / "fixtures"  # directory to hold test fixtures
FIXTURES.mkdir(exist_ok=True)  # ensure fixtures directory exists
SHOW_UI = bool(os.environ.get("SHOW_UI", ""))  # toggle to run browsers headed when truthy


def make_file(path: Path, size_bytes: int = 1024, content: bytes = None):  # helper to create dummy files
    if content is None:  # if no explicit content provided
        chunk = b"0" * 1024  # 1KB chunk to write repeatedly
        with open(path, "wb") as f:  # open file for binary writing
            written = 0  # bytes written so far
            while written < size_bytes:  # loop until desired size
                to_write = min(1024, size_bytes - written)  # amount to write this iteration
                f.write(chunk[:to_write])  # write chunk slice
                written += to_write  # update written counter
    else:
        path.write_bytes(content)  # write provided bytes content directly
    return path  # return the path for convenience


def setup_sample_files():  # create sample, bad and large files used by tests
    pdf = FIXTURES / "sample.pdf"  # sample pdf fixture path
    if not pdf.exists():  # only create if missing
        make_file(pdf, size_bytes=1024 * 10)  # create a small 10KB dummy pdf

    txt = FIXTURES / "bad.txt"  # invalid file type fixture
    if not txt.exists():  # create if missing
        txt.write_text("this is not a pdf")  # write simple text content

    big = FIXTURES / "big.pdf"  # large file fixture path
    if not big.exists():  # create if absent
        make_file(big, size_bytes=(10 * 1024 * 1024) + 1024)  # slightly over 10MB


def launch_browser(show_ui: bool = False):  # start Playwright and a browser context
    p = sync_playwright().start()  # start the Playwright driver
    if show_ui:  # if headed requested
        browser = p.chromium.launch(headless=False, slow_mo=250)  # launch headed with slight slow-down
    else:
        browser = p.chromium.launch(headless=True)  # otherwise run headless
    ctx = browser.new_context()  # create a new browser context
    page = ctx.new_page()  # open a new page in the context
    return p, browser, ctx, page  # return Playwright handle, browser and page


def ensure_authenticated(page):  # set demo auth flag in localStorage to bypass login
    try:
        page.goto(BASE_URL)  # navigate to base to ensure localStorage is available
    except Exception:
        pass  # ignore navigation errors during setup
    page.evaluate("() => localStorage.setItem('isAuthenticated','true')")  # set demo auth flag
    try:
        page.reload()  # reload so protected routes read the updated localStorage
    except Exception:
        pass  # ignore reload errors


def teardown_browser(p, browser):  # close browser and stop Playwright
    try:
        browser.close()  # close browser gracefully
    finally:
        p.stop()  # always stop the Playwright driver


def test_quick_action_navigates_to_upload():  # test quick-action tile navigates to upload page
    setup_sample_files()  # ensure fixtures exist
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # launch browser (headed when SHOW_UI)
    try:
        ensure_authenticated(page)  # set auth in localStorage
        page.click('text=Upload Invoice')  # click the quick action with text
        page.wait_for_url("**/upload", timeout=5000)  # wait for upload route
        assert "/upload" in page.url  # assert we're on upload page
    finally:
        teardown_browser(p, browser)  # cleanup


def test_file_input_enable_remove_and_button_state():  # test file input enables button and remove works
    setup_sample_files()  # prepare fixtures
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # start browser
    try:
        ensure_authenticated(page)  # mark authenticated
        page.goto(f"{BASE_URL}/upload")  # navigate to upload page
        upload_btn = page.locator('button:has-text("Upload & Extract")')  # locate upload button
        assert upload_btn.is_disabled()  # expect disabled initially

        sample = FIXTURES / "sample.pdf"  # sample file path
        page.set_input_files('input[type="file"]', str(sample))  # attach file to input
        assert upload_btn.is_enabled()  # button should now be enabled

        remove_btn = page.locator('button:has-text("Remove")')  # find remove button if present
        if remove_btn.count() > 0:  # if UI shows remove
            remove_btn.click()  # click remove
            assert upload_btn.is_disabled()  # upload button returns to disabled
    finally:
        teardown_browser(p, browser)  # cleanup


def test_reject_invalid_file_type_shows_toast():  # invalid file type should show an error toast
    setup_sample_files()  # ensure fixtures
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # launch browser
    try:
        ensure_authenticated(page)  # set auth
        page.goto(f"{BASE_URL}/upload")  # go to upload page
        bad = FIXTURES / "bad.txt"  # invalid file fixture
        page.set_input_files('input[type="file"]', str(bad))  # attach invalid file
        page.wait_for_selector('[data-sonner-toast]', timeout=3000)  # wait for sonner toast
        toast = page.locator('[data-sonner-toast]').first  # get first toast
        txt = toast.inner_text()  # read toast text
        assert 'invalid' in txt.lower() or 'pdf' in txt.lower()  # assert message mentions invalid/pdf
    finally:
        teardown_browser(p, browser)  # cleanup


def test_large_file_shows_size_error():  # oversized file should trigger size error toast
    setup_sample_files()  # create fixtures
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # start browser
    try:
        ensure_authenticated(page)  # set auth flag
        page.goto(f"{BASE_URL}/upload")  # visit upload
        big = FIXTURES / "big.pdf"  # large file path
        page.set_input_files('input[type="file"]', str(big))  # attach large file
        page.wait_for_selector('[data-sonner-toast]', timeout=3000)  # wait for toast
        toast = page.locator('[data-sonner-toast]').first  # get the toast
        txt = toast.inner_text()  # read its text
        assert 'size' in txt.lower() or '10mb' in txt.lower()  # assert size-related message
    finally:
        teardown_browser(p, browser)  # cleanup


def test_upload_failure_shows_error_toast():  # backend failure should show error toast
    setup_sample_files()  # ensure fixtures
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # launch browser
    try:
        def handle(route, request):  # route handler to mock /extract with 500
            if request.method == 'POST' and '/extract' in request.url:
                route.fulfill(status=500, body=b'Internal Error')  # respond with 500
            else:
                route.continue_()  # otherwise continue normally

        page.route("**/extract", handle)  # register route mock
        ensure_authenticated(page)  # set demo auth
        page.goto(f"{BASE_URL}/upload")  # visit upload page
        sample = FIXTURES / "sample.pdf"  # sample file
        page.set_input_files('input[type="file"]', str(sample))  # set input files
        page.click('button:has-text("Upload & Extract")')  # click upload button
        page.wait_for_selector('[data-sonner-toast]', timeout=5000)  # wait for error toast
        toast = page.locator('[data-sonner-toast]').first  # first toast element
        assert 'error' in toast.inner_text().lower() or 'failed' in toast.inner_text().lower()  # expect error text
    finally:
        teardown_browser(p, browser)  # cleanup


def test_upload_success_navigates_to_invoice():  # successful upload should navigate to invoice page
    setup_sample_files()  # ensure fixtures present
    p, browser, ctx, page = launch_browser(show_ui=SHOW_UI)  # start browser
    try:
        def handle_ok(route, request):  # mock handler returning successful extract response
            if request.method == 'POST' and '/extract' in request.url:
                body = json.dumps({
                    'data': {
                        'InvoiceId': 'FAKE-123',
                        'VendorName': 'Mock Vendor',
                        'InvoiceTotal': 123.45,
                        'Items': [],
                    }
                })  # mocked backend response body
                route.fulfill(status=200, body=body, headers={'Content-Type': 'application/json'})  # send JSON
            else:
                route.continue_()  # let other requests pass

        page.route("**/extract", handle_ok)  # register the success mock
        ensure_authenticated(page)  # mark user as authenticated in localStorage
        page.goto(f"{BASE_URL}/upload")  # go to upload page
        sample = FIXTURES / "sample.pdf"  # sample file path
        page.set_input_files('input[type="file"]', str(sample))  # attach file
        page.click('button:has-text("Upload & Extract")')  # initiate upload
        page.wait_for_timeout(1500)  # short wait for frontend processing
        debug_dir = FIXTURES / 'debug'  # debug artifacts directory
        debug_dir.mkdir(exist_ok=True)  # ensure debug dir exists
        page.screenshot(path=str(debug_dir / 'upload_success_debug.png'), full_page=True)  # capture screenshot
        print('CURRENT_URL_AFTER_UPLOAD:', page.url)  # print current URL for debug
        try:
            page.wait_for_url("**/invoice/FAKE-123", timeout=15000)  # wait for invoice navigation
        except Exception:
            (debug_dir / 'upload_success.html').write_text(page.content())  # save HTML on failure
            raise  # re-raise error after saving state
        assert 'FAKE-123' in page.url  # assert navigation contains invoice id
    finally:
        teardown_browser(p, browser)  # cleanup

