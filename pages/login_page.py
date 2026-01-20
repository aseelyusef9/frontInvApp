from playwright.sync_api import Page
from .base_page import BasePage
from .dashboard_page import DashboardPage

class LoginPage(BasePage):
    USERNAME = 'input[id="username"]'
    PASSWORD = 'input[id="password"]'
    SUBMIT = 'button[type="submit"]'

    def open(self):
        self.goto("/login")
        return self

    def login(self, username: str, password: str) -> DashboardPage:
        self.page.fill(self.USERNAME, username)
        self.page.fill(self.PASSWORD, password)
        self.page.click(self.SUBMIT)
        return DashboardPage(self.page, self.base_url)

    def is_loaded(self) -> bool:
        return "login" in self.page.url.lower()
