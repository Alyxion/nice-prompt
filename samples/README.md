# Sample Applications

Working example applications demonstrating NiceGUI patterns.

## Samples

| Sample | Description |
|--------|-------------|
| [multi_dashboard/](multi_dashboard/) | Full SPA with authentication, signed cookies, role-based permissions, `ui.sub_pages`, `AppLayout` class |
| [sub_pages_demo/](sub_pages_demo/) | SPA navigation with persistent `app.storage.client` state, nested sub_pages |
| [dashboard/](dashboard/) | Simple sales dashboard with dataclass, `bind_value`, `container.clear()` |
| [stock_peers/](stock_peers/) | Stock comparison with async loading, dark mode, `ui.echart()` |
| [bouncing_circle/](bouncing_circle/) | Custom JS/Vue component with server-side PIL rendering |

## Running a Sample

```bash
cd samples/<sample_name>
poetry run python main.py
```

Then open http://localhost:8080
