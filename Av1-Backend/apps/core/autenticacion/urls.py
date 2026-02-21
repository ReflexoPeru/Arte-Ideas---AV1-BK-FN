"""
URLs del Módulo de Autenticación - Arte Ideas
"""
from django.urls import path
from .views import LogoutView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'autenticacion'

urlpatterns = [
    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
