from .base_page import BasePage
from .navbar import Navbar
from .upload_page import UploadPage

class DashboardPage(BasePage):
    HEADING = "h1:has-text('Dashboard')"
    QUICK_UPLOAD = "text=Upload Invoice"

    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.nav = Navbar(page)

    def wait_loaded(self, timeout=5000):
        self.page.wait_for_url("**/dashboard", timeout=timeout)
        return self

    def dashboard_heading_visible(self) -> bool:
        return self.page.locator(self.HEADING).is_visible(timeout=3000)

    def click_quick_upload(self) -> UploadPage:
        self.page.click(self.QUICK_UPLOAD)
        return UploadPage(self.page, self.base_url)
