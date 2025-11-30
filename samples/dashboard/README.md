# Analytics Dashboard

![Screenshot](screenshot.jpg)

A comprehensive analytics dashboard showcasing NiceGUI's charting and input control capabilities with an object-oriented architecture.

## Features

- **Dark Mode** - Custom styled dark theme with CSS injection
- **Interactive Filters** - All charts and KPIs update when filters change
- **Real-time Updates** - Gauge charts update every 2 seconds via `ui.timer`
- **8 Chart Types** - Line, bar, pie, gauge, radar, heatmap, scatter, candlestick
- **YoY Comparison** - Toggle to overlay last year's data on line chart

## Architecture

```
Dashboard (UI class)
├── DashboardData (dataclass) - Per-user state in app.storage.client
├── _build_*() methods - Modular UI construction
├── _create_*_chart() methods - Chart factories
├── update_*() methods - Dynamic updates
└── on_*() handlers - Event handling
```

## Charts Demonstrated

| Chart | Description |
|-------|-------------|
| **Line** | Revenue & orders trend with dual Y-axis, optional YoY comparison |
| **Bar** | Product sales with custom colors per product |
| **Pie** | Sales distribution donut chart |
| **Gauge** | Real-time CPU/memory with animated updates |
| **Radar** | Regional performance across 5 metrics |
| **Heatmap** | Weekly activity by hour |
| **Scatter** | Customer segments (Enterprise/SMB/Consumer) |
| **Candlestick** | Stock-style OHLC data |

## Input Controls

| Control | Use Case |
|---------|----------|
| `ui.select()` | Multi-select regions, date range dropdown |
| `ui.chip()` | Product filter toggles |
| `ui.switch()` | Compare YoY toggle |
| `ui.input()` | Product search with clearable |
| `ui.slider()` | Alert threshold in settings |
| `ui.number()` | Refresh interval in settings |
| `ui.radio()` | Chart type selection |
| `ui.color_input()` | Accent color picker |
| `ui.dialog()` | Settings modal |

## Key Patterns

- **OO UI class** - `Dashboard` with `current()` classmethod for per-user instance
- **Dataclass state** - `DashboardData` stored in `app.storage.client`
- **Modular build methods** - `_build_header()`, `_build_filters()`, `_build_kpis()`, `_build_charts()`
- **Chart update pattern** - Modify `chart.options` then call `chart.update()`
- **Seeded random** - Consistent fake data across page reloads

## Running

```bash
cd samples/dashboard
poetry run python main.py
```

Then open http://localhost:8080
