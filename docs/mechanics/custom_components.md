# Custom JavaScript/Vue Components

NiceGUI allows you to create custom UI components that combine Python and JavaScript/Vue.js. This enables wrapping existing JavaScript libraries or creating entirely custom interactive elements.

## Architecture Overview

NiceGUI components consist of:
1. **Python class** - Extends `Element`, handles server-side logic
2. **JavaScript/Vue module** - Handles client-side rendering and interaction
3. **Communication layer** - Props, events, and method calls between Python and JS

## Creating a Custom Component

### Basic Structure

```
my_component/
├── __init__.py           # Export the component
├── my_component.py       # Python class
└── my_component.js       # Vue component definition
```

### Python Side

Subclass `Element` and specify the JavaScript component file.

**Important**: The `component=` path is **relative to the Python file**, not the project root. Place the `.js` file in the same directory as the Python class, or use a relative path like `component='js/counter.js'`.

```python
from nicegui.element import Element

class MyCounter(Element, component='counter.js'):
    """A simple counter component."""
    
    def __init__(self, initial_value: int = 0) -> None:
        super().__init__()
        # Set props that will be passed to the Vue component
        self._props['count'] = initial_value
    
    def increment(self) -> None:
        """Increment the counter from Python."""
        self._props['count'] += 1
        self.update()  # Push changes to client
```

### JavaScript Side (Vue Component)

Create a Vue component module:

```javascript
// counter.js
export default {
  // HTML template
  template: `
    <div>
      <span>Count: {{ count }}</span>
      <button @click="increment">+</button>
    </div>
  `,
  
  // Props received from Python
  props: {
    count: Number,
  },
  
  // Component lifecycle
  mounted() {
    console.log('Component mounted');
  },
  
  unmounted() {
    console.log('Component unmounted');
  },
  
  // Methods callable from template or Python
  methods: {
    increment() {
      // Emit event to Python
      this.$emit('increment', this.count + 1);
    },
  },
};
```

## Class Registration Options

The `Element` subclass accepts several class-level parameters:

```python
class MyComponent(Element,
    component='my_component.js',           # Vue component file
    dependencies=['lib1.js', 'lib2.js'],   # Additional JS libraries
    esm={'module-name': 'dist'},           # ESM module mapping
    default_classes='my-component',        # Default CSS classes
    default_style='color: blue',           # Default inline styles
    default_props='outlined',              # Default Quasar props
):
    pass
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `component` | Path to the Vue component `.js` file (relative to Python file) |
| `dependencies` | List of additional JS/CSS files to load |
| `esm` | Dict mapping ESM module names to local paths for bundled libraries |
| `default_classes` | Default CSS classes applied to all instances |
| `default_style` | Default inline styles |
| `default_props` | Default Quasar props |

## Props (Python → JavaScript)

Props are the primary way to pass data from Python to JavaScript.

### Setting Props

```python
class MyComponent(Element, component='my_component.js'):
    def __init__(self, title: str, items: list) -> None:
        super().__init__()
        self._props['title'] = title
        self._props['items'] = items
    
    def set_title(self, title: str) -> None:
        self._props['title'] = title
        self.update()  # Required to push changes
```

### Receiving Props in JavaScript

```javascript
export default {
  props: {
    title: String,
    items: Array,
  },
  template: `<div>{{ title }}</div>`,
};
```

### Dynamic Props (JavaScript Expressions)

Props starting with `:` are evaluated as JavaScript:

```python
self._props[':onClick'] = 'console.log("clicked")'
self._props[':data'] = '{"key": "value"}'
```

## Events (JavaScript → Python)

Events allow the JavaScript component to communicate back to Python.

### Emitting Events from JavaScript

```javascript
methods: {
  handleClick(data) {
    // Emit event to Python
    this.$emit('my-event', { value: data });
  },
},
```

### Handling Events in Python

```python
class MyComponent(Element, component='my_component.js'):
    def __init__(self) -> None:
        super().__init__()
        # Register event handler
        self.on('my-event', self._handle_event)
    
    def _handle_event(self, e) -> None:
        print(f'Received: {e.args}')
```

### Custom Event Arguments

Define typed event arguments by inheriting from `UiEventArguments`:

```python
from dataclasses import dataclass
from nicegui.dataclasses import KWONLY_SLOTS
from nicegui.events import UiEventArguments

@dataclass(**KWONLY_SLOTS)
class MyEventArgs(UiEventArguments):
    """Custom event arguments.
    
    Inherits sender and client from UiEventArguments.
    """
    data: dict
```

### Event Handler Signature

```python
from nicegui.events import GenericEventArguments, Handler, handle_event
from typing_extensions import Self

def on_custom_event(self, callback: Handler[MyEventArgs]) -> Self:
    """Register a handler for custom events."""
    def handler(e: GenericEventArguments) -> None:
        args = MyEventArgs(sender=self, client=self.client, data=e.args)
        handle_event(callback, args)
    self.on('custom-event', handler)
    return self
