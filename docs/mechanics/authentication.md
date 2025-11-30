# Authentication Pattern

This document shows how to implement authentication with NiceGUI using `ui.sub_pages` for protected routes.

## Overview

The pattern uses:
- **Signed HTTP cookies** - Persistent auth state that survives page reloads
- **`app.storage.client`** - Transient session state (redirect URLs, cached auth)
- **Dataclass for session** - Type-safe authentication state management
- **Login as sub_page** - Login page integrated into the same root, not a separate `@ui.page`
- **Permission-based access** - Pages define required permissions, roles grant permissions

## Storage Strategy

| Storage | Persistence | Use Case |
|---------|-------------|----------|
| **Signed cookies** | Browser, survives reload | Auth state (username, roles) |
| `app.storage.client` | Memory only, per tab | Transient state (redirect URL, cached session) |
| `app.storage.user` | Disk, per user | Persistent preferences (avoid for auth - disk I/O) |
| `app.storage.browser` | Browser localStorage | Client-side persistence |

### Why Signed Cookies for Auth?

- **Survives page reload** - User stays logged in after F5
- **No disk I/O** - Unlike `app.storage.user`
- **Tamper-proof** - HMAC signature prevents modification
- **Works with WebSocket** - Set via JavaScript during button clicks

> **Important**: Do NOT use `app.storage.tab` for authentication - it throws `RuntimeError` if accessed before client connection is established.

## AuthSession Dataclass

Use a dataclass with signed cookie persistence:

```python
import json
import base64
import hmac
import hashlib
from dataclasses import dataclass, field
from nicegui import app, ui, context

SECRET_KEY = 'change-me-in-production'  # Use environment variable
COOKIE_NAME = 'auth_session'
COOKIE_MAX_AGE_DAYS = 7

# Role to permissions mapping
ROLE_PERMISSIONS = {
    'user': {'view_settings'},
    'admin': {'view_settings', 'view_users', 'manage_users'},
}

# User credentials (in production, use a database)
USERS = {
    'admin': {'password': 'demo123', 'roles': ['user', 'admin']},
    'user': {'password': 'demo123', 'roles': ['user']},
    'guest': {'password': 'demo123', 'roles': []},
}

def _sign(data: str) -> str:
    """Create HMAC signature."""
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

def _encode_cookie(data: dict) -> str:
    """Encode and sign cookie data."""
    json_data = json.dumps(data)
    b64_data = base64.b64encode(json_data.encode()).decode()
    return f'{b64_data}.{_sign(b64_data)}'

def _decode_cookie(cookie: str) -> dict | None:
    """Decode and verify cookie data."""
    try:
        b64_data, signature = cookie.rsplit('.', 1)
        if not hmac.compare_digest(signature, _sign(b64_data)):
            return None
        return json.loads(base64.b64decode(b64_data).decode())
    except (ValueError, json.JSONDecodeError):
        return None

@dataclass
class AuthSession:
    """Authentication session with signed cookie persistence."""
    authenticated: bool = False
    username: str = ''
    roles: list[str] = field(default_factory=list)
    
    @classmethod
    def current(cls) -> 'AuthSession':
        """Get or create session from cookie."""
        # Return cached instance if available
        if 'auth' in app.storage.client:
            return app.storage.client['auth']
        
        # Restore from cookie
        session = cls()
        request = context.client.request
        if request and COOKIE_NAME in request.cookies:
            data = _decode_cookie(request.cookies[COOKIE_NAME])
            if data:
                session.authenticated = data.get('authenticated', False)
                session.username = data.get('username', '')
                session.roles = data.get('roles', [])
        
        app.storage.client['auth'] = session
        return session
    
    def _set_cookie(self) -> None:
        """Set cookie via JavaScript (works during WebSocket callbacks)."""
        data = {'authenticated': self.authenticated, 'username': self.username, 'roles': self.roles}
        cookie_value = _encode_cookie(data)
        ui.run_javascript(
            f'document.cookie = "{COOKIE_NAME}={cookie_value}; path=/; max-age={COOKIE_MAX_AGE_DAYS * 86400}; samesite=lax";'
        )
    
    def _delete_cookie(self) -> None:
        """Delete cookie via JavaScript."""
        ui.run_javascript(f'document.cookie = "{COOKIE_NAME}=; path=/; max-age=0";')
    
    def login(self, username: str, roles: list[str]) -> None:
        """Set authenticated state and persist to cookie."""
        self.authenticated = True
        self.username = username
        self.roles = roles
        self._set_cookie()
    
    def logout(self) -> None:
        """Clear authenticated state and cookie."""
        self.authenticated = False
        self.username = ''
        self.roles = []
        self._delete_cookie()
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a permission based on their roles."""
        for role in self.roles:
            if permission in ROLE_PERMISSIONS.get(role, set()):
                return True
        return False
    
    @property
    def redirect_after_login(self) -> str:
        """Get redirect URL (stored in client storage, not cookie)."""
        return app.storage.client.get('redirect_after_login', '')
    
    @redirect_after_login.setter
    def redirect_after_login(self, value: str) -> None:
        app.storage.client['redirect_after_login'] = value
    
    def get_redirect_and_clear(self) -> str:
        """Get redirect URL and clear it."""
        url = self.redirect_after_login
        if 'redirect_after_login' in app.storage.client:
            del app.storage.client['redirect_after_login']
        return url
```

### Why JavaScript for Cookies?

During button click handlers (WebSocket callbacks), `context.client.response` is not available. Using `ui.run_javascript()` to set cookies works in all contexts. The cookie is still signed with HMAC to prevent tampering.

## Login Page as Sub Page (Not Separate @ui.page)

