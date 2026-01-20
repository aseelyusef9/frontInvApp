from .base_page import BasePage

class UploadPage(BasePage):
    HEADING = "h1:has-text('Upload Invoice')"
    FILE_INPUT = 'input[type="file"]'
    UPLOAD_BTN = 'button:has-text("Upload & Extract")'
    REMOVE_BTN = 'button:has-text("Remove")'
    TOAST = '[data-sonner-toast]'

    def wait_loaded(self, timeout=5000):
        self.page.wait_for_url("**/upload", timeout=timeout)
        return self

    def heading_visible(self) -> bool:
        return self.page.locator(self.HEADING).is_visible(timeout=3000)

    def upload_button(self):
        return self.page.locator(self.UPLOAD_BTN)

    def set_file(self, file_path: str):
        self.page.set_input_files(self.FILE_INPUT, file_path)
        return self

    def click_upload(self):
        self.page.click(self.UPLOAD_BTN)
        return self

    def click_remove_if_exists(self):
        btn = self.page.locator(self.REMOVE_BTN)
        if btn.count() > 0:
            btn.click()
        return self

    def wait_toast(self, timeout=5000) -> str:
        self.page.wait_for_selector(self.TOAST, timeout=timeout)
        return self.page.locator(self.TOAST).first.inner_text()

    def wait_invoice_url(self, invoice_id: str, timeout=15000):
        self.page.wait_for_url(f"**/invoice/{invoice_id}", timeout=timeout)
        return self
