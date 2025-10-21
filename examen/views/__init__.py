from .auth_views import login_view, logout_view, redirect_to_dashboard, dashboard_view
from .dashboard_views import dashboard_nacional, dashboard_regional, dashboard_centro

__all__ = [
    'login_view',
    'logout_view', 
    'redirect_to_dashboard',
    'dashboard_view',
    'dashboard_nacional',
    'dashboard_regional',
    'dashboard_centro',
]