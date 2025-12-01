# NiceGUI Application Structure

## Minimal Application

```python
from nicegui import ui

ui.label('Hello World')

ui.run()
```

## Production Application Structure

**Critical**: Always wrap `ui.run()` in the multiprocessing guard for production:

```python
from nicegui import ui

@ui.page('/')
def index():
    ui.label('Hello World')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
```

### Why This Guard?

- **`__main__`** - Normal script execution
- **`__mp_main__`** - Multiprocessing spawn context (used on macOS/Windows)

Without the guard:
1. **Multiprocessing** - Worker processes would start their own servers
2. **Import safety** - Importing your module would start the server
3. **Testing** - Test frameworks would trigger `ui.run()`
4. **Reload mode** - Hot reload would create duplicate servers

## Recommended Project Structure

### Multi-Page Application (with @ui.page)

```
my_app/
├── main.py              # Entry point with ui.run()
├── pages/
│   ├── __init__.py
│   ├── home.py          # @ui.page('/') 
│   ├── about.py         # @ui.page('/about')
│   └── dashboard.py     # @ui.page('/dashboard')
├── components/
│   ├── __init__.py
│   ├── header.py        # Reusable header component
│   └── sidebar.py       # Reusable sidebar
├── static/              # Static files (images, CSS)
├── requirements.txt
└── pyproject.toml
└── AGENTS.md
```

### SPA with Sub Pages (Recommended for Dashboards)

For single-page applications with client-side routing:

```
my_app/
├── main.py              # Server setup only (static files, page discovery, ui.run)
├── layout.py            # AppLayout class (header, drawer, routing, auth checks)
├── models/
│   ├── __init__.py      # Exports AuthSession, etc.
│   └── auth.py          # AuthSession dataclass, USERS, ROLE_PERMISSIONS
├── pages/
│   ├── home/
│   │   ├── __init__.py      # Exports only
│   │   └── home.py          # Implementation
│   ├── settings/
│   │   ├── __init__.py
│   │   └── settings.py
│   └── ...
├── static/
│   ├── css/
│   │   └── app.css          # Custom styles
│   └── js/
│       └── app.js           # Custom JavaScript
└── pyproject.toml
└── AGENTS.md
```

### Separation of Concerns

**`main.py`** - Server setup only:
```python
from pathlib import Path
from nicegui import app, ui
from layout import AppLayout

STATIC_DIR = Path(__file__).parent / 'static'
PAGES_DIR = Path(__file__).parent / 'pages'

app.add_static_files('/static', STATIC_DIR)
AppLayout.discover_pages(str(PAGES_DIR), exclude={'login'})

def root():
    AppLayout.current().build()

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        root,
        title='My App',
        reload=True,
        uvicorn_reload_includes='*.py,*.js,*.css',
    )
```

**`layout.py`** - All UI logic (header, drawer, navigation, auth checks)

### Module Organization

Keep `__init__.py` files minimal - they should only export:

```python
# pages/home/__init__.py
"""Home page module."""
from .home import HomePage

__all__ = ['HomePage']
```

Implementation goes in a separate file:

```python
# pages/home/home.py
"""Home page implementation."""
from nicegui import ui

class HomePage:
    PAGE = {'path': '/', 'label': 'Home', 'icon': 'home'}
    
    async def build(self) -> None:
        ui.label('Welcome!')
```

This pattern:
- Keeps imports clean
- Avoids circular dependencies  
- Makes it clear what each module exports
- Allows IDE navigation to the actual implementation
- **Names files after content** - `home.py` not `page.py` or `dashboard.py`

### main.py
```python
from nicegui import app, ui

# Import pages to register routes
from pages import home, about, dashboard

# Serve static files
app.add_static_files('/static', 'static')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        title='My App',
        port=8080,
    )
```

### pages/home.py
```python
from nicegui import ui
from components.header import create_header

@ui.page('/')
def home():
    create_header()
    ui.label('Welcome!')
```

### components/header.py
```python
from nicegui import ui

def create_header():
    with ui.header().classes('bg-blue-500'):
        ui.label('My App').classes('text-xl text-white')
        with ui.row():
            ui.link('Home', '/').classes('text-white')
            ui.link('About', '/about').classes('text-white')
```

## ui.run() Options

```python
ui.run(
    # Server
    host='0.0.0.0',          # Bind address (default: '127.0.0.1')
    port=8080,               # Port (default: 8080)
    
    # Display
    title='My App',          # Browser tab title
    dark=None,               # Dark mode: True, False, or None (auto)
    
    # Development
    reload=True,             # Hot reload on file changes
    show=True,               # Open browser on start
    
    # Native mode
    native=False,            # Run in native window
    window_size=(800, 600),  # Native window size
    
    # Storage
    storage_secret='secret', # Secret for signed storage
)
```

## Lifecycle Hooks

```python
from nicegui import app, ui

@app.on_startup
async def startup():
    """Called once when app starts"""
    print('App starting...')
    # Initialize database, load config, etc.

@app.on_shutdown  
async def shutdown():
    """Called once when app stops"""
    print('App shutting down...')
    # Cleanup resources

@app.on_connect
async def connect():
    """Called when each client connects"""
    print('Client connected')

@app.on_disconnect
async def disconnect():
    """Called when each client disconnects"""
    print('Client disconnected')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
```

## Integration with FastAPI

For existing FastAPI applications:

```python
from fastapi import FastAPI
from nicegui import ui

app = FastAPI()

@app.get('/api/data')
def get_data():
    return {'value': 42}

@ui.page('/')
def index():
    ui.label('NiceGUI + FastAPI')

ui.run_with(app)  # Attach to existing FastAPI app
```

## Environment-Based Configuration

```python
import os
from nicegui import ui

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

@ui.page('/')
def index():
    ui.label('My App')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run(
        host='0.0.0.0' if not DEBUG else '127.0.0.1',
        port=int(os.getenv('PORT', 8080)),
        reload=DEBUG,
        show=DEBUG,
    )
```

## Common Mistakes

### ❌ Missing main guard
```python
from nicegui import ui

ui.label('Hello')
ui.run()  # Will cause issues with multiprocessing/reload
```

### ✅ With main guard
```python
from nicegui import ui

ui.label('Hello')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
```

### ❌ Code after ui.run()
```python
if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
    print('This never executes!')  # ui.run() blocks
```

### ✅ Use lifecycle hooks instead
```python
@app.on_startup
async def init():
    print('This runs at startup')

if __name__ in {'__main__', '__mp_main__'}:
    ui.run()
```
