from django.urls import path
from ..views import logout_view

urlpatterns = [
    path('', logout_view, name='logout'),  # Solo logout
]