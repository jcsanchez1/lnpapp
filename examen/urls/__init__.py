from django.urls import path, include
from ..views import (
    redirect_to_dashboard, 
    dashboard_view,
    dashboard_nacional,
    dashboard_regional,
    dashboard_centro,
    login_view
)

urlpatterns = [
    # Login en la raíz
    path('', login_view, name='login'),
    
    # Logout
    path('logout/', include('examen.urls.auth_urls')),
    
    # Dashboard
    path('dashboard/', redirect_to_dashboard, name='redirect_to_dashboard'),
    path('dashboard/inicio/', dashboard_view, name='dashboard'),
    path('dashboard/nacional/', dashboard_nacional, name='dashboard_nacional'),
    path('dashboard/regional/', dashboard_regional, name='dashboard_regional'),
    path('dashboard/centro/', dashboard_centro, name='dashboard_centro'),
]