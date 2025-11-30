"""Authentication module with session management and user credentials."""
import json
import base64
import hmac
import hashlib
from dataclasses import dataclass, field
from nicegui import app, ui, context


# Secret key for signing cookies (in production, use environment variable)
SECRET_KEY = 'change-me-in-production'

# Cookie settings
COOKIE_NAME = 'auth_session'
COOKIE_MAX_AGE_DAYS = 7

# Role to permissions mapping
ROLE_PERMISSIONS = {
    'user': {'view_settings'},
    'admin': {'view_settings', 'view_users', 'manage_users'},
}

# User credentials (in production, use a database)
USERS = {
    'admin': {'password': 'demo123', 'roles': ['user', 'admin']},
    'user': {'password': 'demo123', 'roles': ['user']},
    'guest': {'password': 'demo123', 'roles': []},
}


def _sign(data: str) -> str:
    """Create HMAC signature for data."""
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()


def _encode_cookie(data: dict) -> str:
    """Encode and sign cookie data."""
    json_data = json.dumps(data)
    b64_data = base64.b64encode(json_data.encode()).decode()
    signature = _sign(b64_data)
    return f'{b64_data}.{signature}'


def _decode_cookie(cookie: str) -> dict | None:
    """Decode and verify cookie data."""
    try:
        b64_data, signature = cookie.rsplit('.', 1)
        if not hmac.compare_digest(signature, _sign(b64_data)):
            return None  # Invalid signature
        json_data = base64.b64decode(b64_data).decode()
        return json.loads(json_data)
    except (ValueError, json.JSONDecodeError):
        return None


@dataclass
class AuthSession:
    """Authentication session with signed cookie persistence.
    
    Uses signed HTTP cookies for persistent auth state (survives page reload),
    and app.storage.client for transient state like redirect_after_login.
    """
    authenticated: bool = False
    username: str = ''
    roles: list[str] = field(default_factory=list)
    
    @classmethod
    def current(cls) -> 'AuthSession':
        """Get or create the current auth session from cookie."""
        # Check if we have a cached instance in client storage
        if 'auth' in app.storage.client:
            return app.storage.client['auth']
        
        # Create new instance and restore from cookie if available
        session = cls()
        request = context.client.request
        if request and COOKIE_NAME in request.cookies:
            data = _decode_cookie(request.cookies[COOKIE_NAME])
            if data:
                session.authenticated = data.get('authenticated', False)
                session.username = data.get('username', '')
                session.roles = data.get('roles', [])
        
        # Cache in client storage for this connection
        app.storage.client['auth'] = session
        return session
    
    def _set_cookie(self) -> None:
        """Set signed auth cookie via JavaScript (works during WebSocket callbacks)."""
        data = {
            'authenticated': self.authenticated,
            'username': self.username,
            'roles': self.roles,
        }
        cookie_value = _encode_cookie(data)
        # Use JavaScript to set cookie (httponly not possible via JS, but we sign it)
        js = f'document.cookie = "{COOKIE_NAME}={cookie_value}; path=/; max-age={COOKIE_MAX_AGE_DAYS * 86400}; samesite=lax";'
        ui.run_javascript(js)
    
    def _delete_cookie(self) -> None:
        """Delete auth cookie via JavaScript."""
        js = f'document.cookie = "{COOKIE_NAME}=; path=/; max-age=0";'
        ui.run_javascript(js)
    
    def login(self, username: str, roles: list[str]) -> None:
        """Set authenticated state and persist to cookie."""
        self.authenticated = True
        self.username = username
        self.roles = roles
        self._set_cookie()
    
    def logout(self) -> None:
        """Clear authenticated state and cookie."""
        self.authenticated = False
        self.username = ''
        self.roles = []
        self._delete_cookie()
        # Clear redirect
        if 'redirect_after_login' in app.storage.client:
            del app.storage.client['redirect_after_login']
    
    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission based on their roles."""
        for role in self.roles:
            if permission in ROLE_PERMISSIONS.get(role, set()):
                return True
        return False
    
    @property
    def redirect_after_login(self) -> str:
        """Get redirect URL from client storage."""
        return app.storage.client.get('redirect_after_login', '')
    
    @redirect_after_login.setter
    def redirect_after_login(self, value: str) -> None:
        """Set redirect URL in client storage."""
        app.storage.client['redirect_after_login'] = value
    
    def get_redirect_and_clear(self) -> str:
        """Get redirect URL and clear it."""
        url = self.redirect_after_login
        if 'redirect_after_login' in app.storage.client:
            del app.storage.client['redirect_after_login']
        return url
    
    def try_login(self, username: str, password: str) -> bool:
        """Attempt login with credentials. Returns True if successful."""
        user_data = USERS.get(username)
        if user_data and user_data['password'] == password:
            self.login(username, user_data['roles'])
            return True
        return False
