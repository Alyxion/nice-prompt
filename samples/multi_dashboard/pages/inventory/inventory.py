"""Inventory dashboard implementation."""
from nicegui import ui
from .views import ProductsView, CategoriesView, StockAlertsView, SuppliersView


class InventoryDashboard:
    """Inventory dashboard - public, no login required."""
    PAGE = {'path': '/inventory', 'label': 'Inventory', 'icon': 'inventory_2'}
    
    def __init__(self):
        self.views = [
            {'path': '/', 'label': 'Products', 'icon': 'inventory', 'view': ProductsView},
            {'path': '/categories', 'label': 'Categories', 'icon': 'category', 'view': CategoriesView},
            {'path': '/alerts', 'label': 'Alerts', 'icon': 'warning', 'view': StockAlertsView},
            {'path': '/suppliers', 'label': 'Suppliers', 'icon': 'local_shipping', 'view': SuppliersView},
        ]
    
    async def build(self) -> None:
        with ui.column().classes('w-full h-full'):
            with ui.row().classes('w-full items-center mb-4 px-6 pt-6'):
                ui.icon('inventory_2').classes('text-3xl text-indigo-500')
                ui.label('Inventory Dashboard').classes('text-2xl font-bold ml-2')
            
            with ui.row().classes('w-full px-6 gap-2 border-b border-slate-200'):
                for view in self.views:
                    full_path = '/inventory' if view['path'] == '/' else f"/inventory{view['path']}"
                    ui.button(view['label'], icon=view['icon'],
                              on_click=lambda p=full_path: ui.navigate.to(p)).props('flat no-caps')
            
            with ui.column().classes('w-full flex-grow p-6 dashboard-content'):
                def make_view_builder(view_class):
                    async def builder():
                        await view_class().build()
                    return builder
                
                ui.sub_pages({v['path']: make_view_builder(v['view']) for v in self.views})
