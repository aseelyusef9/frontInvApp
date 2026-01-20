"""Browser Factory for multi-browser and multi-resolution testing."""

import os
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Tuple, Optional


class BrowserFactory:
    """Factory class to create browser instances based on environment variables."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Get configuration from environment variables
        self.browser_name = os.getenv('BROWSER', 'chrome').lower()
        self.headless = os.getenv('HEADLESS', 'false').lower() == 'true'
        self.screen_width = int(os.getenv('SCREEN_WIDTH', '1920'))
        self.screen_height = int(os.getenv('SCREEN_HEIGHT', '1080'))
        self.base_url = os.getenv('APP_URL', 'http://localhost:3000')
    
    def create_browser(self) -> Tuple[Browser, BrowserContext, Page]:
        """
        Create and configure browser instance.
        
        Returns:
            Tuple of (browser, context, page)
        """
        self.playwright = sync_playwright().start()
        
        # Select browser based on environment variable
        if self.browser_name == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_name == 'webkit':
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        else:  # Default to chromium (for 'chrome' or anything else)
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        
        # Create context with specified viewport
        self.context = self.browser.new_context(
            viewport={'width': self.screen_width, 'height': self.screen_height},
            base_url=self.base_url
        )
        
        # Create page
        self.page = self.context.new_page()
        
        return self.browser, self.context, self.page
    
    def close(self):
        """Close browser and cleanup resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
