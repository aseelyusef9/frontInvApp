"""Pytest configuration and fixtures."""

import pytest
import os
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page


@pytest.fixture(scope="session")
def browser_config():
    """Get browser configuration from environment variables."""
    return {
        'browser_name': os.getenv('BROWSER', 'chrome').lower(),
        'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
        'screen_width': int(os.getenv('SCREEN_WIDTH', '1920')),
        'screen_height': int(os.getenv('SCREEN_HEIGHT', '1080')),
        'base_url': os.getenv('APP_URL', 'http://localhost:3000')
    }


@pytest.fixture(scope="session")
def playwright_instance():
    """Create and manage Playwright instance for the test session."""
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def browser(playwright_instance, browser_config):
    """Create browser instance based on configuration."""
    browser_name = browser_config['browser_name']
    headless = browser_config['headless']
    
    # Select browser based on environment variable
    if browser_name == 'firefox':
        browser = playwright_instance.firefox.launch(headless=headless)
    elif browser_name == 'webkit':
        browser = playwright_instance.webkit.launch(headless=headless)
    else:  # Default to chromium for 'chrome' or anything else
        browser = playwright_instance.chromium.launch(headless=headless)
    
    yield browser
    browser.close()


@pytest.fixture(scope="function")
def context(browser, browser_config):
    """Create a new browser context for each test."""
    context = browser.new_context(
        viewport={
            'width': browser_config['screen_width'],
            'height': browser_config['screen_height']
        },
        base_url=browser_config['base_url']
    )
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context):
    """Create a new page for each test."""
    page = context.new_page()
    yield page
    page.close()


@pytest.fixture(scope="session")
def base_url(browser_config):
    """Provide the base URL for tests."""
    return browser_config['base_url']
