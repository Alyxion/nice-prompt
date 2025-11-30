# NiceGUI Sub Pages - Client-Side Routing

`ui.sub_pages` enables **Single Page Application (SPA)** routing within NiceGUI. Navigation between views happens client-side without full page reloads.

## Key Advantages

- **Persistent State**: `app.storage.client` stays alive across sub-page navigation - objects remain "living"
- **Fast Navigation**: No script reload, instant view switching
- **Shared Layout**: Header, sidebar, and other elements persist across routes

## How It Works with Server Routing

When using `ui.sub_pages` with a root page, two routing layers work together:

1. **Server-side (404 fallback)**: The root page catches ALL unmatched URLs
2. **Client-side (sub_pages)**: JavaScript handles navigation without page reloads

```
Browser requests /about
    ↓
Server: No explicit @ui.page('/about') route
    ↓
404 handler: core.root exists → serve root page
    ↓
Client: ui.sub_pages matches '/about' → render about content
```

This is why you **don't need** a catch-all `@ui.page('/{_:path}')` pattern - the root page mechanism already captures all URLs.

See [Routing Architecture](routing.md) for detailed explanation of route precedence.

## Basic Usage

```python
from nicegui import ui

@ui.page('/')
def main_page():
    with ui.header():
        ui.button('Home', on_click=lambda: ui.navigate.to('/'))
        ui.button('About', on_click=lambda: ui.navigate.to('/about'))
        ui.button('User', on_click=lambda: ui.navigate.to('/user/123'))
    
    ui.sub_pages({
        '/': home_page,
        '/about': about_page,
        '/user/{id}': user_page,
    })

def home_page():
    ui.label('Welcome to the home page')

def about_page():
    ui.label('About us')

def user_page(id: str):
    ui.label(f'User profile: {id}')

ui.run()
```

> **Note**: The catch-all pattern `@ui.page('/{_:path}')` is **not required**. `ui.sub_pages` handles client-side routing internally - navigation between sub-pages happens without server round-trips.

## Route Patterns

Routes support path parameters using `{param_name}` syntax:

| Pattern | Matches | Parameters |
|---------|---------|------------|
| `/` | Exact root | None |
| `/about` | Exact path | None |
| `/user/{id}` | `/user/123` | `id='123'` |
| `/post/{category}/{id}` | `/post/tech/42` | `category='tech'`, `id='42'` |

## Page Builder Functions

Builder functions receive path parameters as keyword arguments:

```python
def user_page(id: str):
    ui.label(f'Viewing user {id}')

def product_page(category: str, product_id: str):
    ui.label(f'Product {product_id} in {category}')
```

## PageArguments for Advanced Access

Use `PageArguments` type hint for full route information:

```python
from nicegui.page_arguments import PageArguments

def search_page(args: PageArguments):
    ui.label(f'Path: {args.path}')
    ui.label(f'Parameters: {args.parameters}')
    ui.label(f'Query: {args.query_params.get("q")}')  # ?q=value
    ui.label(f'Fragment: {args.fragment}')             # #section
```

## Constructor Parameters

```python
ui.sub_pages(
    routes={...},              # Path pattern → builder function
    root_path='/app',          # Path prefix to strip (reverse proxy)
    data={'key': 'value'},     # Data passed to all builders
    show_404=True,             # Show 404 for unmatched routes
)
```

## Dynamic Route Addition

```python
router = ui.sub_pages({'/': home})
router.add('/settings', settings_page)
router.add('/profile/{username}', profile_page)
```

## Nested Sub Pages

```python
def admin_section():
    ui.label('Admin Panel')
    ui.sub_pages({
        '/users': admin_users,
        '/settings': admin_settings,
    })

# Main router includes admin section
ui.sub_pages({
    '/': home,
    '/admin': admin_section,  # Nested routing
})
```

## Navigation

```python
ui.button('Home', on_click=lambda: ui.navigate.to('/'))
ui.button('Search', on_click=lambda: ui.navigate.to('/search?q=nicegui'))
ui.button('Section', on_click=lambda: ui.navigate.to('/docs#installation'))
```

## Async Page Builders

```python
async def user_page(id: str):
    ui.spinner()
    user = await fetch_user(id)
    ui.label(f'Name: {user.name}')
```

## Persistent Client State Example

Since `app.storage.client` persists across sub-page navigation, you can maintain live objects:

