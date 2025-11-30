# Core Mechanics

Documentation for NiceGUI patterns and concepts.

## Files

| File | Description |
|------|-------------|
| [application_structure.md](application_structure.md) | App setup, `ui.run()`, file organization, SPA structure |
| [pages.md](pages.md) | Routing with `@ui.page`, path parameters, `ui.navigate` |
| [sub_pages.md](sub_pages.md) | `ui.sub_pages` for SPA routing, persistent state, nested routes |
| [authentication.md](authentication.md) | Signed cookies, role-based permissions, login flows |
| [container_updates.md](container_updates.md) | Dynamic content: `container.clear()`, `@ui.refreshable` |
| [event_binding.md](event_binding.md) | Event handlers, async handlers, throttling |
| [binding_and_state.md](binding_and_state.md) | `bind_value()`, `bind_visibility()`, reactive state |
| [data_modeling.md](data_modeling.md) | Pydantic models, dataclasses, `app.storage` patterns |
| [styling.md](styling.md) | Tailwind CSS, `.classes()`, `.style()`, dark mode |
| [javascript_integration.md](javascript_integration.md) | External JS, `ui.run_javascript()`, browser APIs |

## Advanced

| File | Description |
|------|-------------|
| [custom_components.md](custom_components.md) | Custom JS/Vue components, `run_method()`, Vue lifecycle |
| [configuration_deployment.md](configuration_deployment.md) | `ui.run()` params, Docker, PyInstaller, SSL |
