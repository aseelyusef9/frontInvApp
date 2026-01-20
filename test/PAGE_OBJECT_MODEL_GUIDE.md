# Page Object Model (POM) Implementation Guide

## Overview

This project now uses the **Page Object Model (POM)** pattern for end-to-end testing. The POM provides a clean separation between test logic and page structure, making tests more maintainable and readable.

## Key Principles

### 1. Page Objects as Interfaces
Each page object class represents a specific page in the application and provides an interface to interact with it from an end-user's perspective.

```python
# Example: LoginPage represents the login page
login_page = LoginPage(page, base_url)
```

### 2. Methods Return Page Objects
Methods that cause navigation return the new page object, modeling the user's journey through the application.

```python
# login_as_valid_user returns DashboardPage
dashboard_page = login_page.login_as_valid_user("admin", "admin")

# navigate_to_upload returns UploadPage
upload_page = dashboard_page.navigate_to_upload()
```

### 3. No Assertions in Page Objects
Page objects never contain assertions. All assertions belong in the test code.

```python
# ❌ Wrong - assertion in page object
class LoginPage:
    def login(self, username, password):
        self.page.fill(...)
        assert "dashboard" in self.page.url  # DON'T DO THIS

# ✅ Correct - assertion in test
def test_login(self):
    login_page = LoginPage(self.page, self.base_url)
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    self.assertTrue(dashboard_page.is_heading_visible())  # Assertion in test
```

### 4. Verify Page Loaded
Each page object should verify that the page loaded correctly in its constructor or navigation method.

```python
class DashboardPage(BasePage):
    def verify_page_loaded(self):
        """Verify that the dashboard page is loaded correctly."""
        self.page.wait_for_url("**/dashboard", timeout=5000)
        assert "dashboard" in self.page.url.lower()
```

### 5. Component Composition
For pages rich in components, create separate component objects that can be reused across pages.

```python
class NavigationComponent:
    """Component representing the navigation bar."""
    
    def navigate_to_upload(self):
        self.page.locator(self.UPLOAD_LINK).first.click()
        return UploadPage(self.page, self.base_url)

class DashboardPage(BasePage):
    def __init__(self, page, base_url):
        super().__init__(page, base_url)
        self.navigation = NavigationComponent(page, base_url)  # Composition
```

## File Structure

```
test/
├── page_objects.py          # All page object classes
├── teste2e.py              # Test cases using page objects
└── fixtures/
    └── sample.pdf
```

## Page Object Classes

### BasePage
The base class for all page objects with common functionality:
- `verify_page_loaded()` - Override in subclasses
- `clear_storage()` - Clear browser storage

### LoginPage
Represents the login page:
- `navigate()` - Navigate to login page
- `login_as_valid_user(username, password)` - Login and return DashboardPage
- `login_with_invalid_credentials(username, password)` - Attempt invalid login
- `is_error_message_visible()` - Check for error messages

### DashboardPage
Represents the dashboard page:
- `is_heading_visible()` - Check if dashboard heading is visible
- `navigate_to_upload()` - Navigate to upload page
- `navigate_to_invoices()` - Navigate to invoices page

### UploadPage
Represents the upload invoice page:
- `is_heading_visible()` - Check if upload heading is visible
- `select_file(file_path)` - Select a file for upload
- `upload_invoice(file_path)` - Upload file and return InvoicePage or self
- `navigate_to_invoices()` - Navigate to invoices page
- `navigate_to_dashboard()` - Navigate to dashboard page

### InvoicePage
Represents the invoice detail page:
- `navigate_to_invoices()` - Navigate to invoices list
- `navigate_to_dashboard()` - Navigate to dashboard

### InvoicesPage
Represents the invoices list page:
- `navigate_to_dashboard()` - Navigate to dashboard
- `navigate_to_upload()` - Navigate to upload page

### NavigationComponent
Represents the navigation bar (used as a component in multiple pages):
- `navigate_to_upload()` - Navigate to upload page
- `navigate_to_invoices()` - Navigate to invoices page
- `navigate_to_dashboard()` - Navigate to dashboard page

## Example Test Flow

Here's how the Page Object Model represents a complete user journey:

