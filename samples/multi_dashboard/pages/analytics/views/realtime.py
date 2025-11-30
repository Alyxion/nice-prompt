"""Real-time analytics view with live updates."""
import random
import time
from nicegui import ui


class RealTimeView:
    async def build(self) -> None:
        with ui.column().classes('w-full'):
            ui.label('Real-Time Analytics').classes('text-xl font-semibold mb-4')
            
            with ui.row().classes('w-full gap-4 flex-wrap'):
                with ui.card().classes('flex-1 min-w-48 text-center'):
                    ui.label('Active Users Now').classes('text-slate-500')
                    active_users = ui.label('0').classes('text-4xl font-bold text-indigo-500')
                with ui.card().classes('flex-1 min-w-48 text-center'):
                    ui.label('Page Views / min').classes('text-slate-500')
                    page_views = ui.label('0').classes('text-4xl font-bold text-green-500')
                with ui.card().classes('flex-1 min-w-48 text-center'):
                    ui.label('Events / min').classes('text-slate-500')
                    events = ui.label('0').classes('text-4xl font-bold text-blue-500')
            
            with ui.card().classes('w-full mt-4'):
                ui.label('Live Activity').classes('font-semibold mb-2')
                chart_data = {'timestamps': [], 'values': []}
                chart = ui.echart({
                    'xAxis': {'type': 'category', 'data': []},
                    'yAxis': {'type': 'value', 'min': 0, 'max': 100},
                    'series': [{'data': [], 'type': 'line', 'smooth': True}],
                    'animation': False,
                }).classes('w-full h-64')
        
        def update_realtime():
            active_users.text = str(random.randint(150, 300))
            page_views.text = str(random.randint(50, 150))
            events.text = str(random.randint(200, 500))
            
            chart_data['timestamps'].append(time.strftime('%H:%M:%S'))
            chart_data['values'].append(random.randint(20, 80))
            if len(chart_data['timestamps']) > 20:
                chart_data['timestamps'] = chart_data['timestamps'][-20:]
                chart_data['values'] = chart_data['values'][-20:]
            
            chart.options['xAxis']['data'] = chart_data['timestamps']
            chart.options['series'][0]['data'] = chart_data['values']
            chart.update()
        
        ui.timer(1.0, update_realtime)
        update_realtime()
