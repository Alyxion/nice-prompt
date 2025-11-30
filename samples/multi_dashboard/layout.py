"""Application Layout - Main UI with header, drawer, and page routing."""
import importlib
from pathlib import Path
from nicegui import app, ui

from models import AuthSession
from pages.login import LoginPage


class AppLayout:
    """Application layout managing header, drawer, and page routing."""
    
    # Class-level page registry (populated once at startup)
    _pages: list[dict] = None
    
    def __init__(self):
        self.header: ui.header = None
        self.drawer: ui.left_drawer = None
        self._user_menu: ui.refreshable = None
        self._nav_list: ui.refreshable = None
    
    @classmethod
    def current(cls) -> 'AppLayout':
        """Get or create the layout for this client."""
        if 'layout' not in app.storage.client:
            app.storage.client['layout'] = cls()
        return app.storage.client['layout']
    
    @classmethod
    def discover_pages(cls, package_path: str, exclude: set[str] = None) -> list[dict]:
        """Auto-discover page classes with PAGE = {'path': '...', 'label': '...', 'icon': '...'} attribute."""
        exclude = exclude or set()
        is_page = lambda obj: isinstance(obj, type) and isinstance(getattr(obj, 'PAGE', None), dict)
        pages = []
        for item in Path(package_path).iterdir():
            if item.is_dir() and item.name not in exclude and (item / '__init__.py').exists():
                module = importlib.import_module(f'pages.{item.name}')
                for name in dir(module):
                    obj = getattr(module, name)
                    if is_page(obj):
                        pages.append({**obj.PAGE, 'dashboard': obj})
        cls._pages = sorted(pages, key=lambda p: (p['path'] != '/', p['path']))
        return cls._pages
    
    @classmethod
    def pages(cls) -> list[dict]:
        """Get all discovered pages."""
        return cls._pages or []
    
    def get_visible_pages(self) -> list[dict]:
        """Get pages visible to current user based on permissions.
        
        Pages with 'hidden' permission are only shown if user has that permission.
        Pages with only 'requires' are always shown but access is checked on navigation.
        """
        auth = AuthSession.current()
        visible = []
        for page in self.pages():
            hidden_unless = page.get('hidden')
            if hidden_unless and not auth.has_permission(hidden_unless):
                continue
            visible.append(page)
        return visible
    
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
    
    def refresh(self) -> None:
        """Refresh user menu and nav list after auth change."""
        if self._user_menu:
            self._user_menu.refresh()
        if self._nav_list:
            self._nav_list.refresh()
    
    def logout(self) -> None:
        """Handle logout."""
        AuthSession.current().logout()
        self.refresh()
        ui.navigate.to('/')
    
    def build_user_menu(self) -> None:
        """Build user menu - refreshable on auth change."""
        auth = AuthSession.current()
        
        if auth.authenticated:
            with ui.button(icon='account_circle').props('flat round color=white'):
                with ui.menu().props('auto-close').classes('user-menu'):
                    with ui.column().classes('user-info'):
                        ui.label(auth.username).classes('user-name')
                        ui.label(', '.join(auth.roles)).classes('user-roles')
                    with ui.item(on_click=self.logout):
                        with ui.item_section().props('avatar'):
                            ui.icon('logout').classes('text-red-500')
                        with ui.item_section():
                            ui.item_label('Logout')
        else:
            ui.button('Login', icon='login', on_click=lambda: ui.navigate.to('/login')).props('flat color=white')
    
    def build_nav_list(self) -> None:
        """Build navigation list - refreshable on auth change."""
        with ui.list().classes('w-full'):
            for page in self.get_visible_pages():
                with ui.item(on_click=lambda p=page['path']: ui.navigate.to(p)).classes('rounded-lg mx-2'):
                    with ui.item_section().props('avatar'):
                        ui.icon(page['icon']).classes('text-indigo-500')
                    with ui.item_section():
                        ui.item_label(page['label'])
    
    def build_login_page(self) -> None:
        """Build login page - hide header/drawer."""
        self.hide()
        
        def on_login_success():
            self.refresh()
        
        LoginPage(on_login_success=on_login_success).build()
    
    def make_page_builder(self, page_info: dict):
        """Create a lazy builder for a dashboard page."""
        async def builder():
            # Always show header/drawer on regular pages (handles back button from login)
            self.show()
            
            auth = AuthSession.current()
            required = page_info.get('requires')
            
            # Check if permission is required
            if required:
                if not auth.authenticated:
                    # Not logged in - store target and redirect to login
                    auth.redirect_after_login = page_info['path']
                    ui.navigate.to('/login')
                    return
                if not auth.has_permission(required):
                    # Logged in but missing permission
                    ui.label('Access Denied').classes('text-2xl text-red-500')
                    ui.label(f'You need the "{required}" permission to view this page.')
                    return
            
            await page_info['dashboard']().build()
        return builder
    
    def build(self) -> None:
        """Build the complete layout."""
        # Include custom CSS and JS
        ui.add_head_html('<link rel="stylesheet" href="/static/css/app.css">')
        ui.add_head_html('<script src="/static/js/login.js"></script>')
        
        # Create refreshable wrappers
        @ui.refreshable
        def user_menu():
            self.build_user_menu()
        
        @ui.refreshable
        def nav_list():
            self.build_nav_list()
        
        self._user_menu = user_menu
        self._nav_list = nav_list
        
        # Header
        self.header = ui.header().classes('items-center app-header')
        with self.header:
            ui.button(icon='menu', on_click=lambda: self.drawer.toggle()).props('flat round color=white')
            ui.label('Multi-Dashboard App').classes('text-xl text-white ml-2 app-title')
            ui.space()
            user_menu()
        
        # Navigation Drawer
        self.drawer = ui.left_drawer(value=True).classes('nav-drawer bg-slate-50 dark:bg-slate-800')
        with self.drawer:
            ui.label('Dashboards').classes('nav-header p-4')
            nav_list()
            
            ui.separator().classes('my-4')
            
            # Dark mode toggle
            with ui.row().classes('p-4 items-center'):
                ui.icon('dark_mode').classes('text-slate-500')
                dark = ui.dark_mode()
                ui.switch('Dark Mode').bind_value(dark).classes('ml-2')
        
        # All pages including login
        with ui.column().classes('w-full h-full p-0'):
            ui.sub_pages({
                '/login': self.build_login_page,
                **{page['path']: self.make_page_builder(page) for page in self.pages()}
            })
