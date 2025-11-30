# JavaScript Integration

NiceGUI allows integrating custom JavaScript for browser-side functionality that can't be handled server-side.

## Including External JS Files

### Static Files Setup

```python
from pathlib import Path
from nicegui import app, ui

# Serve static files (CSS, JS)
STATIC_DIR = Path(__file__).parent / 'static'
app.add_static_files('/static', STATIC_DIR)
```

### Including in Page Head

```python
def root():
    # Include custom JS and CSS
    ui.add_head_html('<script src="/static/js/app.js"></script>')
    ui.add_head_html('<link rel="stylesheet" href="/static/css/app.css">')
    
    # ... rest of page
```

## Running JavaScript from Python

### Basic Execution

```python
from nicegui import ui

# Run JavaScript immediately
ui.run_javascript('console.log("Hello from Python!")')

# Run JavaScript with return value
async def get_screen_width():
    width = await ui.run_javascript('window.innerWidth')
    ui.notify(f'Screen width: {width}px')

ui.button('Get Width', on_click=get_screen_width)
```

### Calling Functions Defined in External JS

```javascript
// static/js/app.js
function showAlert(message) {
    alert(message);
}

window.showAlert = showAlert;  // Export to global scope
```

```python
# Python
ui.run_javascript('showAlert("Hello!")')
```

## Browser History Manipulation

### Preventing Back Button Loops

When redirecting from a protected page to login, pressing back creates a loop. Use `history.replaceState` to fix:

```javascript
// static/js/login.js
function setupLoginBackHandler() {
    // Clean up any existing handler first
    cleanupLoginBackHandler();
    
    // Back button handler - redirect to home
    window._loginBackHandler = function(event) {
        cleanupLoginBackHandler();
        history.replaceState(null, "", "/");
        location.href = "/";
    };
    window.addEventListener('popstate', window._loginBackHandler);
    
    // Clean up when URL changes away from /login
    window._loginUrlChecker = setInterval(function() {
        if (location.pathname !== '/login') {
            cleanupLoginBackHandler();
        }
    }, 100);
}

function cleanupLoginBackHandler() {
    if (window._loginUrlChecker) {
        clearInterval(window._loginUrlChecker);
        delete window._loginUrlChecker;
    }
    if (window._loginBackHandler) {
        window.removeEventListener('popstate', window._loginBackHandler);
        delete window._loginBackHandler;
    }
}

// Export for use from Python
window.setupLoginBackHandler = setupLoginBackHandler;
window.cleanupLoginBackHandler = cleanupLoginBackHandler;
```

```python
# Python - call when building login page
if has_redirect:
    ui.run_javascript('setupLoginBackHandler()')
```

### Key Concepts

1. **Store handlers on `window`** - So they can be removed later
2. **Clean up on URL change** - Use `setInterval` to detect navigation
3. **Self-removing handlers** - Clean up immediately when triggered
4. **Export to `window`** - Functions must be on global scope to call from Python

## Event Listener Cleanup

**Critical**: Always clean up event listeners when navigating away, or they persist and break functionality.

### Pattern: URL Change Detection

```javascript
// Watch for URL changes and clean up
const currentPath = location.pathname;
const checkUrl = setInterval(function() {
    if (location.pathname !== currentPath) {
        clearInterval(checkUrl);
        // Clean up your handlers here
        window.removeEventListener('popstate', myHandler);
    }
}, 100);
```

### Pattern: One-Time Handler

```javascript
// Handler that removes itself after firing once
window.addEventListener('popstate', function handler(event) {
    window.removeEventListener('popstate', handler);
    // ... do something
}, {once: true});  // Alternative: use {once: true} option
```

## DOM Manipulation

### Querying Elements

NiceGUI elements have auto-generated IDs. Use `ui.run_javascript` with element references:

```python
label = ui.label('Hello')
# Access via nicegui-id attribute
ui.run_javascript(f'document.querySelector("[data-nicegui-id=\\"{label.id}\\"]").style.color = "red"')
```

### Better: Use Classes

```python
label = ui.label('Hello').classes('my-label')
ui.run_javascript('document.querySelector(".my-label").style.color = "red"')
```

## Async JavaScript

### Awaiting Results

```python
async def fetch_data():
    result = await ui.run_javascript('''
        return await fetch('/api/data').then(r => r.json())
    ''')
    print(result)
```

### Timeout Handling

```python
try:
    result = await ui.run_javascript('someSlowOperation()', timeout=5.0)
except TimeoutError:
    ui.notify('Operation timed out', type='negative')
```

## Common Patterns

### Clipboard Operations

```python
async def copy_to_clipboard(text: str):
    await ui.run_javascript(f'navigator.clipboard.writeText("{text}")')
    ui.notify('Copied!')

ui.button('Copy', on_click=lambda: copy_to_clipboard('Hello'))
```

### Local Storage Access

```python
async def save_preference(key: str, value: str):
    await ui.run_javascript(f'localStorage.setItem("{key}", "{value}")')

async def load_preference(key: str) -> str:
    return await ui.run_javascript(f'localStorage.getItem("{key}")')
```

### Scroll Control

```python
# Scroll to top
ui.run_javascript('window.scrollTo(0, 0)')

# Scroll to element
ui.run_javascript('document.querySelector(".target").scrollIntoView()')
```

### Focus Management

```python
input_field = ui.input('Name').classes('name-input')
ui.run_javascript('document.querySelector(".name-input input").focus()')
```

## File Organization

Recommended structure for static files:

```
my_app/
├── static/
│   ├── css/
│   │   └── app.css
│   └── js/
│       ├── app.js        # General utilities
│       └── login.js      # Login-specific handlers
├── main.py
└── ...
```

## Best Practices

1. **Prefer Python over JS** - Only use JS for browser-specific functionality
2. **Always clean up** - Remove event listeners when navigating away
3. **Use external files** - Keep JS in `.js` files, not inline strings
4. **Export to `window`** - Functions called from Python must be global
5. **Handle errors** - Wrap async JS in try/catch
6. **Avoid `location.href`** - Use `ui.navigate.to()` to preserve SPA state

## See Also

- [Styling](styling.md) - CSS integration with `ui.add_head_html`
- [Authentication](authentication.md) - Back button handling for login
- [Sub Pages](sub_pages.md) - SPA navigation patterns
