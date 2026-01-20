# Page Object Model - Quick Reference Card

## Core Concepts (5 Principles)

```
1. Page Objects as Interfaces     → Represent services pages provide
2. Methods Return Page Objects     → Model user journey through app
3. No Assertions in Page Objects   → Assertions belong in tests only
4. Verify Page Loaded             → Each page verifies it loaded correctly
5. Component Composition          → Reuse components across pages
```

## Quick Syntax Guide

### Creating a Page Object
```python
from page_objects import LoginPage

login_page = LoginPage(self.page, self.base_url)
```

### Navigation Pattern
```python
# Method that navigates returns new page object
login_page = LoginPage(self.page, self.base_url).navigate()
dashboard_page = login_page.login_as_valid_user("admin", "admin")
upload_page = dashboard_page.navigate_to_upload()
```

### Query Pattern
```python
# Methods that check state return boolean
if login_page.is_username_input_visible():
    # Element is visible
    pass
```

### Action Pattern
```python
# Actions that don't navigate return self or None
upload_page.select_file(file_path)  # Returns None
login_page = login_page.login_with_invalid_credentials(...)  # Returns self
```

## Available Page Objects

| Page Object | Purpose | Key Methods |
|-------------|---------|-------------|
| `LoginPage` | Login page | `login_as_valid_user()`, `login_with_invalid_credentials()` |
| `DashboardPage` | Dashboard | `navigate_to_upload()`, `navigate_to_invoices()` |
| `UploadPage` | Upload invoices | `upload_invoice()`, `select_file()` |
| `InvoicePage` | Invoice details | `navigate_to_invoices()`, `navigate_to_dashboard()` |
| `InvoicesPage` | Invoice list | `navigate_to_dashboard()`, `navigate_to_upload()` |
| `NavigationComponent` | Nav bar | `navigate_to_*()` methods |

## Common Patterns

### Standard Test Flow
```python
def test_feature(self):
    # 1. Navigate to starting page
    login_page = LoginPage(self.page, self.base_url).navigate()
    
    # 2. Perform actions (returns new page objects)
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    upload_page = dashboard_page.navigate_to_upload()
    
    # 3. Make assertions (in test, not page object!)
    self.assertTrue(upload_page.is_heading_visible())
```

### Login Flow (Reusable)
```python
# Start any test with this pattern
login_page = LoginPage(self.page, self.base_url).navigate()
dashboard_page = login_page.login_as_valid_user("admin", "admin")
# Now on dashboard, ready for your test
```

### Upload Flow
```python
upload_page = dashboard_page.navigate_to_upload()
result_page = upload_page.upload_invoice(self.sample_invoice_path)

# Check result type
if isinstance(result_page, InvoicePage):
    # Success - on invoice page
    pass
else:
    # Still on upload page - check for messages
    if upload_page.is_error_message_visible():
        # Error occurred
        pass
```

## Dos and Don'ts

### ✅ DO

```python
# ✅ Use page objects for all interactions
dashboard_page = login_page.login_as_valid_user("admin", "admin")

# ✅ Make assertions in tests
self.assertTrue(dashboard_page.is_heading_visible())

# ✅ Chain page transitions
page1 = PageA(page, url).navigate()
page2 = page1.go_to_b()
page3 = page2.go_to_c()

# ✅ Return page objects from navigation methods
def login_as_valid_user(self, username, password):
    # ... perform login ...
    return DashboardPage(self.page, self.base_url)
```

### ❌ DON'T

```python
# ❌ Don't make assertions in page objects
class LoginPage:
    def login(self):
        self.page.click(...)
        assert "dashboard" in self.page.url  # WRONG!

# ❌ Don't expose page internals to tests
def test_login(self):
    login_page = LoginPage(...)
    login_page.page.locator('input[id="username"]')...  # WRONG!

# ❌ Don't use direct Playwright calls in tests
def test_login(self):
    self.page.goto(...)  # WRONG! Use page objects
    self.page.locator(...)  # WRONG! Use page objects
```

