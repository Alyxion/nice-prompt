"""Reports view for generating and viewing reports."""
from datetime import datetime
from nicegui import ui


class ReportsView:
    async def build(self) -> None:
        rows = [
            {'name': 'Revenue Report - Q4', 'date': '2024-01-15', 'status': 'Ready'},
            {'name': 'User Activity - December', 'date': '2024-01-10', 'status': 'Ready'},
            {'name': 'Conversion Funnel', 'date': '2024-01-08', 'status': 'Processing'},
        ]
        
        with ui.column().classes('w-full'):
            ui.label('Generate Reports').classes('text-xl font-semibold mb-4')
            
            with ui.card().classes('w-full'):
                with ui.row().classes('gap-4 items-end flex-wrap'):
                    report_type = ui.select(
                        ['Revenue Report', 'User Activity', 'Conversion Funnel', 'Traffic Analysis'],
                        label='Report Type', value='Revenue Report'
                    ).classes('min-w-48')
                    time_period = ui.select(
                        ['Last 7 Days', 'Last 30 Days', 'Last Quarter', 'Last Year'],
                        label='Time Period', value='Last 30 Days'
                    ).classes('min-w-48')
                    
                    def generate_report():
                        new_report = {
                            'name': f'{report_type.value} - {time_period.value}',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'status': 'Processing'
                        }
                        rows.insert(0, new_report)
                        table.update_rows(rows)
                        ui.notify(f'Generating {report_type.value}...', type='positive')
                    
                    ui.button('Generate', icon='play_arrow', on_click=generate_report).props('color=primary')
            
            ui.label('Recent Reports').classes('text-lg font-semibold mt-8 mb-4')
            
            with ui.card().classes('w-full'):
                columns = [
                    {'name': 'name', 'label': 'Report Name', 'field': 'name', 'align': 'left'},
                    {'name': 'date', 'label': 'Generated', 'field': 'date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ]
                table = ui.table(columns=columns, rows=rows).classes('w-full')
