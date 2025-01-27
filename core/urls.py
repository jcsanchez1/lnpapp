from django.urls import path
from .views import ( CustomLoginView, ExpedienteListView,
                        ExpedienteDetailView, MuestraListView,
                        MuestraDetailView, ReportesView,
                        RegionListView, RegionDetailView
)
from django.conf import settings
from django.conf.urls.static import static
from .views import DashboardView, dashboard_data
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', CustomLoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/dashboard-data/', dashboard_data, name='dashboard_data'),
    path('expedientes/', ExpedienteListView.as_view(), name='expediente_list'),
    path('expedientes/<int:pk>/', ExpedienteDetailView.as_view(), name='expediente_detail'),
    path('muestras/', MuestraListView.as_view(), name='muestra_list'),
    path('muestras/<int:pk>/', MuestraDetailView.as_view(), name='muestra_detail'),
    path('reportes/', ReportesView.as_view(), name='reportes'),
    path('regiones/', RegionListView.as_view(), name='centros'),
    path('regiones/<int:pk>/', RegionDetailView.as_view(), name='region_detail'),    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)