**Key insight**: The login page should be a sub_page, not a separate `@ui.page('/login')`. This ensures:
- Session state persists (no full page reload)
- Header/drawer can be hidden/shown dynamically
- Consistent SPA navigation

```python
class AppLayout:
    """Application layout managing header, drawer, and page routing."""
    
    def __init__(self):
        self.header: ui.header = None
        self.drawer: ui.left_drawer = None
    
    @classmethod
    def current(cls) -> 'AppLayout':
        """Get or create the layout for this client."""
        if 'layout' not in app.storage.client:
            app.storage.client['layout'] = cls()
        return app.storage.client['layout']
    
    def show(self) -> None:
        """Show header and drawer."""
        if self.header:
            self.header.set_visibility(True)
        if self.drawer:
            self.drawer.set_visibility(True)
            self.drawer.show()
    
    def hide(self) -> None:
        """Hide header and drawer."""
        if self.header:
            self.header.set_visibility(False)
        if self.drawer:
            self.drawer.set_visibility(False)
            self.drawer.hide()
    
    def build_login_page(self) -> None:
        """Build login page - hide header/drawer."""
        self.hide()
        
        auth = AuthSession.current()
        
        # Already logged in - redirect to home
        if auth.authenticated:
            redirect = auth.get_redirect_and_clear() or '/'
            ui.navigate.to(redirect)
            return
        
        def do_login():
            if auth.try_login(username_input.value, password_input.value):
                self.show()
                redirect = auth.get_redirect_and_clear() or '/'
                ui.navigate.to(redirect)
            else:
                ui.notify('Invalid credentials', type='negative')
        
        with ui.card().classes('absolute-center w-80'):
            ui.label('Sign In').classes('text-2xl font-bold')
            username_input = ui.input('Username').on('keydown.enter', do_login)
            password_input = ui.input('Password', password=True).on('keydown.enter', do_login)
            ui.button('Sign In', on_click=do_login).classes('w-full mt-4')
    
    def build(self) -> None:
        """Build the complete app shell."""
        # Header
        self.header = ui.header()
        with self.header:
            ui.label('My App')
        
        # Drawer
        self.drawer = ui.left_drawer(value=True)
        with self.drawer:
            ui.label('Navigation')
        
        # All pages including login
        ui.sub_pages({
            '/login': self.build_login_page,
            '/': lambda: ui.label('Home'),
            '/settings': self.make_protected_page('view_settings', settings_page),
        })

def root():
    AppLayout.current().build()

ui.run(root, title='My App')
```

## Permission-Based Page Protection

Pages define what permissions they require. Users have roles, roles grant permissions:

```python
# Page metadata
PAGES = [
    {'path': '/', 'label': 'Home', 'icon': 'home'},
    {'path': '/settings', 'label': 'Settings', 'icon': 'settings', 'requires': 'view_settings'},
    {'path': '/users', 'label': 'Users', 'icon': 'people', 'requires': 'view_users', 'hidden': 'view_users'},
]

def get_visible_pages() -> list[dict]:
    """Get pages visible to current user based on permissions."""
    auth = AuthSession.current()
    visible = []
    for page in PAGES:
        # 'hidden' means page is only shown if user has that permission
        hidden_unless = page.get('hidden')
        if hidden_unless and not auth.has_permission(hidden_unless):
            continue
        visible.append(page)
    return visible

def make_page_builder(self, page_info: dict):
    """Create a lazy builder for a dashboard page with permission check."""
    async def builder():
        # Always show header/drawer on regular pages (handles back button from login)
        self.show()
        
        auth = AuthSession.current()
        required = page_info.get('requires')
        
        if required:
            if not auth.authenticated:
                # Store target for redirect after login
                auth.redirect_after_login = page_info['path']
                ui.navigate.to('/login')
                return
            if not auth.has_permission(required):
                ui.label('Access Denied').classes('text-2xl text-red-500')
                return
        
        await page_info['dashboard']().build()
    return builder
```

The `self.show()` call at the start ensures header/drawer are visible when navigating to any regular page, including via browser back button from login.

## Redirect After Login

Store the originally requested URL and redirect after successful login:

```python
# In page builder - when user tries to access protected page
if not auth.authenticated:
    auth.redirect_after_login = page_info['path']
    ui.navigate.to('/login')
    return

# In login handler - after successful login
redirect = auth.get_redirect_and_clear() or '/'
ui.navigate.to(redirect)
```

## Logout - Clear Auth Only, Not Entire Storage

**Important**: Don't use `app.storage.client.clear()` - it clears ALL client state including UI references. Instead, only clear auth-related fields:

```python
def logout(self) -> None:
    """Clear authenticated state (not entire storage)."""
    self.authenticated = False
    self.username = ''
    self.roles = []
    self.redirect_after_login = ''
```

## Navigation Best Practices

- **Always use `ui.navigate.to()`** - Never use `ui.context.client.open()` or JavaScript `window.location` as they cause full page reloads and lose session state
- **Login page should redirect if already authenticated** - Prevents accessing login when already logged in

```python
def build_login_page(self):
    auth = AuthSession.current()
    
    # Already logged in - redirect to home
    if auth.authenticated:
        redirect = auth.get_redirect_and_clear() or '/'
        ui.navigate.to(redirect)
        return
    
    # ... show login form
```

## See Also

- [Sub Pages](sub_pages.md) - Client-side routing with `ui.sub_pages`
- [Routing Architecture](routing.md) - How URL routing works internally
- [JavaScript Integration](javascript_integration.md) - Custom JS for browser interactions
- [Binding and State](binding_and_state.md) - Storage options explained
