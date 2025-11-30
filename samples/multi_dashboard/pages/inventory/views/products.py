"""Products view."""
from nicegui import app, ui


class ProductsView:
    async def build(self) -> None:
        if 'products' not in app.storage.client:
            app.storage.client['products'] = [
                {'id': 1, 'name': 'Laptop Pro 15"', 'sku': 'LP-15-001', 'stock': 45, 'price': 1299.99},
                {'id': 2, 'name': 'Wireless Mouse', 'sku': 'WM-002', 'stock': 230, 'price': 29.99},
                {'id': 3, 'name': 'USB-C Hub', 'sku': 'UCH-003', 'stock': 89, 'price': 49.99},
                {'id': 4, 'name': 'Mechanical Keyboard', 'sku': 'MK-004', 'stock': 12, 'price': 149.99},
            ]
        
        ui.label('Product Inventory').classes('text-xl font-semibold mb-4')
        columns = [
            {'name': 'name', 'label': 'Product', 'field': 'name', 'align': 'left'},
            {'name': 'sku', 'label': 'SKU', 'field': 'sku'},
            {'name': 'stock', 'label': 'Stock', 'field': 'stock'},
            {'name': 'price', 'label': 'Price', 'field': 'price'},
        ]
        rows = [{'name': p['name'], 'sku': p['sku'], 'stock': p['stock'], 'price': f"${p['price']:.2f}"} 
                for p in app.storage.client['products']]
        ui.table(columns=columns, rows=rows).classes('w-full')
