"""Activity view."""
from nicegui import ui


class ActivityView:
    async def build(self) -> None:
        ui.label('Recent Activity').classes('text-xl font-semibold mb-4')
        activities = [
            {'user': 'Alice', 'action': 'Updated inventory', 'time': '2 min ago', 'icon': 'edit'},
            {'user': 'Bob', 'action': 'Created report', 'time': '15 min ago', 'icon': 'add'},
            {'user': 'Carol', 'action': 'Viewed dashboard', 'time': '1 hour ago', 'icon': 'visibility'},
        ]
        with ui.timeline(side='right'):
            for a in activities:
                with ui.timeline_entry(title=a['action'], subtitle=a['time'], icon=a['icon']):
                    ui.label(a['user']).classes('text-sm text-slate-500')
