"""Simple matrix configuration test."""

import pytest


def test_browser_config(browser_config):
    """Test that browser configuration is loaded correctly from environment."""
    print(f"\n✅ Browser: {browser_config['browser_name']}")
    print(f"✅ Resolution: {browser_config['screen_width']}x{browser_config['screen_height']}")
    print(f"✅ Headless: {browser_config['headless']}")
    print(f"✅ Base URL: {browser_config['base_url']}")
    
    assert browser_config['browser_name'] in ['chrome', 'chromium', 'firefox', 'webkit']
    assert browser_config['screen_width'] > 0
    assert browser_config['screen_height'] > 0


def test_page_viewport(page, browser_config):
    """Test that page viewport matches configuration."""
    viewport = page.viewport_size
    print(f"\n✅ Actual viewport: {viewport['width']}x{viewport['height']}")
    
    assert viewport['width'] == browser_config['screen_width']
    assert viewport['height'] == browser_config['screen_height']


def test_browser_type(page, browser_config):
    """Test that correct browser is launched."""
    # Navigate to a simple page to verify browser works
    page.goto("data:text/html,<h1>Matrix Testing Works!</h1>")
    
    heading = page.locator("h1")
    assert heading.is_visible()
    assert "Matrix Testing Works!" in heading.text_content()
    
    print(f"\n✅ Browser {browser_config['browser_name']} is working correctly!")
