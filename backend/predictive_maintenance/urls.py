from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EquipmentViewSet,
    SensorDataViewSet,
    MaintenanceRecordViewSet,
    FailurePredictionViewSet,
    MaintenancePlanViewSet
)

router = DefaultRouter()
router.register(r'equipment', EquipmentViewSet, basename='pm-equipment')
router.register(r'sensor-data', SensorDataViewSet, basename='pm-sensor-data')
router.register(r'maintenance-records', MaintenanceRecordViewSet, basename='pm-maintenance-records')
router.register(r'failure-predictions', FailurePredictionViewSet, basename='pm-failure-predictions')
router.register(r'maintenance-plans', MaintenancePlanViewSet, basename='pm-maintenance-plans')

urlpatterns = [
    path('', include(router.urls)),
]
