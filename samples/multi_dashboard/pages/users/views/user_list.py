"""User list view."""
from nicegui import app, ui


class UserListView:
    async def build(self) -> None:
        if 'users' not in app.storage.client:
            app.storage.client['users'] = [
                {'id': 1, 'name': 'Alice Johnson', 'email': 'alice@example.com', 'role': 'Admin', 'status': 'Active'},
                {'id': 2, 'name': 'Bob Smith', 'email': 'bob@example.com', 'role': 'Editor', 'status': 'Active'},
                {'id': 3, 'name': 'Carol White', 'email': 'carol@example.com', 'role': 'Viewer', 'status': 'Inactive'},
            ]
        
        ui.label('User Management').classes('text-xl font-semibold mb-4')
        
        for user in app.storage.client['users']:
            with ui.card().classes('w-full mb-2'):
                with ui.row().classes('items-center justify-between'):
                    with ui.row().classes('items-center gap-3'):
                        ui.avatar(user['name'][0], color='indigo')
                        with ui.column().classes('gap-0'):
                            ui.label(user['name']).classes('font-semibold')
                            ui.label(user['email']).classes('text-sm text-slate-500')
                    with ui.row().classes('gap-2'):
                        role_colors = {'Admin': 'red', 'Editor': 'blue', 'Viewer': 'gray'}
                        ui.badge(user['role']).props(f"color={role_colors.get(user['role'], 'gray')}")
                        status_color = 'green' if user['status'] == 'Active' else 'gray'
                        ui.badge(user['status']).props(f"color={status_color} outline")
