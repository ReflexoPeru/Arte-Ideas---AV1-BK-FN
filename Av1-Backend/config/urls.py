"""
URL configuration for arte_ideas_backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/core/', include('apps.core.urls')),
    path('api/crm/', include('apps.crm.urls')),
    path('api/commerce/', include('apps.commerce.urls')),
    path('api/operations/', include('apps.operations.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]
