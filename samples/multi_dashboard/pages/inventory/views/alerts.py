"""Stock alerts view."""
from nicegui import app, ui


class StockAlertsView:
    async def build(self) -> None:
        ui.label('Stock Alerts').classes('text-xl font-semibold mb-4')
        products = app.storage.client.get('products', [])
        low_stock = [p for p in products if p['stock'] < 50]
        if low_stock:
            for p in low_stock:
                with ui.card().classes('w-full bg-amber-50 border-l-4 border-amber-500 mb-2'):
                    with ui.row().classes('items-center gap-2'):
                        ui.icon('warning').classes('text-amber-500')
                        ui.label(p['name'])
                        ui.label(f"Stock: {p['stock']}").classes('text-amber-600')
        else:
            ui.label('All products well stocked!').classes('text-green-600')
