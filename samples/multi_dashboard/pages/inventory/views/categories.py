"""Categories view."""
from nicegui import ui


class CategoriesView:
    async def build(self) -> None:
        ui.label('Categories').classes('text-xl font-semibold mb-4')
        categories = [
            {'name': 'Electronics', 'count': 45, 'icon': 'devices'},
            {'name': 'Accessories', 'count': 128, 'icon': 'cable'},
            {'name': 'Peripherals', 'count': 67, 'icon': 'keyboard'},
        ]
        with ui.row().classes('gap-4 flex-wrap'):
            for cat in categories:
                with ui.card().classes('w-48'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon(cat['icon']).classes('text-2xl text-indigo-500')
                        with ui.column().classes('gap-0'):
                            ui.label(cat['name']).classes('font-semibold')
                            ui.label(f"{cat['count']} items").classes('text-sm text-slate-500')
