"""UI Tests using Page Object Model
==================================

Basic UI tests for the Invoice Parser application.
"""

import unittest
import os
from playwright.sync_api import sync_playwright

from test.login_page import LoginPage


class TestInvParserUI(unittest.TestCase):
    """Basic UI tests for the invoice parser application."""
    
    @classmethod
    def setUpClass(cls):
        """Set up the browser once for all tests in this class."""
        cls.playwright = sync_playwright().start()
        
        show_ui = os.environ.get("SHOW_UI", "0") == "1"
        if show_ui:
            cls.browser = cls.playwright.BrowserFactory.get_page().launch(headless=True, slow_mo=500)
        else:
            cls.browser = cls.playwright.BrowserFactory.get_page().launch(headless=True)
        
        cls.base_url = "https://yolande-phalangeal-kristan.ngrok-free.dev"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests are done."""
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        """Set up before each test method."""
        self.page = self.browser.new_page()
    
    def tearDown(self):
        """Close the page after each test."""
        self.page.close()
    
    def test_page_title(self):
        """Test that the page title is correct."""
        login_page = LoginPage(self.page, self.base_url)
        self.page.goto(self.base_url)
        
        title = self.page.title()
        self.assertIn("Invoice Parser", title)
    
    def test_login_page_loads(self):
        """Test that the login page loads correctly."""
        login_page = LoginPage(self.page, self.base_url).navigate()
        
        # Verify login page elements are present
        self.assertTrue(login_page.is_username_input_visible(),
                       "Username input should be visible")
        self.assertTrue(login_page.is_password_input_visible(),
                       "Password input should be visible")
        self.assertTrue(login_page.is_submit_button_visible(),
                       "Submit button should be visible")


if __name__ == "__main__":
    unittest.main()