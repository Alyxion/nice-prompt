#!/usr/bin/env python3
"""
Sub Pages Demo - Multi-App Navigation with Persistent State

Demonstrates:
- ui.sub_pages for SPA-style client-side routing
- Fixed navigation drawer for app switching
- Persistent app.storage.client state across sub-pages
- Nested routing within sub-apps
"""

from nicegui import app, ui


# ============================================================================
# Sub-App: Dashboard
# ============================================================================
def dashboard_app():
    """Simple dashboard with live counter demonstrating persistent state."""
    ui.label('Dashboard').classes('text-2xl font-bold mb-4')
    
    # Counter persists across all sub-page navigation
    if 'visits' not in app.storage.client:
        app.storage.client['visits'] = 0
    app.storage.client['visits'] += 1
    
    with ui.card().classes('w-full max-w-md'):
        ui.label('Welcome to the Dashboard!')
        ui.label().bind_text_from(
            app.storage.client, 'visits',
            backward=lambda v: f'Page visits this session: {v}'
        )
        
        with ui.row().classes('mt-4'):
            ui.button('Increment Counter', 
                      on_click=lambda: app.storage.client.update(
                          counter=app.storage.client.get('counter', 0) + 1
                      ))
            ui.label().bind_text_from(
                app.storage.client, 'counter',
                backward=lambda c: f'Counter: {c or 0}'
            )


# ============================================================================
# Sub-App: Notes
# ============================================================================
def notes_app():
    """Notes app with persistent note storage."""
    ui.label('Notes').classes('text-2xl font-bold mb-4')
    
    if 'notes' not in app.storage.client:
        app.storage.client['notes'] = []
    
    note_input = ui.input('New note...').classes('w-full max-w-md')
    
    def add_note():
        if note_input.value:
            app.storage.client['notes'] = [
                *app.storage.client['notes'], 
                note_input.value
            ]
            note_input.value = ''
            notes_list.refresh()
    
    ui.button('Add Note', on_click=add_note).classes('mt-2')
    
    @ui.refreshable
    def notes_list():
        with ui.column().classes('mt-4 w-full max-w-md gap-2'):
            for i, note in enumerate(app.storage.client['notes']):
                with ui.card().classes('w-full'):
                    with ui.row().classes('w-full justify-between items-center'):
                        ui.label(note)
                        def delete_note(idx=i):
                            notes = list(app.storage.client['notes'])
                            notes.pop(idx)
                            app.storage.client['notes'] = notes
                            notes_list.refresh()
                        ui.button(icon='delete', on_click=delete_note).props('flat round size=sm')
            
            if not app.storage.client['notes']:
                ui.label('No notes yet. Add one above!').classes('text-gray-500')
    
    notes_list()


# ============================================================================
# Sub-App: Settings (with nested sub-pages)
# ============================================================================
def settings_app():
    """Settings app demonstrating nested sub-pages."""
    ui.label('Settings').classes('text-2xl font-bold mb-4')
    
    with ui.row().classes('gap-2 mb-4'):
        ui.button('General', on_click=lambda: ui.navigate.to('/settings'))
        ui.button('Appearance', on_click=lambda: ui.navigate.to('/settings/appearance'))
        ui.button('About', on_click=lambda: ui.navigate.to('/settings/about'))
    
    # Nested sub-pages within settings
    ui.sub_pages({
        '/': settings_general,
        '/appearance': settings_appearance,
        '/about': settings_about,
    })


def settings_general():
    with ui.card().classes('w-full max-w-md'):
        ui.label('General Settings').classes('text-lg font-semibold mb-2')
        
        if 'username' not in app.storage.client:
            app.storage.client['username'] = 'User'
        
        ui.input('Username').bind_value(app.storage.client, 'username')
        ui.checkbox('Enable notifications').bind_value(
            app.storage.client, 'notifications', forward=lambda x: x or False
        )


def settings_appearance():
    with ui.card().classes('w-full max-w-md'):
        ui.label('Appearance Settings').classes('text-lg font-semibold mb-2')
        
        dark = ui.dark_mode()
        ui.switch('Dark Mode').bind_value(dark)
        
        ui.select(
            ['Default', 'Compact', 'Comfortable'],
            label='Density',
            value='Default'
        ).classes('w-full')


