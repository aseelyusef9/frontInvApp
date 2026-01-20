# Complete Example: Before and After POM Refactoring

## The Same Test: Side-by-Side Comparison

### BEFORE: Without Page Object Model

```python
"""
Direct Playwright calls mixed with test logic.
Hard to read, hard to maintain, hard to reuse.
"""

def test_complete_user_journey(self):
    # Navigate to login
    self.page.goto(f"{self.base_url}/login")
    self.assertIn("login", self.page.url.lower())

    # Find form elements
    username_input = self.page.locator('input[id="username"]')
    password_input = self.page.locator('input[id="password"]')
    submit_button = self.page.locator('button[type="submit"]')

    # Verify elements visible
    self.assertTrue(username_input.is_visible(), "Username input should be visible")
    self.assertTrue(password_input.is_visible(), "Password input should be visible")
    self.assertTrue(submit_button.is_visible(), "Submit button should be visible")

    # Fill form and submit
    username_input.fill("admin")
    password_input.fill("admin")
    submit_button.click()

    # Wait for navigation
    self.page.wait_for_url("**/dashboard", timeout=5000)
    self.assertIn("dashboard", self.page.url.lower())

    # Verify dashboard
    dashboard_heading = self.page.locator("h1:has-text('Dashboard')")
    self.assertTrue(dashboard_heading.is_visible(timeout=3000), 
                   "Dashboard heading should be visible after login")

    # Navigate to upload
    upload_link = self.page.locator('nav a[href="/upload"]').first
    self.assertTrue(upload_link.is_visible(), "Upload link should be visible in navbar")
    upload_link.click()
    self.page.wait_for_url("**/upload", timeout=5000)
    self.assertIn("upload", self.page.url.lower())

    # Verify upload page
    upload_heading = self.page.locator("h1:has-text('Upload Invoice')")
    self.assertTrue(upload_heading.is_visible(timeout=3000), 
                   "Upload Invoice heading should be visible")

    # Check for file input
    if not os.path.exists(self.sample_invoice_path):
        self.skipTest(f"Sample invoice file not found at {self.sample_invoice_path}")

    file_input = self.page.locator('input[type="file"]')
    self.assertTrue(file_input.count() > 0, "File input should exist")
    file_input.set_input_files(self.sample_invoice_path)

    # Check if filename displayed
    file_name_display = self.page.locator("text=/invoice.*\\.pdf/i")
    try:
        self.assertTrue(file_name_display.is_visible(timeout=3000), 
                       "File name should be displayed after selection")
    except PlaywrightTimeoutError:
        pass

    # Upload file
    upload_button = self.page.locator('button:has-text("Upload & Extract")')
    self.assertTrue(upload_button.is_visible(), "Upload button should be visible")
    upload_button.click()

    # Check for success
    try:
        success_message = self.page.locator('text=/successfully/i')
        if success_message.is_visible(timeout=120000):
            self.assertTrue(True, "Upload completed successfully")
    except PlaywrightTimeoutError:
        try:
            self.page.wait_for_url("**/invoice/**", timeout=120000)
            self.assertIn("invoice", self.page.url.lower())
            print("[OK] Redirected to invoice detail page after upload")
        except PlaywrightTimeoutError:
            error_message = self.page.locator('text=/error|unavailable|failed/i')
            if error_message.is_visible(timeout=2000):
                print("[WARN] Upload failed (likely backend not configured)")
            else:
                print("[WARN] Upload process completed (check manually)")

    # Navigate to invoices
    invoices_link = self.page.locator('nav a[href="/invoices"]').first
    if invoices_link.is_visible():
        invoices_link.click()
        self.page.wait_for_url("**/invoices", timeout=5000)
        self.assertIn("invoices", self.page.url.lower())
        print("[OK] Navigation to invoices page works")

    # Navigate back to dashboard
    dashboard_link = self.page.locator('nav a[href="/dashboard"]').first
    if dashboard_link.is_visible():
        dashboard_link.click()
        self.page.wait_for_url("**/dashboard", timeout=5000)
        self.assertIn("dashboard", self.page.url.lower())
        print("[OK] Navigation back to dashboard works")
```

**Issues with this approach:**
- ❌ 80+ lines of code
- ❌ Selectors mixed with test logic
- ❌ Hard to read and understand flow
- ❌ Not reusable across tests
- ❌ When UI changes, must update every test
- ❌ Difficult to maintain
- ❌ Test intent is buried in implementation details

