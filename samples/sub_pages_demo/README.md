# Sub Pages Demo - Multi-App Navigation

![Screenshot](screenshot.jpg)

A demonstration of NiceGUI's `ui.sub_pages` for building Single Page Applications (SPAs) with persistent client state.

## Features

- **Fixed Navigation Drawer**: Always-visible sidebar for switching between apps
- **Persistent State**: `app.storage.client` maintains state across all sub-pages
- **Multiple Sub-Apps**:
  - **Dashboard**: Visit counter and global counter
  - **Notes**: Add/delete notes that persist during session
  - **Timer**: Stopwatch that keeps running when navigating away
  - **Settings**: Nested sub-pages for different setting categories

## Key Concepts Demonstrated

### 1. Single Page Route
```python
@ui.page('/')
def main():
    # No catch-all needed - ui.sub_pages handles client-side routing
    ...
```

### 2. Sub Pages Router
```python
ui.sub_pages({
    '/': dashboard_app,
    '/notes': notes_app,
    '/timer': timer_app,
    '/settings': settings_app,
})
```

### 3. Nested Sub Pages
The Settings app contains its own nested router:
```python
def settings_app():
    ui.sub_pages({
        '/': settings_general,
        '/appearance': settings_appearance,
        '/about': settings_about,
    })
```

### 4. Persistent Client State
State in `app.storage.client` survives navigation:
```python
# Initialize once
if 'counter' not in app.storage.client:
    app.storage.client['counter'] = 0

# Update anywhere
app.storage.client['counter'] += 1

# Bind to UI
ui.label().bind_text_from(app.storage.client, 'counter')
```

### 5. Navigation
```python
ui.button('Go to Notes', on_click=lambda: ui.navigate.to('/notes'))
```

## Running

```bash
cd samples/sub_pages_demo
python main.py
```

Then open http://localhost:8080 in your browser.

## What to Try

1. **Counter Persistence**: Increment the counter on Dashboard, navigate away, come back - it's still there
2. **Timer Persistence**: Start the timer, switch to Notes, come back - timer kept running
3. **Notes**: Add some notes, navigate around - they persist
4. **Nested Settings**: Click through General → Appearance → About within Settings
5. **Drawer State Display**: Watch the drawer footer update as you interact with apps
