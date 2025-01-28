from django.urls import path
from .views import ( CustomLoginView, ExpedienteListView,
                        ExpedienteDetailView, MuestraListView,
                        MuestraDetailView, ReportesView,
                        RegionListView, RegionDetailView,
                        ExpedienteCreateView, ExpedienteListDataView,
                        MuestraCreateView, MuestraListDataView,
                        ExpedienteSearchView, ExpedienteAjaxCreateView
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
    path('expedientes/crear/', ExpedienteCreateView.as_view(), name='expediente_create'),      
    path('expedientes/data/', ExpedienteListDataView.as_view(), name='expediente_list_data'),
    path('expedientes/<int:pk>/muestra/crear/', MuestraCreateView.as_view(), name='muestra_create'),  
    path('muestras/data/', MuestraListDataView.as_view(), name='muestra_list_data'),
    path('expedientes/search/', ExpedienteSearchView.as_view(), name='expediente_search'),
    path('expedientes/ajax-create/', ExpedienteAjaxCreateView.as_view(), name='expediente_ajax_create'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)