---

### AFTER: With Page Object Model

```python
"""
Clean, readable test using page objects.
Easy to read, easy to maintain, highly reusable.
"""

def test_complete_user_journey(self):
    """Test complete user journey: login → upload → view invoice."""
    
    # Step 1: Navigate to login page
    login_page = LoginPage(self.page, self.base_url).navigate()
    
    # Verify login page elements are visible
    self.assertTrue(login_page.is_username_input_visible(), 
                   "Username input should be visible")
    self.assertTrue(login_page.is_password_input_visible(), 
                   "Password input should be visible")
    self.assertTrue(login_page.is_submit_button_visible(), 
                   "Submit button should be visible")
    
    # Step 2: Login with valid credentials
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    
    # Verify dashboard page loaded correctly
    self.assertTrue(dashboard_page.is_heading_visible(), 
                   "Dashboard heading should be visible after login")
    
    # Step 3: Navigate to upload page
    upload_page = dashboard_page.navigate_to_upload()
    
    # Verify upload page loaded correctly
    self.assertTrue(upload_page.is_heading_visible(), 
                   "Upload Invoice heading should be visible")
    
    # Step 4: Upload invoice file
    if not os.path.exists(self.sample_invoice_path):
        self.skipTest(f"Sample invoice file not found at {self.sample_invoice_path}")
    
    self.assertTrue(upload_page.is_file_input_present(), 
                   "File input should exist")
    self.assertTrue(upload_page.is_upload_button_visible(), 
                   "Upload button should be visible")
    
    # Perform the upload
    result_page = upload_page.upload_invoice(self.sample_invoice_path)
    
    # Check upload outcome
    if isinstance(result_page, InvoicePage):
        print("[OK] Successfully redirected to invoice detail page after upload")
    else:
        if upload_page.is_success_message_visible():
            print("[OK] Upload completed successfully")
        elif upload_page.is_error_message_visible():
            print("[WARN] Upload failed (likely backend not configured)")
        else:
            print("[WARN] Upload process completed (check manually)")
    
    # Step 5: Test navigation between pages
    if upload_page.navigation.is_invoices_link_visible():
        invoices_page = upload_page.navigate_to_invoices()
        print("[OK] Navigation to invoices page works")
        
        dashboard_page = invoices_page.navigate_to_dashboard()
        print("[OK] Navigation back to dashboard works")
```

**Benefits of this approach:**
- ✅ 55 lines (30% less code)
- ✅ Clear separation of concerns
- ✅ Readable user journey
- ✅ Reusable page objects
- ✅ UI changes only affect page objects
- ✅ Easy to maintain
- ✅ Test intent is clear

---

## Line-by-Line Transformation Examples

### Example 1: Login Flow

**BEFORE (8 lines)**
```python
username_input = self.page.locator('input[id="username"]')
password_input = self.page.locator('input[id="password"]')
submit_button = self.page.locator('button[type="submit"]')
username_input.fill("admin")
password_input.fill("admin")
submit_button.click()
self.page.wait_for_url("**/dashboard", timeout=5000)
self.assertIn("dashboard", self.page.url.lower())
```

**AFTER (1 line + assertion)**
```python
dashboard_page = login_page.login_as_valid_user("admin", "admin")
self.assertTrue(dashboard_page.is_heading_visible())
```

---

### Example 2: Navigation

**BEFORE (5 lines)**
```python
upload_link = self.page.locator('nav a[href="/upload"]').first
self.assertTrue(upload_link.is_visible(), "Upload link should be visible")
upload_link.click()
self.page.wait_for_url("**/upload", timeout=5000)
self.assertIn("upload", self.page.url.lower())
```

**AFTER (1 line)**
```python
upload_page = dashboard_page.navigate_to_upload()
```

---

### Example 3: File Upload

**BEFORE (20+ lines)**
```python
if not os.path.exists(self.sample_invoice_path):
    self.skipTest(f"Sample invoice file not found")

file_input = self.page.locator('input[type="file"]')
self.assertTrue(file_input.count() > 0, "File input should exist")
file_input.set_input_files(self.sample_invoice_path)

file_name_display = self.page.locator("text=/invoice.*\\.pdf/i")
try:
    self.assertTrue(file_name_display.is_visible(timeout=3000))
except PlaywrightTimeoutError:
    pass

upload_button = self.page.locator('button:has-text("Upload & Extract")')
self.assertTrue(upload_button.is_visible())
upload_button.click()

try:
    success_message = self.page.locator('text=/successfully/i')
    if success_message.is_visible(timeout=120000):
        # Success
        pass
except PlaywrightTimeoutError:
    # Handle error...
    pass
```