def settings_about():
    with ui.card().classes('w-full max-w-md'):
        ui.label('About').classes('text-lg font-semibold mb-2')
        ui.label('Sub Pages Demo v1.0')
        ui.label('Built with NiceGUI').classes('text-gray-500')
        ui.link('View Documentation', 'https://nicegui.io/documentation/sub_pages')


# ============================================================================
# Sub-App: Timer
# ============================================================================
def timer_app():
    """Timer app showing that timers persist across navigation."""
    ui.label('Timer').classes('text-2xl font-bold mb-4')
    
    if 'timer_seconds' not in app.storage.client:
        app.storage.client['timer_seconds'] = 0
        app.storage.client['timer_running'] = False
    
    with ui.card().classes('w-full max-w-md text-center'):
        time_label = ui.label().classes('text-4xl font-mono')
        time_label.bind_text_from(
            app.storage.client, 'timer_seconds',
            backward=lambda s: f'{s // 60:02d}:{s % 60:02d}'
        )
        
        def tick():
            if app.storage.client.get('timer_running'):
                app.storage.client['timer_seconds'] += 1
        
        ui.timer(1.0, tick)
        
        with ui.row().classes('justify-center gap-2 mt-4'):
            def toggle_timer():
                app.storage.client['timer_running'] = not app.storage.client.get('timer_running')
            
            ui.button(
                on_click=toggle_timer
            ).bind_text_from(
                app.storage.client, 'timer_running',
                backward=lambda r: 'Pause' if r else 'Start'
            ).props('outline')
            
            def reset_timer():
                app.storage.client['timer_seconds'] = 0
                app.storage.client['timer_running'] = False
            
            ui.button('Reset', on_click=reset_timer).props('outline')
        
        ui.label('Timer continues running when you navigate away!').classes(
            'text-sm text-gray-500 mt-4'
        )


# ============================================================================
# Main Application Layout
# ============================================================================
NAV_ITEMS = [
    {'path': '/', 'icon': 'dashboard', 'label': 'Dashboard'},
    {'path': '/notes', 'icon': 'note', 'label': 'Notes'},
    {'path': '/timer', 'icon': 'timer', 'label': 'Timer'},
    {'path': '/settings', 'icon': 'settings', 'label': 'Settings'},
]


@ui.page('/')
def main():
    """Main SPA layout with fixed navigation drawer."""
    
    # Header
    with ui.header().classes('items-center bg-primary'):
        ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat round color=white')
        ui.label('Sub Pages Demo').classes('text-xl text-white ml-2')
        ui.space()
        # Show current username from persistent storage
        ui.label().bind_text_from(
            app.storage.client, 'username',
            backward=lambda u: f'👤 {u}' if u else ''
        ).classes('text-white')
    
    # Fixed Navigation Drawer
    with ui.left_drawer(value=True).classes('bg-gray-100') as drawer:
        ui.label('Navigation').classes('text-lg font-bold p-4')
        
        with ui.column().classes('w-full gap-1'):
            for item in NAV_ITEMS:
                with ui.item(on_click=lambda p=item['path']: ui.navigate.to(p)).classes('w-full'):
                    with ui.item_section().props('avatar'):
                        ui.icon(item['icon'])
                    with ui.item_section():
                        ui.item_label(item['label'])
        
        ui.separator().classes('my-4')
        
        # Show persistent state info
        with ui.column().classes('p-4 text-sm text-gray-600'):
            ui.label('Persistent State:')
            ui.label().bind_text_from(
                app.storage.client, 'counter',
                backward=lambda c: f'Counter: {c or 0}'
            )
            ui.label().bind_text_from(
                app.storage.client, 'notes',
                backward=lambda n: f'Notes: {len(n) if n else 0}'
            )
            ui.label().bind_text_from(
                app.storage.client, 'timer_seconds',
                backward=lambda s: f'Timer: {s // 60:02d}:{s % 60:02d}' if s else 'Timer: 00:00'
            )
    
    # Main Content Area with Sub Pages Router
    with ui.column().classes('w-full p-6'):
        ui.sub_pages({
            '/': dashboard_app,
            '/notes': notes_app,
            '/timer': timer_app,
            '/settings': settings_app,
        })


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(show=False, title='Sub Pages Demo', reload=True)
