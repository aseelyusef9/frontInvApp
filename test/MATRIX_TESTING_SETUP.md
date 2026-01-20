# Matrix Testing Setup - Quick Reference

## ✅ Changes Made

### 1. Created `conftest.py`
- Pytest fixtures for browser, context, and page management
- Automatic browser selection (Chrome/Firefox) via `BROWSER` env var
- Automatic viewport configuration via `SCREEN_WIDTH` and `SCREEN_HEIGHT`
- Session-scoped browser, function-scoped page for test isolation

### 2. Updated `upload_page.py`
- ❌ Removed module-level browser instantiation (lines 7-12)
- ✅ Fixed import: `from .invoice_page import InvoicePage`
- Now properly uses Page Object pattern

### 3. Updated `BrowserFactory.py`
- Enhanced with proper typing and documentation
- Returns tuple of (browser, context, page)
- Better error handling and cleanup

### 4. Created `test_example_pytest.py`
- Example tests using new pytest fixtures
- Shows how to use `page` and `base_url` fixtures
- Includes responsive layout test

### 5. Fixed `ui-testing.yaml`
- Corrected test directory path

## 🚀 How to Run Tests

### Locally (single browser/resolution)
```bash
cd test
pytest test_example_pytest.py -v
```

### With specific browser
```bash
BROWSER=firefox pytest test_example_pytest.py -v
```

### With specific resolution
```bash
BROWSER=chrome SCREEN_WIDTH=768 SCREEN_HEIGHT=1024 pytest test_example_pytest.py -v
```

### Full headless mode
```bash
HEADLESS=true BROWSER=firefox pytest test_example_pytest.py -v
```

## 📊 CI/CD Matrix (GitHub Actions)

When pushed to GitHub, the workflow runs **6 parallel jobs**:
- Chrome × Desktop (1920×1080)
- Chrome × Tablet (768×1024)
- Chrome × Mobile (375×667)
- Firefox × Desktop (1920×1080)
- Firefox × Tablet (768×1024)
- Firefox × Mobile (375×667)

## 📝 Writing New Tests

```python
def test_my_feature(page, base_url):
    """Test description."""
    # Setup authentication
    page.goto(base_url)
    page.evaluate("() => localStorage.setItem('isAuthenticated', 'true')")
    
    # Use page objects
    upload_page = UploadPage(page, base_url)
    page.goto(f"{base_url}/upload")
    
    # Your test logic
    assert upload_page.is_heading_visible()
```

## 🔧 Environment Variables

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `BROWSER` | chrome, firefox, webkit | chrome | Browser to use |
| `SCREEN_WIDTH` | number | 1920 | Viewport width |
| `SCREEN_HEIGHT` | number | 1080 | Viewport height |
| `HEADLESS` | true, false | false | Run headless mode |
| `APP_URL` | URL | http://localhost:3000 | Application URL |

## 🎯 Key Benefits

✅ **No more manual browser instantiation** in page objects
✅ **Automatic multi-browser testing** via pytest fixtures
✅ **Parallel execution** in CI/CD (6 jobs simultaneously)
✅ **Test isolation** - each test gets fresh page
✅ **Responsive testing** - automatically tests 3 screen sizes
