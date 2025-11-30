"""Suppliers view."""
from nicegui import ui


class SuppliersView:
    async def build(self) -> None:
        ui.label('Suppliers').classes('text-xl font-semibold mb-4')
        suppliers = [
            {'name': 'TechSupply Co.', 'contact': 'john@techsupply.com', 'rating': 4.5},
            {'name': 'Global Parts', 'contact': 'sales@globalparts.com', 'rating': 4.2},
        ]
        for s in suppliers:
            with ui.card().classes('w-full mb-2'):
                with ui.row().classes('justify-between'):
                    with ui.column().classes('gap-0'):
                        ui.label(s['name']).classes('font-semibold')
                        ui.label(s['contact']).classes('text-slate-500')
                    with ui.row().classes('items-center gap-1'):
                        ui.icon('star').classes('text-amber-400')
                        ui.label(str(s['rating']))