```

## Methods (Python → JavaScript)

Call JavaScript methods from Python using `run_method()`.

### Python Side

```python
class MyComponent(Element, component='my_component.js'):
    def focus(self) -> AwaitableResponse:
        """Focus the component."""
        return self.run_method('focus')
    
    async def get_value(self) -> str:
        """Get value from JavaScript (async)."""
        return await self.run_method('getValue')
    
    def set_data(self, data: dict) -> None:
        """Call JS method with arguments."""
        self.run_method('setData', data)
```

### JavaScript Side

```javascript
methods: {
  focus() {
    this.$el.focus();
  },
  getValue() {
    return this.internalValue;
  },
  setData(data) {
    this.data = data;
  },
},
```

### Awaiting Results

`run_method()` returns an `AwaitableResponse`:

```python
# Fire and forget
self.run_method('doSomething')

# Wait for result
result = await self.run_method('getValue', timeout=2.0)
```

## JavaScript → Python Method Calls

Use `ui.run_javascript()` or emit events for complex communication:

```javascript
// In Vue component
methods: {
  async callPython() {
    // Emit event that Python handles
    this.$emit('request-data', { query: 'test' });
  },
},
```

## Vue Component Lifecycle

### Lifecycle Hooks

```javascript
export default {
  template: '<div ref="container"></div>',
  
  // Before component is mounted
  beforeMount() {
    // Initialize state
  },
  
  // After component is mounted to DOM
  mounted() {
    // Access DOM: this.$el, this.$refs.container
    // Initialize third-party libraries
    this.chart = new Chart(this.$refs.container);
  },
  
  // Before component is updated
  beforeUpdate() {
    // Save state before re-render
  },
  
  // After component is updated
  updated() {
    // React to prop changes
  },
  
  // Before component is unmounted
  beforeUnmount() {
    // Start cleanup
  },
  
  // After component is unmounted
  unmounted() {
    // Final cleanup
    this.chart?.destroy();
  },
};
```

### Watching Props

```javascript
export default {
  props: {
    data: Object,
  },
  watch: {
    data: {
      handler(newVal, oldVal) {
        this.updateChart(newVal);
      },
      deep: true,  // Watch nested changes
    },
  },
};
```

## Loading External Libraries

### ESM Modules

For bundled npm packages:

```python
class MyChart(Element,
    component='chart.js',
    esm={'my-chart-lib': 'dist'}  # Maps import name to local path
):
    pass
```

```javascript
// chart.js
import { Chart } from 'my-chart-lib';

export default {
  mounted() {
    this.chart = new Chart(this.$el);
  },
};
```

### Adding Resources

For CSS and other static files:

```python
from pathlib import Path

class MyComponent(Element, component='my_component.js'):
    def __init__(self) -> None:
        super().__init__()
        self.add_resource(Path(__file__).parent / 'dist')
```

Access in JavaScript:

```javascript
import { loadResource } from '../../static/utils/resources.js';

export default {
  async mounted() {
    await loadResource(window.path_prefix + `${this.resource_path}/styles.css`);
  },
  props: {
    resource_path: String,
  },
};
```

## Complete Example: Terminal Wrapper

Here's how NiceGUI wraps xterm.js:

### Python (xterm.py)

```python
from pathlib import Path
from nicegui.element import Element
from nicegui.events import GenericEventArguments, handle_event

class Xterm(Element, component='xterm.js', esm={'nicegui-xterm': 'dist'}):
    
    def __init__(self, options: dict | None = None) -> None:
        super().__init__()
        self.add_resource(Path(__file__).parent / 'dist')
        self._props['options'] = options or {}
    
    def on_data(self, callback) -> Self:
        """Handle user input."""
        def handle(e: GenericEventArguments) -> None:
            handle_event(callback, XtermDataEventArgs(
                sender=self, client=self.client, data=e.args
            ))
        self.on('data', handle)
        return self
    
    def write(self, data: str) -> AwaitableResponse:
        """Write data to terminal."""
        return self.run_method('write', data)
    
    async def get_rows(self) -> int:
        """Get terminal rows."""
        return await self.run_method('getRows')
```

### JavaScript (xterm.js)

```javascript
import { Terminal, FitAddon } from 'nicegui-xterm';
import { loadResource } from '../../static/utils/resources.js';

export default {
  template: '<div></div>',
  
  props: {
    options: Object,
    resource_path: String,
  },
  
  mounted() {
    // Create terminal
    this.terminal = new Terminal(this.options);
    this.terminal.loadAddon(this.fit_addon = new FitAddon());
    this.terminal.open(this.$el);
    
    // Re-emit terminal events to Vue/Python
    Object.getOwnPropertyNames(Object.getPrototypeOf(this.terminal))
      .filter(key => key.startsWith('on') && typeof this.terminal[key] === 'function')
      .forEach(key => {
        this.terminal[key](e => this.$emit(key.slice(2).toLowerCase(), e));
      });
    
    // Load CSS
    this.$nextTick().then(() => 
      loadResource(window.path_prefix + `${this.resource_path}/xterm.css`)
    );
  },
  
  methods: {
    getRows() {
      return this.terminal.rows;
    },
    fit() {
      this.fit_addon.fit();
    },
    write(data) {
      return this.terminal.write(data);
    },
  },
};
```

## Development Setup

Enable hot-reloading of JavaScript, CSS, and HTML files during development:

```python
ui.run(reload=True, uvicorn_reload_includes='*.js,*.css,*.html')
```

This watches your component files for changes and automatically reloads the browser.

## Dynamic Route Registration

Components that need server endpoints (like file uploads) can register routes dynamically at runtime.

### Registering Routes

```python
from nicegui import app
from nicegui.element import Element

