"""Settings dashboard implementation."""
from nicegui import app, ui


def get_auth():
    """Get auth session from app.storage.client."""
    return app.storage.client.get('auth')


class SettingsDashboard:
    """Settings dashboard - requires login but not admin role."""
    PAGE = {'path': '/settings', 'label': 'Settings', 'icon': 'settings', 'requires': 'view_settings'}
    
    async def build(self) -> None:
        auth = get_auth()
        
        with ui.column().classes('w-full h-full dashboard-content'):
            with ui.row().classes('w-full items-center mb-4 px-6 pt-6'):
                ui.icon('settings').classes('text-3xl text-indigo-500')
                ui.label('Settings').classes('text-2xl font-bold ml-2')
            
            with ui.column().classes('w-full p-6 gap-4 max-w-xl'):
                # User info card
                with ui.card().classes('w-full'):
                    ui.label('Account').classes('text-lg font-semibold mb-2')
                    with ui.row().classes('items-center gap-4'):
                        ui.icon('account_circle').classes('text-4xl text-indigo-500')
                        with ui.column():
                            ui.label(auth.username).classes('text-lg font-medium')
                            ui.label(f'Roles: {", ".join(auth.roles)}').classes('text-sm text-gray-500')
                
                # Preferences card
                with ui.card().classes('w-full'):
                    ui.label('Preferences').classes('text-lg font-semibold mb-2')
                    ui.switch('Enable notifications')
                    ui.switch('Dark mode by default')
                    ui.select(
                        ['English', 'German', 'French'],
                        label='Language',
                        value='English'
                    ).classes('w-48')
                
                # Danger zone
                with ui.card().classes('w-full border-red-200'):
                    ui.label('Danger Zone').classes('text-lg font-semibold mb-2 text-red-500')
                    ui.button('Delete Account', color='red').props('outline')
