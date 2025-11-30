"""Users views."""
from .user_list import UserListView
from .roles import RolesView
from .activity import ActivityView
from .settings import SettingsView

__all__ = ['UserListView', 'RolesView', 'ActivityView', 'SettingsView']
