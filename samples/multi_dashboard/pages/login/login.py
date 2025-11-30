"""Login page implementation."""
from nicegui import ui
from models import AuthSession


class LoginPage:
    """Login page - displayed without header/drawer."""
    PAGE = {'path': '/login', 'label': 'Login', 'icon': 'login'}
    
    def __init__(self, on_login_success: callable = None):
        self.on_login_success = on_login_success
    
    def build(self) -> None:
        """Build the login form."""
        auth = AuthSession.current()
        
        # Already logged in - redirect to home or target
        if auth.authenticated:
            redirect = auth.get_redirect_and_clear() or '/'
            ui.navigate.to(redirect)
            return
        
        has_redirect = bool(auth.redirect_after_login)
        
        def do_login():
            if auth.try_login(username_input.value, password_input.value):
                if self.on_login_success:
                    self.on_login_success()
                redirect = auth.get_redirect_and_clear() or '/'
                ui.navigate.to(redirect)
            else:
                ui.notify('Invalid credentials', type='negative')
        
        def do_cancel():
            auth.redirect_after_login = ''
            ui.navigate.to('/')
        
        with ui.card().classes('absolute-center login-card'):
            ui.label('Multi-Dashboard App').classes('login-title')
            ui.label('Sign in to continue').classes('login-subtitle')
            username_input = ui.input('Username').props('outlined').classes('w-full').on('keydown.enter', do_login)
            password_input = ui.input('Password', password=True).props('outlined').classes('w-full').on('keydown.enter', do_login)
            with ui.row().classes('w-full mt-4 gap-2'):
                if has_redirect:
                    ui.button('Cancel', on_click=do_cancel).props('flat').classes('flex-1')
                ui.button('Sign In', on_click=do_login).classes('flex-1 btn-primary')
            ui.label('Hint: admin, user, or guest (password: demo123)').classes('login-hint')
        
        # Handle browser back button - redirect to home instead of protected page
        if has_redirect:
            ui.run_javascript('setupLoginBackHandler()')