```python
from nicegui import app, ui

@ui.page('/')
def spa():
    # Initialize once, persists across all sub-pages
    if 'counter' not in app.storage.client:
        app.storage.client['counter'] = 0
    
    with ui.header():
        ui.label().bind_text_from(app.storage.client, 'counter', 
                                   backward=lambda c: f'Count: {c}')
        ui.button('+', on_click=lambda: app.storage.client.update(
            counter=app.storage.client['counter'] + 1))
    
    ui.sub_pages({
        '/': page_a,
        '/other': page_b,
    })

def page_a():
    ui.label('Page A - counter persists when navigating!')
    ui.button('Go to B', on_click=lambda: ui.navigate.to('/other'))

def page_b():
    ui.label('Page B - same counter value!')
    ui.button('Go to A', on_click=lambda: ui.navigate.to('/'))
```

## Custom 404 Handling

Subclass `SubPages` for custom error pages:

```python
from nicegui.elements.sub_pages import SubPages

class CustomSubPages(SubPages):
    def _render_404(self):
        ui.label('Page not found!').classes('text-red-500')
        ui.button('Go Home', on_click=lambda: ui.navigate.to('/'))

# Use instead of ui.sub_pages
CustomSubPages({'/': home, '/about': about})
```

## Route Protection

Since sub pages only render **after** the parent page executes, authentication checks belong in the parent/layout page - not in individual sub pages.

See [Authentication Pattern](authentication.md) for a complete example with login page, session management, and role-based access.

## Layout Constraints

### Header/Drawer Must Be Outside sub_pages

Top-level layout elements (`ui.header`, `ui.left_drawer`, `ui.footer`) **cannot** be nested inside `ui.sub_pages`. They must be created in the parent:

```python
# CORRECT - header/drawer at root level
def root():
    header = ui.header()
    drawer = ui.left_drawer()
    
    with ui.column():
        ui.sub_pages({...})

# WRONG - will cause RuntimeError
def root():
    ui.sub_pages({
        '/': lambda: ui.header()  # Error!
    })
```

### Hiding Header/Drawer on Login Page

Store references and toggle visibility. **Key pattern**: Call `show()` at the start of every regular page builder to handle back button navigation from login:

```python
class AppLayout:
    def __init__(self):
        self.header = None
        self.drawer = None
    
    def hide(self):
        if self.header:
            self.header.set_visibility(False)
        if self.drawer:
            self.drawer.set_visibility(False)
            self.drawer.hide()
    
    def show(self):
        if self.header:
            self.header.set_visibility(True)
        if self.drawer:
            self.drawer.set_visibility(True)
            self.drawer.show()
    
    def build_login_page(self):
        self.hide()  # Hide on login
        # ... login form
    
    def make_page_builder(self, page_info):
        async def builder():
            self.show()  # Always show on regular pages (handles back button)
            # ... page content
        return builder
    
    def build(self):
        self.header = ui.header()
        self.drawer = ui.left_drawer()
        
        ui.sub_pages({
            '/login': self.build_login_page,
            '/': self.make_page_builder({'path': '/'}),
        })
```

This pattern ensures header/drawer are restored when:
- User clicks Cancel on login
- User presses browser back button from login
- User navigates to any regular page

### Full-Width Content

By default, NiceGUI may constrain content width. Add CSS to ensure full width:

```css
.nicegui-content,
.nicegui-sub-pages,
.q-page,
.q-page-container {
    width: 100% !important;
    max-width: 100% !important;
}
```

## Login Page Integration

**Key insight**: The login page should be a sub_page route, not a separate `@ui.page('/login')`:

```python
ui.sub_pages({
    '/login': build_login_page,  # Part of same SPA
    '/': home_page,
    '/settings': settings_page,
})
```

Benefits:
- Session state (`app.storage.client`) persists across navigation
- Header/drawer can be hidden/shown dynamically
- No full page reload on login/logout

## Avoiding Global Variables

Don't use global variables for UI references. Instead, use a class stored in `app.storage.client`:

```python
class AppLayout:
    @classmethod
    def current(cls) -> 'AppLayout':
        if 'layout' not in app.storage.client:
            app.storage.client['layout'] = cls()
        return app.storage.client['layout']

def root():
    AppLayout.current().build()
```

## Documentation

- [NiceGUI Sub Pages](https://nicegui.io/documentation/sub_pages)
