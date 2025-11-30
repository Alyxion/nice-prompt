"""Sample NiceGUI Dashboard Application.

Demonstrates NiceGUI's charting and input control capabilities with an OO architecture.
"""

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from nicegui import app, ui


# --- Constants ---

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
PRODUCTS = ['Laptops', 'Phones', 'Tablets', 'Watches', 'Headphones']
REGIONS = ['North', 'South', 'East', 'West', 'Central']
PRODUCT_COLORS = {'Laptops': '#3b82f6', 'Phones': '#10b981', 'Tablets': '#f59e0b', 'Watches': '#ef4444', 'Headphones': '#8b5cf6'}
DATE_RANGE_CONFIG = {
    'Last 7 days': {'points': 7, 'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},
    'Last 30 days': {'points': 30, 'labels': [f'Day {i+1}' for i in range(30)]},
    'Last 3 months': {'points': 12, 'labels': [f'Week {i+1}' for i in range(12)]},
    'Last 12 months': {'points': 12, 'labels': MONTHS},
    'Year to date': {'points': 12, 'labels': MONTHS},
}


# --- Data Model ---

@dataclass
class DashboardData:
    """Per-user dashboard state with sample data."""
    
    revenue: float = 124500.0
    orders: int = 1847
    customers: int = 892
    conversion_rate: float = 3.24
    cpu_usage: float = 45.0
    memory_usage: float = 62.0
    
    monthly_sales: list = field(default_factory=lambda: [random.randint(8000, 15000) for _ in range(12)])
    monthly_orders: list = field(default_factory=lambda: [random.randint(100, 300) for _ in range(12)])
    product_sales: dict = field(default_factory=lambda: {p: random.randint(5000, 25000) for p in PRODUCTS})
    regional_metrics: dict = field(default_factory=lambda: {
        r: {'sales': random.randint(10000, 30000), 'marketing': random.randint(5000, 15000),
            'support': random.randint(3000, 10000), 'development': random.randint(8000, 20000),
            'operations': random.randint(4000, 12000)} for r in REGIONS
    })
    
    # Filter state
    selected_regions: list = field(default_factory=lambda: REGIONS.copy())
    selected_products: list = field(default_factory=lambda: PRODUCTS.copy())
    date_range: str = 'Last 12 months'
    show_comparison: bool = False
    search_text: str = ''
    alert_threshold: int = 80
    refresh_interval: int = 5
    chart_type: str = 'line'
    
    @classmethod
    def current(cls) -> 'DashboardData':
        if 'dashboard_data' not in app.storage.client:
            app.storage.client['dashboard_data'] = cls()
        return app.storage.client['dashboard_data']


# --- Dashboard UI ---

class Dashboard:
    """Main dashboard UI class."""
    
    def __init__(self):
        self.data = DashboardData.current()
        self.charts: dict[str, ui.echart | None] = {'line': None, 'bar': None, 'pie': None}
        self.kpi_labels: dict[str, ui.label | None] = {}
        self.cpu_gauge: ui.echart | None = None
        self.mem_gauge: ui.echart | None = None
        self.settings_dialog: ui.dialog | None = None
    
    @classmethod
    def current(cls) -> 'Dashboard':
        if 'dashboard' not in app.storage.client:
            app.storage.client['dashboard'] = cls()
        return app.storage.client['dashboard']
    
    # --- Data Methods ---
    
    def get_filtered_data(self) -> tuple[list, list, list, dict]:
        """Get data filtered by current selections."""
        config = DATE_RANGE_CONFIG.get(self.data.date_range, DATE_RANGE_CONFIG['Last 12 months'])
        points, labels = config['points'], config['labels']
        
        # Generate data based on date range (seeded for consistency)
        rnd = random.Random()
        if self.data.date_range == 'Last 7 days':
            rnd.seed(7)
            base_sales = [rnd.randint(800, 1500) for _ in range(points)]
            base_orders = [rnd.randint(10, 40) for _ in range(points)]
        elif self.data.date_range == 'Last 30 days':
            rnd.seed(30)
            base_sales = [rnd.randint(600, 1200) for _ in range(points)]
            base_orders = [rnd.randint(8, 30) for _ in range(points)]
        elif self.data.date_range == 'Last 3 months':
            rnd.seed(90)
            base_sales = [rnd.randint(2000, 4000) for _ in range(points)]
            base_orders = [rnd.randint(25, 80) for _ in range(points)]
        else:  # Last 12 months, Year to date
            base_sales = self.data.monthly_sales.copy()
            base_orders = self.data.monthly_orders.copy()
        
        region_scale = len(self.data.selected_regions) / len(REGIONS) if self.data.selected_regions else 0
        product_scale = len(self.data.selected_products) / len(PRODUCTS) if self.data.selected_products else 0
        combined_scale = region_scale * product_scale
        
        sales = [int(s * combined_scale) for s in base_sales]
        orders = [int(o * combined_scale) for o in base_orders]
        
        filtered_products = {}
        for k, v in self.data.product_sales.items():
            if k in self.data.selected_products:
                if self.data.search_text and self.data.search_text not in k.lower():
                    continue
                filtered_products[k] = int(v * region_scale)
        
        return labels, sales, orders, filtered_products
    
    def get_scale(self) -> float:
        region_scale = len(self.data.selected_regions) / len(REGIONS) if self.data.selected_regions else 0
        product_scale = len(self.data.selected_products) / len(PRODUCTS) if self.data.selected_products else 0
        return region_scale * product_scale
    
    # --- Chart Creation ---
    
    def _line_series(self) -> list:
        labels, sales, orders, _ = self.get_filtered_data()
        series = [
            {'name': 'Revenue', 'type': 'line', 'smooth': True, 'areaStyle': {'opacity': 0.3},
             'data': sales, 'itemStyle': {'color': '#3b82f6'}},
            {'name': 'Orders', 'type': 'line', 'smooth': True, 'yAxisIndex': 1,
             'data': orders, 'itemStyle': {'color': '#10b981'}},
        ]
        if self.data.show_comparison:
            rnd = random.Random(42)
            series.extend([
                {'name': 'Revenue (LY)', 'type': 'line', 'smooth': True, 'lineStyle': {'type': 'dashed'},
                 'data': [int(s * rnd.uniform(0.80, 0.95)) for s in sales], 'itemStyle': {'color': '#60a5fa'}},
                {'name': 'Orders (LY)', 'type': 'line', 'smooth': True, 'yAxisIndex': 1, 'lineStyle': {'type': 'dashed'},
                 'data': [int(o * rnd.uniform(0.80, 0.95)) for o in orders], 'itemStyle': {'color': '#34d399'}},
            ])
        return series
    
    def _line_legend(self) -> list:
        legend = ['Revenue', 'Orders']
        if self.data.show_comparison:
            legend.extend(['Revenue (LY)', 'Orders (LY)'])
        return legend
    
    def _create_line_chart(self) -> ui.echart:
        labels, _, _, _ = self.get_filtered_data()
        return ui.echart({
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': self._line_legend(), 'top': 5},
            'grid': {'left': 50, 'right': 20, 'top': 40, 'bottom': 30},
            'xAxis': {'type': 'category', 'data': labels},
            'yAxis': [{'type': 'value', 'name': 'Revenue ($)', 'position': 'left'},
                      {'type': 'value', 'name': 'Orders', 'position': 'right'}],
            'series': self._line_series(),
        }).classes('w-full h-64')
    
    def _create_bar_chart(self) -> ui.echart:
        _, _, _, products = self.get_filtered_data()
        return ui.echart({
            'tooltip': {'trigger': 'axis'},
            'grid': {'left': 50, 'right': 20, 'top': 20, 'bottom': 30},
            'xAxis': {'type': 'category', 'data': list(products.keys())},
            'yAxis': {'type': 'value', 'name': 'Sales ($)'},
            'series': [{'type': 'bar', 'barWidth': '60%',
                        'data': [{'value': v, 'itemStyle': {'color': PRODUCT_COLORS.get(k, '#888')}} for k, v in products.items()]}],
        }).classes('w-full h-64')
    
    def _create_pie_chart(self) -> ui.echart:
        _, _, _, products = self.get_filtered_data()
        return ui.echart({
            'tooltip': {'trigger': 'item', 'formatter': '{b}: ${c} ({d}%)'},
            'legend': {'orient': 'vertical', 'right': 10, 'top': 'center'},
            'series': [{'type': 'pie', 'radius': ['40%', '70%'], 'center': ['40%', '50%'],
                        'itemStyle': {'borderRadius': 8, 'borderColor': '#1e293b', 'borderWidth': 2},
                        'label': {'show': False}, 'emphasis': {'label': {'show': True, 'fontSize': 14}},
                        'data': [{'value': v, 'name': k} for k, v in products.items()]}],
        }).classes('w-full h-64')
    
    def _create_gauge_chart(self, value: float, title: str, color: str) -> ui.echart:
        return ui.echart({
            'series': [{'type': 'gauge', 'startAngle': 200, 'endAngle': -20, 'min': 0, 'max': 100,
                        'itemStyle': {'color': color}, 'progress': {'show': True, 'width': 20},
                        'pointer': {'show': False}, 'axisLine': {'lineStyle': {'width': 20, 'color': [[1, '#334155']]}},
                        'axisTick': {'show': False}, 'splitLine': {'show': False}, 'axisLabel': {'show': False},
                        'title': {'show': True, 'offsetCenter': [0, '70%'], 'fontSize': 14, 'color': '#94a3b8'},
                        'detail': {'valueAnimation': True, 'fontSize': 28, 'fontWeight': 'bold',
                                   'offsetCenter': [0, '0%'], 'formatter': '{value}%', 'color': '#f8fafc'},
                        'data': [{'value': value, 'name': title}]}],
        }).classes('w-full h-48')
    
    def _create_radar_chart(self) -> ui.echart:
        indicators = [{'name': n, 'max': m} for n, m in [('Sales', 35000), ('Marketing', 20000),
                      ('Support', 15000), ('Development', 25000), ('Operations', 15000)]]
        series_data = [{'name': r, 'value': list(m.values())} for r, m in list(self.data.regional_metrics.items())[:3]]
        return ui.echart({
            'tooltip': {'trigger': 'item'},
            'legend': {'data': [s['name'] for s in series_data], 'top': 5},
            'radar': {'indicator': indicators, 'center': ['50%', '55%'], 'radius': '65%'},
            'series': [{'type': 'radar', 'data': series_data, 'areaStyle': {'opacity': 0.2}}],
        }).classes('w-full h-64')
    
    def _create_heatmap_chart(self) -> ui.echart:
        rnd = random.Random(123)
        return ui.echart({
            'tooltip': {'position': 'top'},
            'grid': {'left': 50, 'right': 20, 'top': 20, 'bottom': 50},
            'xAxis': {'type': 'category', 'data': [f'{h}:00' for h in range(24)]},
            'yAxis': {'type': 'category', 'data': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},
            'visualMap': {'min': 0, 'max': 100, 'orient': 'horizontal', 'left': 'center', 'bottom': 0,
                          'inRange': {'color': ['#1e3a5f', '#3b82f6', '#60a5fa']}},
            'series': [{'type': 'heatmap', 'data': [[i, j, rnd.randint(0, 100)] for i in range(7) for j in range(24)]}],
        }).classes('w-full h-64')
    
    def _create_scatter_chart(self) -> ui.echart:
        rnd = random.Random(456)
        return ui.echart({
            'tooltip': {'trigger': 'item'},
            'legend': {'data': ['Enterprise', 'SMB', 'Consumer'], 'top': 5},
            'grid': {'left': 50, 'right': 20, 'top': 40, 'bottom': 30},
            'xAxis': {'type': 'value', 'name': 'Engagement'},
            'yAxis': {'type': 'value', 'name': 'Satisfaction'},
            'series': [
                {'name': 'Enterprise', 'type': 'scatter', 'symbolSize': 10,
                 'data': [[rnd.gauss(50, 15), rnd.gauss(50, 15)] for _ in range(50)]},
                {'name': 'SMB', 'type': 'scatter', 'symbolSize': 10,
                 'data': [[rnd.gauss(70, 10), rnd.gauss(30, 10)] for _ in range(40)]},
                {'name': 'Consumer', 'type': 'scatter', 'symbolSize': 10,
                 'data': [[rnd.gauss(30, 10), rnd.gauss(70, 10)] for _ in range(30)]},
            ],
        }).classes('w-full h-64')
    
    def _create_candlestick_chart(self) -> ui.echart:
        dates = [(datetime.now() - timedelta(days=30-i)).strftime('%m/%d') for i in range(30)]
        data, price = [], 100.0
        for _ in range(30):
            close = price + random.uniform(-5, 5)
            low = min(price, close) - random.uniform(0, 3)
            high = max(price, close) + random.uniform(0, 3)
            data.append([price, close, low, high])
            price = close
        return ui.echart({
            'tooltip': {'trigger': 'axis', 'axisPointer': {'type': 'cross'}},
            'grid': {'left': 50, 'right': 20, 'top': 20, 'bottom': 30},
            'xAxis': {'type': 'category', 'data': dates},
            'yAxis': {'type': 'value', 'scale': True},
            'series': [{'type': 'candlestick', 'data': data,
                        'itemStyle': {'color': '#10b981', 'color0': '#ef4444', 'borderColor': '#10b981', 'borderColor0': '#ef4444'}}],
        }).classes('w-full h-64')
    
    # --- Update Methods ---
    
    def update_kpis(self) -> None:
        scale = self.get_scale()
        if self.kpi_labels.get('revenue'):
            self.kpi_labels['revenue'].set_text(f'${self.data.revenue * scale:,.0f}')
        if self.kpi_labels.get('orders'):
            self.kpi_labels['orders'].set_text(f'{int(self.data.orders * scale):,}')
        if self.kpi_labels.get('customers'):
            self.kpi_labels['customers'].set_text(f'{int(self.data.customers * scale):,}')
    
    def update_charts(self) -> None:
        self.update_kpis()
        if self.charts['line']:
            labels, _, _, _ = self.get_filtered_data()
            self.charts['line'].options['xAxis']['data'] = labels
            self.charts['line'].options['legend']['data'] = self._line_legend()
            self.charts['line'].options['series'] = self._line_series()
            self.charts['line'].update()
        if self.charts['bar']:
            _, _, _, products = self.get_filtered_data()
            self.charts['bar'].options['xAxis']['data'] = list(products.keys())
            self.charts['bar'].options['series'][0]['data'] = [
                {'value': v, 'itemStyle': {'color': PRODUCT_COLORS.get(k, '#888')}} for k, v in products.items()]
            self.charts['bar'].update()
        if self.charts['pie']:
            _, _, _, products = self.get_filtered_data()
            self.charts['pie'].options['series'][0]['data'] = [{'value': v, 'name': k} for k, v in products.items()]
            self.charts['pie'].update()
    
    def update_metrics(self) -> None:
        self.data.cpu_usage = max(10, min(95, self.data.cpu_usage + random.uniform(-5, 5)))
        self.data.memory_usage = max(20, min(90, self.data.memory_usage + random.uniform(-3, 3)))
        if self.cpu_gauge:
            self.cpu_gauge.options['series'][0]['data'][0]['value'] = round(self.data.cpu_usage, 1)
            self.cpu_gauge.update()
        if self.mem_gauge:
            self.mem_gauge.options['series'][0]['data'][0]['value'] = round(self.data.memory_usage, 1)
            self.mem_gauge.update()
    
    # --- Event Handlers ---
    
    def toggle_product(self, product: str) -> None:
        if product in self.data.selected_products:
            self.data.selected_products.remove(product)
        else:
            self.data.selected_products.append(product)
        self.update_charts()
    
    def on_regions_change(self, e) -> None:
        self.data.selected_regions = e.value if e.value else []
        self.update_charts()
    
    def on_date_range_change(self, e) -> None:
        self.data.date_range = e.value
        self.update_charts()
    
    def on_comparison_change(self, e) -> None:
        self.data.show_comparison = e.value
        self.update_charts()
    
    def on_search_change(self, e) -> None:
        self.data.search_text = e.value.lower() if e.value else ''
        self.update_charts()
    
    # --- UI Building ---
    
    def build(self) -> None:
        ui.dark_mode().enable()
        ui.add_head_html('''<style>
            body { background-color: #0f172a !important; }
            .nicegui-content { background-color: #0f172a !important; }
            .q-card { background-color: #1e293b !important; border: 1px solid #334155; }
        </style>''')
        
        self._build_settings_dialog()
        
        with ui.column().classes('w-full p-6 gap-6'):
            self._build_header()
            self._build_filters()
            self._build_kpis()
            self._build_charts()
        
        ui.timer(2.0, self.update_metrics)
    
    def _build_settings_dialog(self) -> None:
        with ui.dialog() as self.settings_dialog, ui.card().classes('p-6 w-96'):
            ui.label('Dashboard Settings').classes('text-xl font-bold text-white mb-4')
            with ui.column().classes('w-full gap-4'):
                ui.label('Alert Threshold (%)').classes('text-slate-400 text-sm')
                ui.slider(min=50, max=100, step=5).bind_value(self.data, 'alert_threshold').props('label-always')
                ui.label('Auto-refresh Interval (seconds)').classes('text-slate-400 text-sm')
                ui.number(min=1, max=60, step=1).bind_value(self.data, 'refresh_interval').props('dense outlined dark')
                ui.label('Default Chart Type').classes('text-slate-400 text-sm')
                ui.radio(['line', 'bar', 'area'], value=self.data.chart_type).bind_value(self.data, 'chart_type').props('inline')
                ui.label('Accent Color').classes('text-slate-400 text-sm')
                ui.color_input(value='#3b82f6').props('dense')
                ui.separator()
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=self.settings_dialog.close).props('flat')
                    ui.button('Apply', on_click=lambda: (self.settings_dialog.close(), ui.notify('Settings applied!'))).props('color=primary')
    
    def _build_header(self) -> None:
        with ui.row().classes('w-full justify-between items-center'):
            ui.label('Analytics Dashboard').classes('text-3xl font-bold text-white')
            with ui.row().classes('gap-4 items-center'):
                ui.label().classes('text-slate-400').bind_text_from(
                    globals(), '__name__', lambda _: datetime.now().strftime('%B %d, %Y • %H:%M'))
                ui.button(icon='refresh', on_click=lambda: ui.notify('Data refreshed!')).props('flat round color=white')
                ui.button(icon='settings', on_click=lambda: self.settings_dialog.open()).props('flat round color=white')
    
    def _build_filters(self) -> None:
        with ui.card().classes('w-full p-4'):
            with ui.row().classes('w-full gap-6 items-center flex-wrap'):
                with ui.column().classes('gap-1'):
                    ui.label('Regions').classes('text-slate-400 text-xs')
                    ui.select(REGIONS, value=self.data.selected_regions, multiple=True,
                              on_change=self.on_regions_change).props('dense outlined dark').classes('w-40')
                with ui.column().classes('gap-1'):
                    ui.label('Date Range').classes('text-slate-400 text-xs')
                    ui.select(list(DATE_RANGE_CONFIG.keys()), value=self.data.date_range,
                              on_change=self.on_date_range_change).props('dense outlined dark').classes('w-40')
                with ui.column().classes('gap-1 flex-1'):
                    ui.label('Products').classes('text-slate-400 text-xs')
                    with ui.row().classes('gap-2'):
                        for product in PRODUCTS:
                            ui.chip(product, selectable=True, selected=product in self.data.selected_products,
                                    on_click=lambda e, p=product: self.toggle_product(p)).props('dark outline')
                with ui.column().classes('gap-1'):
                    ui.label('Options').classes('text-slate-400 text-xs')
                    ui.switch('Compare YoY', value=self.data.show_comparison, on_change=self.on_comparison_change).props('dark')
                with ui.column().classes('gap-1'):
                    ui.label('Search Products').classes('text-slate-400 text-xs')
                    ui.input(placeholder='e.g. laptop...', value=self.data.search_text,
                             on_change=self.on_search_change).props('dense outlined dark clearable').classes('w-40')
    
    def _build_kpis(self) -> None:
        with ui.row().classes('w-full gap-4'):
            scale = self.get_scale()
            for title, value, change, icon, color, key in [
                ('Revenue', f'${self.data.revenue * scale:,.0f}', '+12.5%', 'trending_up', 'text-blue-400', 'revenue'),
                ('Orders', f'{int(self.data.orders * scale):,}', '+8.2%', 'shopping_cart', 'text-green-400', 'orders'),
                ('Customers', f'{int(self.data.customers * scale):,}', '+15.3%', 'people', 'text-purple-400', 'customers'),
                ('Conversion', f'{self.data.conversion_rate}%', '+0.8%', 'speed', 'text-amber-400', 'conversion'),
            ]:
                with ui.card().classes('flex-1 p-4'):
                    with ui.row().classes('justify-between items-start'):
                        with ui.column().classes('gap-1'):
                            ui.label(title).classes('text-slate-400 text-sm')
                            self.kpi_labels[key] = ui.label(value).classes('text-white text-2xl font-bold')
                            ui.label(change).classes('text-green-400 text-sm')
                        ui.icon(icon).classes(f'{color} text-3xl')
    
    def _build_charts(self) -> None:
        # Row 1
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 p-4'):
                ui.label('Revenue & Orders Trend').classes('text-white font-semibold mb-2')
                self.charts['line'] = self._create_line_chart()
            with ui.card().classes('flex-1 p-4'):
                ui.label('Product Sales').classes('text-white font-semibold mb-2')
                self.charts['bar'] = self._create_bar_chart()
        # Row 2
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('w-1/3 p-4'):
                ui.label('Sales Distribution').classes('text-white font-semibold mb-2')
                self.charts['pie'] = self._create_pie_chart()
            with ui.card().classes('w-1/3 p-4'):
                ui.label('Regional Performance').classes('text-white font-semibold mb-2')
                self._create_radar_chart()
            with ui.card().classes('w-1/3 p-4'):
                ui.label('System Health').classes('text-white font-semibold mb-2')
                with ui.row().classes('w-full'):
                    with ui.column().classes('flex-1'):
                        self.cpu_gauge = self._create_gauge_chart(self.data.cpu_usage, 'CPU', '#3b82f6')
                    with ui.column().classes('flex-1'):
                        self.mem_gauge = self._create_gauge_chart(self.data.memory_usage, 'Memory', '#10b981')
        # Row 3
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 p-4'):
                ui.label('Weekly Activity').classes('text-white font-semibold mb-2')
                self._create_heatmap_chart()
            with ui.card().classes('flex-1 p-4'):
                ui.label('Customer Segments').classes('text-white font-semibold mb-2')
                self._create_scatter_chart()
        # Row 4
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('flex-1 p-4'):
                ui.label('Stock Performance').classes('text-white font-semibold mb-2')
                self._create_candlestick_chart()


@ui.page('/')
def index():
    Dashboard.current().build()


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(show=False, title='Analytics Dashboard')
