# Multi-Dashboard Application

A complex application demonstrating class-based architecture with multiple dashboards, each containing multiple views using nested `ui.sub_pages`.

## Architecture

```
main.py                     # Main app with navigation drawer
├── dashboards/
│   ├── analytics.py       # Analytics dashboard + 3 views (self-contained)
│   ├── inventory.py       # Inventory dashboard + 4 views (self-contained)
│   └── users.py           # Users dashboard + 4 views (self-contained)
```

Each dashboard file is **self-contained** - no base classes. You can read any single file and understand exactly what it does.

## Key Patterns

### 1. View Class with Async Build

```python
class OverviewView:
    """Overview with key metrics and charts."""
    
    async def build(self) -> None:
        """Build the overview UI with loading state."""
        container = ui.column().classes('w-full')
        
        # Show loading spinner
        with container:
            with ui.row().classes('w-full justify-center py-8'):
                ui.spinner(size='lg')
                ui.label('Loading...')
        
        await asyncio.sleep(0.5)  # Simulate API call
        
        # Replace with actual content
        container.clear()
        with container:
            # Build actual UI...
```

### 2. Dashboard Class with Nested Sub Pages

```python
class AnalyticsDashboard:
    """Analytics dashboard with overview, reports, and real-time views."""
    
    def __init__(self):
        self.views = [
            {'path': '/', 'label': 'Overview', 'icon': 'dashboard', 'view': OverviewView},
            {'path': '/reports', 'label': 'Reports', 'icon': 'description', 'view': ReportsView},
            {'path': '/realtime', 'label': 'Real-Time', 'icon': 'speed', 'view': RealTimeView},
        ]
    
    async def build(self) -> None:
        """Build the dashboard with header, view tabs, and nested sub_pages."""
        with ui.column().classes('w-full h-full'):
            # Dashboard header
            with ui.row().classes('w-full items-center mb-4 px-6 pt-6'):
                ui.icon('analytics').classes('text-3xl text-indigo-500')
                ui.label('Analytics Dashboard').classes('text-2xl font-bold ml-2')
            
            # View navigation tabs
            with ui.row().classes('w-full px-6 gap-2'):
                for view in self.views:
                    ui.button(view['label'], icon=view['icon'],
                              on_click=lambda p=view['path']: ui.navigate.to(p))
            
            # Nested sub_pages for views
            with ui.column().classes('w-full flex-grow p-6'):
                def make_view_builder(view_class):
                    async def builder():
                        await view_class().build()
                    return builder
                
                ui.sub_pages({
                    view['path']: make_view_builder(view['view'])
                    for view in self.views
                })
```

### 3. Main App with Dynamic Page Registration

```python
def register_pages(paths: list[str]):
    """Decorator factory that registers a function for multiple page paths."""
    def decorator(func):
        return reduce(lambda f, path: ui.page(path)(f), paths, func)
    return decorator

DASHBOARDS = [
    {'path': '/', 'dashboard': AnalyticsDashboard},
    {'path': '/inventory', 'dashboard': InventoryDashboard},
    {'path': '/users', 'dashboard': UsersDashboard},
]

@register_pages([item['path'] for item in DASHBOARDS])
def main():
    # Lazy builder - only instantiates dashboard when navigated to
    def make_builder(dashboard_class):
        async def builder():
            await dashboard_class().build()
        return builder
    
    ui.sub_pages({
        item['path']: make_builder(item['dashboard'])
        for item in DASHBOARDS
    })
```

## Dashboards

### Analytics Dashboard (`/`)
- **Overview**: Key metrics, revenue chart, traffic sources
- **Reports**: Report generation and history
- **Real-Time**: Live updating metrics and charts

### Inventory Dashboard (`/inventory`)
- **Products**: Product listing with add/search
- **Categories**: Category management
- **Stock Alerts**: Low stock notifications
- **Suppliers**: Supplier directory

### Users Dashboard (`/users`)
- **All Users**: User listing with roles/status
- **Roles**: Role and permission management
- **Activity**: User activity timeline
- **Settings**: Security and user settings

## Features Demonstrated

- **Class-based architecture** for pages and views
- **Async build methods** for data loading
- **Nested sub_pages** (dashboard → views)
- **Persistent state** via `app.storage.client`
- **Real-time updates** with `ui.timer`
- **Dark mode** toggle
- **Dialogs** for add/edit operations
- **Tables, charts, timelines** and more

## Running

```bash
cd samples/multi_dashboard
poetry run python main.py
```

Open http://localhost:8080

## State Persistence

All data persists across navigation:
- Products, categories, suppliers (Inventory)
- Users, settings (Users)
- Real-time chart data (Analytics)

Navigate between dashboards and views - state is maintained!
