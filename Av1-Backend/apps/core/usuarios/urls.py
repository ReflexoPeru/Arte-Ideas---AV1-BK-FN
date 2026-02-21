"""
URLs del Módulo de Usuarios - Arte Ideas
"""
from django.urls import path
from .views import (
    ProfileView, ProfileStatisticsView, ProfileCompletionView,
    ProfileActivityView, ChangePasswordView, ChangeEmailView
)

app_name = 'usuarios'

urlpatterns = [
    # Perfil personal
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/statistics/', ProfileStatisticsView.as_view(), name='profile_statistics'),
    path('profile/completion/', ProfileCompletionView.as_view(), name='profile_completion'),
    path('profile/activity/', ProfileActivityView.as_view(), name='profile_activity'),
    
    # Seguridad
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('change-email/', ChangeEmailView.as_view(), name='change_email'),
]