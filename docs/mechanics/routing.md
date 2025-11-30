# NiceGUI Routing Architecture

This document explains how NiceGUI handles URL routing internally, including the root page mechanism, route precedence, and dynamic route registration.

## Route Matching Order

NiceGUI uses FastAPI/Starlette for routing. Routes are matched in this order:

1. **Explicit routes** - All registered `@ui.page` decorators and `app.get()`/`app.post()` routes
2. **Static/media file routes** - Routes under `/_nicegui/...` for assets
3. **404 handler fallback** - If no route matches, the 404 exception handler is triggered

## The Root Page Mechanism

When you pass a `root` function to `ui.run()`, NiceGUI uses a **404 exception handler** as a catch-all:

```python
def root():
    ui.label('Hello World')

ui.run(root)  # root() handles ALL unmatched URLs
```

### How It Works Internally

1. `ui.run()` stores the root function in `core.root`
2. The 404 exception handler checks for `core.root`:

```python
# Simplified from nicegui/nicegui.py
@app.exception_handler(404)
async def _exception_handler_404(request: Request, exception: Exception) -> Response:
    root = core.root
    if root is not None:
        # Serve the root page for ANY unmatched URL
        return await page('')._wrap(root)(request=request, **kwargs)
    # Otherwise show 404 error page
```

### URL Capture Behavior

| Scenario | Behavior |
|----------|----------|
| **With `root` function** | ALL URLs that don't match an explicit route are captured by root |
| **Without `root` function** | Unmatched URLs return a 404 error page |

### Practical Example

```python
from nicegui import ui

@ui.page('/about')
def about():
    ui.label('About page')

def root():
    ui.label('Main page')

ui.run(root)
```

| URL | Handler |
|-----|---------|
| `/about` | `about()` - explicit route takes precedence |
| `/` | `root()` - via 404 fallback |
| `/foo` | `root()` - via 404 fallback |
| `/any/path/here` | `root()` - via 404 fallback |

## Script Mode vs Page Mode

NiceGUI has two modes for defining the root page:

### Script Mode (Implicit Root)

UI elements defined at module level automatically become the root page:

```python
from nicegui import ui

ui.label('Hello')  # This IS the root page
ui.run()
```

Internally, NiceGUI wraps the script execution as the root function.

### Page Mode (Explicit Root)

Pass a function to `ui.run()`:

```python
from nicegui import ui

def root():
    ui.label('Hello')

ui.run(root)
```

### Restrictions

- **Script mode cannot use `@ui.page`** - You'll get a `RuntimeError`
- **Page mode requires explicit routes** - Use `@ui.page` for additional pages

## Dynamic Route Registration

Components like `ui.upload` register routes dynamically at runtime. These routes work correctly because:

1. **They use reserved prefixes** - Routes under `/_nicegui/...` won't conflict with user paths
2. **They're registered as real FastAPI routes** - Matched before the 404 fallback
3. **They're cleaned up on element deletion** - No route leaks

### Example: Upload Element

```python
# From nicegui/elements/upload.py
class Upload(Element):
    def __init__(self, ...):
        # Build unique URL with client and element IDs
        self._props['url'] = f'/_nicegui/client/{self.client.id}/upload/{self.id}'
        
        # Register the route dynamically
        @app.post(self._props['url'])
        async def upload_route(request: Request):
            # Handle upload...
            return {'upload': 'success'}
    
    def _handle_delete(self):
        # Clean up route when element is removed
        app.remove_route(self._props['url'])
```

### Dynamic Route URL Patterns

| Component | URL Pattern | Purpose |
|-----------|-------------|---------|
| `ui.upload` | `/_nicegui/client/{client_id}/upload/{element_id}` | File upload endpoint |
| `add_static_file` | `/_nicegui/auto/static/{hash}/{filename}` | Single-use file serving |
| `add_media_file` | `/_nicegui/auto/media/{hash}/{filename}` | Streaming media files |

## Route Precedence Summary

```
Request arrives
    ↓
Check explicit @ui.page routes
    ↓
Check app.get()/app.post() routes (including dynamic ones)
    ↓
Check /_nicegui/* internal routes
    ↓
No match → 404 exception raised
    ↓
404 handler: if core.root exists → serve root page
             else → show 404 error
```

## Combining with Sub Pages

When using `ui.sub_pages` with a root page, the routing works as follows:

1. **Server-side**: Root page catches all URLs via 404 handler
2. **Client-side**: `ui.sub_pages` handles navigation without page reloads
3. **Result**: SPA-like experience with persistent state

```python
from nicegui import ui

def root():
    with ui.header():
        ui.button('Home', on_click=lambda: ui.navigate.to('/'))
        ui.button('About', on_click=lambda: ui.navigate.to('/about'))
    
    ui.sub_pages({
        '/': lambda: ui.label('Home'),
        '/about': lambda: ui.label('About'),
    })

ui.run(root)
```

All URLs (`/`, `/about`, `/anything`) are served by `root()`, and `ui.sub_pages` handles the client-side routing.

## Best Practices

1. **Use explicit `@ui.page` for distinct pages** - When you need separate server-side handling
2. **Use `root` + `ui.sub_pages` for SPAs** - When you want persistent state and fast navigation
3. **Reserve `/_nicegui/` prefix** - Never create routes starting with `/_nicegui/`
4. **Clean up dynamic routes** - Always remove routes in `_handle_delete()` for custom components
