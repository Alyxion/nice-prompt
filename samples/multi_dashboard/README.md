# Multi-Dashboard Application

![Screenshot](screenshot.jpg)

A full SPA demonstrating authentication, signed cookie persistence, role-based permissions, and auto-discovered pages.

## Features

- **Signed Cookie Authentication** - HMAC-signed cookies for persistent login across reloads
- **Role-Based Permissions** - Pages hidden or protected based on user roles
- **Auto-Discovered Pages** - Pages with `PAGE` attribute are auto-registered at startup
- **SPA Navigation** - `ui.sub_pages` with header/drawer visibility management
- **Hot Reload** - JS/CSS changes reload automatically

## File Structure

| File/Folder | Description |
|-------------|-------------|
| `main.py` | Server setup only (static files, page discovery, `ui.run`) |
| `layout.py` | `AppLayout` class (header, drawer, routing, auth checks) |
| `models/auth.py` | `AuthSession` dataclass with signed cookie persistence |
| `pages/` | Auto-discovered page modules (analytics, inventory, users, settings, login) |
| `static/` | CSS and JavaScript files |

## Key Patterns

| Pattern | Location | Description |
|---------|----------|-------------|
| Minimal server setup | `main.py` | Only static files, page discovery, and `ui.run()` |
| Layout class | `layout.py` | `AppLayout.current()` stored in `app.storage.client` |
| Header/drawer toggle | `layout.py` | `show()`/`hide()` methods for login page |
| Signed cookies | `models/auth.py` | HMAC-signed JSON via JavaScript |
| Page auto-discovery | `layout.py` | Scans `pages/` for classes with `PAGE` attribute |
| Permission checks | `layout.py` | `make_page_builder()` checks `requires` before rendering |

## Default Users

| Username | Password | Roles |
|----------|----------|-------|
| admin | demo123 | user, admin |
| user | demo123 | user |
| guest | demo123 | (none) |

## Running

```bash
cd samples/multi_dashboard
poetry run python main.py
```

Open http://localhost:8080
