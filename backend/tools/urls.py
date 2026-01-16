"""
치공구 관리 시스템 URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ToolViewSet

app_name = 'tools'

router = DefaultRouter()
router.register(r'tools', ToolViewSet, basename='tool')

urlpatterns = [
    path('', include(router.urls)),
]