```python
def test_complete_user_journey(self):
    """Test complete user journey: login -> upload -> view invoice."""
    
    # Step 1: Navigate to login page
    login_page = LoginPage(self.page, self.base_url).navigate()
    
    # Verify login page elements
    self.assertTrue(login_page.is_username_input_visible())
    
    # Step 2: Login (returns DashboardPage)
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    
    # Verify dashboard loaded
    self.assertTrue(dashboard_page.is_heading_visible())
    
    # Step 3: Navigate to upload (returns UploadPage)
    upload_page = dashboard_page.navigate_to_upload()
    
    # Verify upload page loaded
    self.assertTrue(upload_page.is_heading_visible())
    
    # Step 4: Upload invoice (returns InvoicePage or UploadPage)
    result_page = upload_page.upload_invoice(self.sample_invoice_path)
    
    # Check result
    if isinstance(result_page, InvoicePage):
        print("[OK] Successfully navigated to invoice page")
    
    # Step 5: Navigate to invoices list (returns InvoicesPage)
    invoices_page = upload_page.navigate_to_invoices()
    
    # Step 6: Navigate back to dashboard (returns DashboardPage)
    dashboard_page = invoices_page.navigate_to_dashboard()
```

## Benefits of This Approach

### 1. Maintainability
When the UI changes, you only need to update the page object, not all the tests:

```python
# If the login button selector changes, update only LoginPage
class LoginPage:
    SUBMIT_BUTTON = 'button[type="submit"]'  # Change only here
```

### 2. Readability
Tests read like user stories:

```python
# Clear, high-level test logic
login_page = LoginPage(page, base_url).navigate()
dashboard_page = login_page.login_as_valid_user("admin", "admin")
upload_page = dashboard_page.navigate_to_upload()
```

### 3. Reusability
Page object methods can be reused across multiple tests:

```python
def test_login(self):
    login_page = LoginPage(self.page, self.base_url).navigate()
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    # Reusable login flow

def test_another_feature(self):
    login_page = LoginPage(self.page, self.base_url).navigate()
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    # Same reusable login flow
```

### 4. Encapsulation
Page structure details are hidden from tests:

```python
# Tests don't need to know about selectors
dashboard_page = login_page.login_as_valid_user("admin", "admin")

# Instead of tests having:
# self.page.locator('input[id="username"]').fill("admin")
# self.page.locator('input[id="password"]').fill("admin")
# self.page.locator('button[type="submit"]').click()
```

## Running the Tests

```bash
# Run all tests
python -m unittest test.teste2e

# Run specific test
python -m unittest test.teste2e.TestUserJourney.test_complete_user_journey

# Run with UI visible (headed mode)
SHOW_UI=1 python -m unittest test.teste2e

# Run from test directory
cd test
python teste2e.py
```

## Adding New Pages

To add a new page object:

1. **Create the page class** in `page_objects.py`:
```python
class NewPage(BasePage):
    """Page object for the new page."""
    
    # Define locators
    SOME_BUTTON = 'button[id="some-button"]'
    
    def __init__(self, page: Page, base_url: str):
        super().__init__(page, base_url)
        self.url = f"{base_url}/new-page"
        self.navigation = NavigationComponent(page, base_url)
        self.verify_page_loaded()
    
    def verify_page_loaded(self):
        """Verify that the page is loaded correctly."""
        self.page.wait_for_url("**/new-page", timeout=5000)
        assert "new-page" in self.page.url.lower()
    
    def perform_action(self):
        """Perform some action and return next page."""
        self.page.locator(self.SOME_BUTTON).click()
        return NextPage(self.page, self.base_url)
```

2. **Update navigation** to return new page:
```python
class SomePage(BasePage):
    def navigate_to_new_page(self):
        """Navigate to the new page."""
        self.page.locator('a[href="/new-page"]').click()
        return NewPage(self.page, self.base_url)
```

3. **Use in tests**:
```python
def test_new_feature(self):
    # Navigate through pages
    login_page = LoginPage(self.page, self.base_url).navigate()
    some_page = login_page.login_as_valid_user("admin", "admin")
    new_page = some_page.navigate_to_new_page()
    
    # Perform action on new page
    next_page = new_page.perform_action()
    
    # Make assertions
    self.assertTrue(next_page.is_loaded())
```

## Best Practices

1. **Keep page objects focused** - Each page object should represent one page
2. **Use descriptive method names** - `login_as_valid_user()` not `login()`
3. **Return page objects** - Methods should return the resulting page
4. **No test logic in page objects** - Keep them as interfaces only
5. **Verify page loaded** - Always verify the page loaded correctly
6. **Use composition for components** - Reuse common components like navigation
7. **Keep selectors in page objects** - Don't expose selectors to tests

## Troubleshooting

### Page Not Loading
If `verify_page_loaded()` fails, check:
- Is the URL correct?
- Is the timeout sufficient?
- Is the application running?

### Element Not Found
If an element locator fails, check:
- Is the selector correct in the page object?
- Has the UI changed?
- Update the selector in the page object only

### Test Flakiness
If tests are flaky:
- Add proper waits in page objects
- Use `wait_for_url()` for navigation
- Use `is_visible(timeout=...)` for elements
- Don't rely on fixed `time.sleep()` calls
