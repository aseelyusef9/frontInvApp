class Navbar:
    def __init__(self, page):
        self.page = page

    UPLOAD = 'nav a[href="/upload"]'
    INVOICES = 'nav a[href="/invoices"]'
    DASHBOARD = 'nav a[href="/dashboard"]'

    def go_upload(self):
        self.page.locator(self.UPLOAD).first.click()

    def go_invoices(self):
        self.page.locator(self.INVOICES).first.click()

    def go_dashboard(self):
        self.page.locator(self.DASHBOARD).first.click()