**AFTER (4 lines)**
```python
if not os.path.exists(self.sample_invoice_path):
    self.skipTest(f"Sample invoice file not found")

result_page = upload_page.upload_invoice(self.sample_invoice_path)
```

---

## What Moved Where

### Test Responsibilities (teste2e.py)
```python
✓ Test scenarios and flow
✓ Assertions
✓ Test data
✓ Test setup/teardown
✗ No selectors
✗ No element interactions
✗ No page structure knowledge
```

### Page Object Responsibilities (page_objects.py)
```python
✓ Page structure (selectors)
✓ Element interactions
✓ Navigation between pages
✓ Page verification
✗ No assertions
✗ No test logic
✗ No test data
```

---

## Impact on Maintainability

### Scenario: Login button selector changes

**BEFORE: Must change in every test**
```python
# test_complete_user_journey
submit_button = self.page.locator('button[type="submit"]')  # Change here

# test_login_with_invalid_credentials  
self.page.click('button[type="submit"]')  # AND here

# test_another_feature
self.page.locator('button[type="submit"]').click()  # AND here

# ... in EVERY test that uses login
```

**AFTER: Change in ONE place**
```python
# In page_objects.py - LoginPage class
class LoginPage(BasePage):
    SUBMIT_BUTTON = 'button[type="submit"]'  # Change ONLY here
    
# All tests automatically use the new selector!
```

---

## Readability Comparison

### BEFORE: What is this test doing?
```python
def test_complete_user_journey(self):
    self.page.goto(f"{self.base_url}/login")
    username_input = self.page.locator('input[id="username"]')
    password_input = self.page.locator('input[id="password"]')
    username_input.fill("admin")
    password_input.fill("admin")
    self.page.locator('button[type="submit"]').click()
    self.page.wait_for_url("**/dashboard", timeout=5000)
    upload_link = self.page.locator('nav a[href="/upload"]').first
    upload_link.click()
    # ... what's the user journey here? Hard to tell!
```

### AFTER: Crystal clear user journey!
```python
def test_complete_user_journey(self):
    """Test: Login → Upload → View Invoice"""
    login_page = LoginPage(self.page, self.base_url).navigate()
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    upload_page = dashboard_page.navigate_to_upload()
    result_page = upload_page.upload_invoice(file_path)
    # User journey is immediately clear!
```

---

## Code Reuse Comparison

### BEFORE: Can't reuse login flow
```python
# test_feature_a
def test_feature_a(self):
    self.page.goto(f"{self.base_url}/login")
    self.page.locator('input[id="username"]').fill("admin")
    self.page.locator('input[id="password"]').fill("admin")
    self.page.locator('button[type="submit"]').click()
    # ... test feature A

# test_feature_b
def test_feature_b(self):
    self.page.goto(f"{self.base_url}/login")
    self.page.locator('input[id="username"]').fill("admin")  # Duplicate!
    self.page.locator('input[id="password"]').fill("admin")  # Duplicate!
    self.page.locator('button[type="submit"]').click()       # Duplicate!
    # ... test feature B
```

### AFTER: Easy reuse everywhere
```python
# test_feature_a
def test_feature_a(self):
    dashboard_page = LoginPage(self.page, self.base_url).navigate() \
                     .login_as_valid_user("admin", "admin")
    # ... test feature A

# test_feature_b
def test_feature_b(self):
    dashboard_page = LoginPage(self.page, self.base_url).navigate() \
                     .login_as_valid_user("admin", "admin")
    # ... test feature B
```

---

## Summary: Why This Matters

| Metric | Before POM | After POM | Improvement |
|--------|-----------|-----------|-------------|
| **Lines of code** | 100+ | 70 | -30% |
| **Readability** | Poor | Excellent | +++++ |
| **Maintainability** | Low | High | +++++ |
| **Reusability** | None | High | +++++ |
| **Test clarity** | Hidden | Clear | +++++ |
| **Change impact** | All tests | 1 file | +++++ |

**The Page Object Model transforms your tests from brittle, hard-to-maintain code into clean, readable, reusable specifications of user behavior.**
