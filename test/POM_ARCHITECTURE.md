# Page Object Model Architecture Diagram

## Class Hierarchy

```
BasePage (Abstract Base)
├── verify_page_loaded()
├── clear_storage()
│
├── LoginPage
│   ├── navigate()
│   ├── login_as_valid_user() → DashboardPage
│   ├── login_with_invalid_credentials() → LoginPage
│   └── is_error_message_visible()
│
├── DashboardPage
│   ├── is_heading_visible()
│   ├── navigate_to_upload() → UploadPage
│   ├── navigate_to_invoices() → InvoicesPage
│   └── navigation: NavigationComponent
│
├── UploadPage
│   ├── is_heading_visible()
│   ├── select_file()
│   ├── upload_invoice() → InvoicePage | UploadPage
│   ├── navigate_to_invoices() → InvoicesPage
│   ├── navigate_to_dashboard() → DashboardPage
│   └── navigation: NavigationComponent
│
├── InvoicePage
│   ├── navigate_to_invoices() → InvoicesPage
│   ├── navigate_to_dashboard() → DashboardPage
│   └── navigation: NavigationComponent
│
└── InvoicesPage
    ├── navigate_to_dashboard() → DashboardPage
    ├── navigate_to_upload() → UploadPage
    └── navigation: NavigationComponent

NavigationComponent (Reusable Component)
├── navigate_to_upload() → UploadPage
├── navigate_to_invoices() → InvoicesPage
└── navigate_to_dashboard() → DashboardPage
```

## User Journey Flow

```
Test Start
    ↓
┌─────────────────────────────────────────────────────────────┐
│  test_complete_user_journey()                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. LoginPage.navigate()                                    │
│     └─ Verify: page loaded, elements visible               │
│                                                             │
│  2. LoginPage.login_as_valid_user("admin", "admin")        │
│     └─ Returns: DashboardPage                              │
│                                                             │
│  3. DashboardPage.navigate_to_upload()                     │
│     └─ Returns: UploadPage                                 │
│                                                             │
│  4. UploadPage.upload_invoice(file_path)                   │
│     └─ Returns: InvoicePage (success) or UploadPage (fail) │
│                                                             │
│  5. UploadPage.navigate_to_invoices()                      │
│     └─ Returns: InvoicesPage                               │
│                                                             │
│  6. InvoicesPage.navigate_to_dashboard()                   │
│     └─ Returns: DashboardPage                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
    ↓
Test End
```

## Page Transition Map

```
             ┌──────────────┐
             │  LoginPage   │
             │   (Entry)    │
             └──────┬───────┘
                    │ login_as_valid_user()
                    ↓
             ┌──────────────┐
        ┌───→│ DashboardPage│←───┐
        │    └──────┬───────┘    │
        │           │             │
        │           │ navigate_to_upload()
        │           ↓             │
        │    ┌──────────────┐    │
        │    │  UploadPage  │────┘ navigate_to_dashboard()
        │    └──────┬───────┘
        │           │
        │           │ upload_invoice()
        │           ↓
        │    ┌──────────────┐
        │    │ InvoicePage  │
        │    └──────┬───────┘
        │           │
        │           │ navigate_to_invoices()
        │           ↓
        │    ┌──────────────┐
        └────│ InvoicesPage │
             └──────────────┘
```

## Component Composition

```
┌─────────────────────────────────────────────┐
│          DashboardPage                      │
├─────────────────────────────────────────────┤
│  Properties:                                │
│  - page: Page                               │
│  - base_url: str                            │
│  - navigation: NavigationComponent ◄────┐   │
│                                         │   │
│  Methods:                               │   │
│  - is_heading_visible()                 │   │
│  - navigate_to_upload() ────────────────┘   │
│  - navigate_to_invoices() ──────────────┐   │
└─────────────────────────────────────────│───┘
                                          │
                    ┌─────────────────────┘
                    ↓
        ┌──────────────────────────────┐
        │   NavigationComponent        │
        ├──────────────────────────────┤
        │  Locators:                   │
        │  - DASHBOARD_LINK            │
        │  - UPLOAD_LINK               │
        │  - INVOICES_LINK             │
        │                              │
        │  Methods:                    │
        │  - navigate_to_upload()      │
        │  - navigate_to_invoices()    │
        │  - navigate_to_dashboard()   │
        └──────────────────────────────┘
             ▲           ▲          ▲
             │           │          │
    Used by: │           │          │
         UploadPage  InvoicePage  InvoicesPage
```