class MyUploader(Element, component='uploader.js'):
    def __init__(self) -> None:
        super().__init__()
        # Build unique URL using client and element IDs
        self._props['url'] = f'/_nicegui/client/{self.client.id}/upload/{self.id}'
        
        # Register the route dynamically
        @app.post(self._props['url'])
        async def upload_route(request: Request) -> dict:
            # Handle the upload...
            return {'status': 'success'}
```

### URL Pattern Guidelines

| Pattern | Example | Use Case |
|---------|---------|----------|
| `/_nicegui/client/{client_id}/{action}/{element_id}` | `/_nicegui/client/abc123/upload/42` | Per-client, per-element endpoints |
| `/_nicegui/auto/static/{hash}/{filename}` | `/_nicegui/auto/static/def456/file.pdf` | Auto-generated static files |

**Important**: Always use the `/_nicegui/` prefix for dynamic routes to avoid conflicts with user-defined pages and the root page fallback.

### Cleaning Up Routes

Always remove routes when the element is deleted to prevent memory leaks:

```python
class MyUploader(Element, component='uploader.js'):
    def __init__(self) -> None:
        super().__init__()
        self._props['url'] = f'/_nicegui/client/{self.client.id}/upload/{self.id}'
        
        @app.post(self._props['url'])
        async def upload_route(request: Request) -> dict:
            return {'status': 'success'}
    
    def _handle_delete(self) -> None:
        # Remove the route when element is deleted
        app.remove_route(self._props['url'])
        super()._handle_delete()
```

### Why Dynamic Routes Work with Root Pages

Dynamic routes are registered as real FastAPI routes, which are matched **before** the 404 handler that serves root pages. This means:

1. Request to `/_nicegui/client/.../upload/...` → matches the dynamic route
2. Request to `/any/other/path` → no match → 404 handler → root page (if defined)

See [Routing Architecture](routing.md) for details on route precedence.

## Push vs Pull: Avoiding Bandwidth Bottlenecks

**Critical**: When sending large binary data (e.g., base64-encoded images, video frames) from Python to JavaScript, pushing data faster than the client can consume it will cause the system to halt.

### ❌ Push Pattern (Dangerous for High-Frequency Updates)

```python
# BAD - Server pushes frames as fast as possible
def send_frames(self):
    while True:
        frame = capture_frame()
        base64_data = encode_to_base64(frame)
        self.run_method('updateFrame', base64_data)  # May overwhelm client!
        time.sleep(0.016)  # 60 FPS attempt
```

This fails because:
- Network latency varies
- Client may be busy rendering
- WebSocket buffer fills up → connection stalls

### ✅ Pull Pattern (Safe for High-Frequency Updates)

Let the browser request data when it's ready:

```javascript
// JavaScript - Client pulls when ready
export default {
  mounted() {
    this.requestNextFrame();
  },
  methods: {
    requestNextFrame() {
      this.$emit('frame-request');  // Ask Python for next frame
    },
    updateFrame(base64Data) {
      this.imageData = base64Data;
      // Request next frame only after current one is processed
      requestAnimationFrame(() => this.requestNextFrame());
    },
  },
};
```

```python
# Python - Server responds to requests
class AnimatedImage(Element, component='animated_image.js'):
    def __init__(self) -> None:
        super().__init__()
        self.on('frame-request', self._handle_frame_request)
    
    async def _handle_frame_request(self, e) -> None:
        frame = await run.io_bound(self._get_frame)
        self.run_method('updateFrame', frame)
```

### When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| **Push** | Small, infrequent updates (notifications, status changes) |
| **Pull** | Large binary data, high-frequency updates (video, animations) |

See `samples/video_custom_component` for a complete pull-based implementation.

## Best Practices

1. **Cleanup in unmounted** - Always destroy third-party library instances
2. **Use props for data flow** - Avoid direct DOM manipulation when possible
3. **Emit events for user actions** - Let Python handle business logic
4. **Bundle dependencies** - Use ESM for npm packages
5. **Handle async initialization** - Use `mounted()` for setup that needs DOM
6. **Validate props** - Define prop types in JavaScript
7. **Clean up dynamic routes** - Always call `app.remove_route()` in `_handle_delete()`
8. **Use pull pattern for large data** - Let the client request data when ready to avoid bandwidth bottlenecks

## Debugging

### Browser Console

```javascript
// Access component instance
getElement(123)  // By element ID

// Check props
getElement(123).count
```

### Python Side

```python
# Check current props
print(element._props)

# Force update
element.update()
```
