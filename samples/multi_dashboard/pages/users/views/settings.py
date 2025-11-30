"""Settings view."""
from nicegui import app, ui


class SettingsView:
    async def build(self) -> None:
        ui.label('User Settings').classes('text-xl font-semibold mb-4')
        if 'user_settings' not in app.storage.client:
            app.storage.client['user_settings'] = {'require_2fa': True, 'session_timeout': 30}
        settings = app.storage.client['user_settings']
        
        with ui.card().classes('w-full max-w-md'):
            with ui.row().classes('w-full justify-between items-center mb-4'):
                ui.label('Require 2FA')
                ui.switch().bind_value(settings, 'require_2fa')
            with ui.row().classes('w-full justify-between items-center'):
                ui.label('Session Timeout')
                ui.select([15, 30, 60], value=settings['session_timeout']).classes('w-20')
