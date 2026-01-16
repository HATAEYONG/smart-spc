"""
설비 관리 시스템 URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EquipmentViewSet, PreventiveMaintenanceViewSet

app_name = 'equipment'

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'preventive-maintenance', PreventiveMaintenanceViewSet, basename='preventive-maintenance')

urlpatterns = [
    path('', include(router.urls)),
]
