"""
ERP/MES 연계 시스템 URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ERPIntegrationViewSet, IntegrationHistoryViewSet, ManualQualityInputViewSet

app_name = 'integration'

router = DefaultRouter()
router.register(r'erp-integrations', ERPIntegrationViewSet, basename='erp-integration')
router.register(r'integration-history', IntegrationHistoryViewSet, basename='integration-history')
router.register(r'manual-inputs', ManualQualityInputViewSet, basename='manual-input')

urlpatterns = [
    path('', include(router.urls)),
]
