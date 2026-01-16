"""
품질 이슈 시스템 URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QualityIssueViewSet

app_name = 'quality_issues'

router = DefaultRouter()
router.register(r'issues', QualityIssueViewSet, basename='quality-issue')

urlpatterns = [
    path('', include(router.urls)),
]
