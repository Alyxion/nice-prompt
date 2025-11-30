"""Users dashboard implementation."""
from nicegui import ui
from .views import UserListView, RolesView, ActivityView, SettingsView


class UsersDashboard:
    """Users dashboard - requires admin role."""
    PAGE = {'path': '/users', 'label': 'Users', 'icon': 'people', 'requires': 'view_users', 'hidden': 'view_users'}
    
    def __init__(self):
        self.views = [
            {'path': '/', 'label': 'Users', 'icon': 'people', 'view': UserListView},
            {'path': '/roles', 'label': 'Roles', 'icon': 'admin_panel_settings', 'view': RolesView},
            {'path': '/activity', 'label': 'Activity', 'icon': 'history', 'view': ActivityView},
            {'path': '/settings', 'label': 'Settings', 'icon': 'settings', 'view': SettingsView},
        ]
    
    async def build(self) -> None:
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full items-center mb-4 px-6 pt-6'):
                ui.icon('people').classes('text-3xl text-indigo-500')
                ui.label('Users Dashboard').classes('text-2xl font-bold ml-2')
            
            with ui.row().classes('w-full px-6 gap-2 border-b border-slate-200'):
                for view in self.views:
                    full_path = '/users' if view['path'] == '/' else f"/users{view['path']}"
                    ui.button(view['label'], icon=view['icon'],
                              on_click=lambda p=full_path: ui.navigate.to(p)).props('flat no-caps')
            
            with ui.column().classes('w-full flex-grow p-6 dashboard-content'):
                def make_view_builder(view_class):
                    async def builder():
                        await view_class().build()
                    return builder
                
                ui.sub_pages({v['path']: make_view_builder(v['view']) for v in self.views})