## Adding New Pages (Template)

```python
class NewPage(BasePage):
    """Page object for [page description]."""
    
    # Locators (constants)
    SOME_BUTTON = 'button[id="some-button"]'
    SOME_INPUT = 'input[name="some-input"]'
    
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.url = f"{base_url}/new-page"
        self.navigation = NavigationComponent(page, base_url)
        self.verify_page_loaded()
    
    def verify_page_loaded(self):
        """Verify page loaded correctly."""
        self.page.wait_for_url("**/new-page", timeout=5000)
        assert "new-page" in self.page.url.lower()
    
    def is_element_visible(self):
        """Query method - returns boolean."""
        return self.page.locator(self.SOME_BUTTON).is_visible()
    
    def perform_action(self):
        """Action method - returns next page."""
        self.page.locator(self.SOME_BUTTON).click()
        return NextPage(self.page, self.base_url)
```

## Test Template

```python
def test_my_feature(self):
    """Test [feature description]."""
    
    # Step 1: Navigate to starting point
    login_page = LoginPage(self.page, self.base_url).navigate()
    
    # Step 2: Login
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    
    # Step 3: Navigate to feature page
    feature_page = dashboard_page.navigate_to_feature()
    
    # Step 4: Perform actions
    result_page = feature_page.perform_action()
    
    # Step 5: Make assertions
    self.assertTrue(result_page.is_success_visible())
    self.assertIn("success", self.page.url.lower())
```

## Running Tests

```bash
# All tests
python -m unittest test.teste2e

# Specific test
python -m unittest test.teste2e.TestUserJourney.test_complete_user_journey

# With visible browser
SHOW_UI=1 python -m unittest test.teste2e

# From test directory
cd test && python teste2e.py
```

## Debugging Tips

```python
# Take screenshot from page object
login_page.take_debug_screenshot('debug.png')

# Check current URL
print(f"Current URL: {self.page.url}")

# Verify page loaded (will raise assertion if not)
page_object.verify_page_loaded()

# Check if element exists
if upload_page.is_file_input_present():
    print("File input exists")
```

## File Structure

```
test/
├── page_objects.py              ← All page object classes
├── teste2e.py                   ← Your tests
├── PAGE_OBJECT_MODEL_GUIDE.md   ← Detailed guide
├── POM_ARCHITECTURE.md          ← Architecture diagrams
├── REFACTORING_SUMMARY.md       ← What changed
├── QUICK_REFERENCE.md           ← This file
└── fixtures/
    └── sample.pdf
```

## Method Naming Conventions

| Pattern | Returns | Example |
|---------|---------|---------|
| `navigate_to_*()` | Page Object | `navigate_to_upload()` |
| `is_*()` | Boolean | `is_heading_visible()` |
| `*_as_*()` | Page Object | `login_as_valid_user()` |
| `select_*()` | None | `select_file()` |
| `upload_*()` | Page Object | `upload_invoice()` |

## Component Reuse

```python
# Navigation component used across multiple pages
class DashboardPage(BasePage):
    def __init__(self, page, base_url):
        self.navigation = NavigationComponent(page, base_url)
    
    def navigate_to_upload(self):
        return self.navigation.navigate_to_upload()

class UploadPage(BasePage):
    def __init__(self, page, base_url):
        self.navigation = NavigationComponent(page, base_url)
    
    def navigate_to_dashboard(self):
        return self.navigation.navigate_to_dashboard()
```

## Need Help?

1. **For basic usage**: Read this quick reference
2. **For detailed guide**: See `PAGE_OBJECT_MODEL_GUIDE.md`
3. **For architecture**: See `POM_ARCHITECTURE.md`
4. **For what changed**: See `REFACTORING_SUMMARY.md`
5. **For examples**: Look at `teste2e.py` and `page_objects.py`
