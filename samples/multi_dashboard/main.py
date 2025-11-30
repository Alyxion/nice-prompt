#!/usr/bin/env python3
"""
Multi-Dashboard Application - Auto-discovers pages with PAGE class attribute.

Uses root page + ui.sub_pages for SPA-style navigation with persistent state.
Includes authentication with role-based access control.
"""
from pathlib import Path
from nicegui import app, ui

from layout import AppLayout


# ============================================================================
# Server Setup
# ============================================================================
STATIC_DIR = Path(__file__).parent / 'static'
PAGES_DIR = Path(__file__).parent / 'pages'

# Serve static files (with reload on change)
app.add_static_files('/static', STATIC_DIR)

# Discover pages at startup
AppLayout.discover_pages(str(PAGES_DIR), exclude={'login'})


def root():
    """Root page entry point."""
    AppLayout.current().build()


if __name__ in {'__main__', '__mp_main__'}:
    # Include static folder in reload watch paths
    ui.run(
        root,
        show=False,
        title='Multi-Dashboard App',
        reload=True,
        uvicorn_reload_includes='*.py,*.js,*.css',
    )
