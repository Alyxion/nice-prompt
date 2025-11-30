"""Overview view with key metrics and charts."""
import asyncio
import random
from nicegui import ui


class OverviewView:
    async def build(self) -> None:
        container = ui.column().classes('w-full')
        
        with container:
            with ui.row().classes('w-full justify-center py-8'):
                ui.spinner(size='lg')
                ui.label('Loading analytics data...')
        
        await asyncio.sleep(0.5)
        container.clear()
        
        with container:
            with ui.row().classes('w-full gap-4 flex-wrap'):
                self._metric_card('Total Revenue', '$124,500', 'trending_up', '+12.5%', 'green')
                self._metric_card('Active Users', '8,420', 'people', '+5.2%', 'blue')
                self._metric_card('Conversion Rate', '3.24%', 'show_chart', '-0.8%', 'red')
                self._metric_card('Avg. Session', '4m 32s', 'timer', '+1.1%', 'green')
            
            with ui.row().classes('w-full gap-4 mt-6 flex-wrap'):
                with ui.card().classes('flex-1 min-w-80'):
                    ui.label('Revenue Trend').classes('font-semibold mb-2')
                    self._revenue_chart()
                with ui.card().classes('min-w-96'):
                    ui.label('Traffic Sources').classes('font-semibold mb-2')
                    self._traffic_pie()
    
    def _metric_card(self, title: str, value: str, icon: str, change: str, color: str) -> None:
        with ui.card().classes('w-56'):
            with ui.row().classes('items-center justify-between'):
                ui.icon(icon).classes(f'text-2xl text-{color}-500')
                ui.label(change).classes(f'text-sm text-{color}-500')
            ui.label(value).classes('text-2xl font-bold mt-2')
            ui.label(title).classes('text-slate-500 text-sm')
    
    def _revenue_chart(self) -> None:
        data = [random.randint(80, 150) for _ in range(12)]
        ui.echart({
            'xAxis': {'type': 'category', 'data': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                                                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']},
            'yAxis': {'type': 'value'},
            'series': [{'data': data, 'type': 'line', 'smooth': True, 'areaStyle': {'opacity': 0.3}}],
        }).classes('w-full h-64')
    
    def _traffic_pie(self) -> None:
        ui.echart({
            'tooltip': {'trigger': 'item'},
            'series': [{
                'type': 'pie',
                'radius': ['30%', '50%'],
                'center': ['50%', '50%'],
                'label': {'show': True, 'formatter': '{b}'},
                'labelLine': {'show': True},
                'data': [
                    {'value': 45, 'name': 'Organic'},
                    {'value': 25, 'name': 'Direct'},
                    {'value': 20, 'name': 'Referral'},
                    {'value': 10, 'name': 'Social'},
                ]
            }],
        }).classes('w-full h-80')