## Separation of Concerns

```
┌────────────────────────────────────────────────────────────┐
│                    TEST LAYER                              │
│  (test_complete_user_journey, test_login, etc.)            │
│                                                            │
│  Responsibilities:                                         │
│  - Define test scenarios                                   │
│  - Make assertions                                         │
│  - Orchestrate page interactions                           │
├────────────────────────────────────────────────────────────┤
│  ✓ Contains: Assertions, test logic, validation           │
│  ✗ Does NOT contain: Selectors, page structure            │
└────────────────────────────────────────────────────────────┘
                          ↕ (uses)
┌────────────────────────────────────────────────────────────┐
│                 PAGE OBJECT LAYER                          │
│  (LoginPage, DashboardPage, UploadPage, etc.)              │
│                                                            │
│  Responsibilities:                                         │
│  - Encapsulate page structure                              │
│  - Provide user-facing methods                             │
│  - Handle element interactions                             │
│  - Return other page objects                               │
├────────────────────────────────────────────────────────────┤
│  ✓ Contains: Selectors, element interactions, navigation   │
│  ✗ Does NOT contain: Assertions, test logic               │
└────────────────────────────────────────────────────────────┘
                          ↕ (uses)
┌────────────────────────────────────────────────────────────┐
│                   PLAYWRIGHT LAYER                         │
│  (Page, Locator, Browser, etc.)                            │
│                                                            │
│  Responsibilities:                                         │
│  - Browser automation                                      │
│  - Element location and interaction                        │
│  - Navigation and waiting                                  │
└────────────────────────────────────────────────────────────┘
```

## Method Return Pattern

```
Page Object Method Pattern:

┌──────────────────────────────┐
│  Action causes navigation?   │
└──────────┬───────────────────┘
           │
     ┌─────┴─────┐
     │           │
    YES          NO
     │           │
     ↓           ↓
Return Next   Return
Page Object   Self/Data
     │           │
     ↓           ↓
┌────────────┐ ┌──────────────┐
│dashboard = │ │is_visible =  │
│login_page. │ │login_page.   │
│login_as_   │ │is_username_  │
│valid_user()│ │input_visible│
└────────────┘ └──────────────┘

Examples:

Navigation Methods (return new page):
├── login_as_valid_user() → DashboardPage
├── navigate_to_upload() → UploadPage
├── navigate_to_invoices() → InvoicesPage
└── upload_invoice() → InvoicePage

Query Methods (return data/boolean):
├── is_heading_visible() → bool
├── is_username_input_visible() → bool
├── is_error_message_visible() → bool
└── is_file_input_present() → bool

Action Methods (return self):
├── login_with_invalid_credentials() → LoginPage
└── select_file() → None
```

## Before and After Comparison

### BEFORE (Direct Playwright calls in tests):
```python
def test_login(self):
    self.page.goto(f"{self.base_url}/login")
    self.page.locator('input[id="username"]').fill("admin")
    self.page.locator('input[id="password"]').fill("admin")
    self.page.locator('button[type="submit"]').click()
    self.page.wait_for_url("**/dashboard", timeout=5000)
    
    # If selector changes, EVERY test needs updating!
```

### AFTER (Page Object Model):
```python
def test_login(self):
    login_page = LoginPage(self.page, self.base_url).navigate()
    dashboard_page = login_page.login_as_valid_user("admin", "admin")
    
    # If selector changes, only LoginPage needs updating!
```

## Data Flow

```
Test Creates Page Object
        ↓
┌──────────────────────┐
│ LoginPage.__init__() │
├──────────────────────┤
│ - Stores page ref    │
│ - Stores base_url    │
│ - Defines locators   │
└──────────────────────┘
        ↓
Test Calls Method
        ↓
┌─────────────────────────────┐
│ login_as_valid_user()       │
├─────────────────────────────┤
│ 1. Locate username input    │
│ 2. Fill username            │
│ 3. Locate password input    │
│ 4. Fill password            │
│ 5. Click submit button      │
│ 6. Create DashboardPage     │
│ 7. Return DashboardPage     │
└─────────────────────────────┘
        ↓
Test Receives New Page Object
        ↓
┌──────────────────────────┐
│ DashboardPage.__init__() │
├──────────────────────────┤
│ - Verifies page loaded   │
│ - Creates navigation     │
│ - Ready for next action  │
└──────────────────────────┘
```
