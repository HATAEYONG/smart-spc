"""
작업지시 관리 시스템 URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, WorkOrderToolViewSet

app_name = 'work_orders'

router = DefaultRouter()
router.register(r'work-orders', WorkOrderViewSet, basename='work-order')
router.register(r'work-order-tools', WorkOrderToolViewSet, basename='work-order-tool')

urlpatterns = [
    path('', include(router.urls)),
]
