"""Roles view."""
from nicegui import ui


class RolesView:
    async def build(self) -> None:
        ui.label('Roles & Permissions').classes('text-xl font-semibold mb-4')
        roles = [
            {'name': 'Admin', 'perms': ['Create', 'Read', 'Update', 'Delete'], 'color': 'red'},
            {'name': 'Editor', 'perms': ['Create', 'Read', 'Update'], 'color': 'blue'},
            {'name': 'Viewer', 'perms': ['Read'], 'color': 'gray'},
        ]
        for role in roles:
            with ui.card().classes('w-full mb-2'):
                with ui.row().classes('items-center gap-2'):
                    ui.badge(role['name']).props(f"color={role['color']}")
                    for perm in role['perms']:
                        ui.chip(perm).props('outline size=sm')
