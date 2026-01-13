"""
ERP Integration URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MasterItemViewSet,
    MasterMachineViewSet,
    MasterWorkCenterViewSet,
    MasterBOMViewSet,
    MasterRoutingViewSet,
    ERPWorkOrderViewSet,
    ERPSyncLogViewSet,
    ERPDataImportViewSet,
)

router = DefaultRouter()
router.register(r"items", MasterItemViewSet, basename="master-item")
router.register(r"machines", MasterMachineViewSet, basename="master-machine")
router.register(r"workcenters", MasterWorkCenterViewSet, basename="master-workcenter")
router.register(r"bom", MasterBOMViewSet, basename="master-bom")
router.register(r"routing", MasterRoutingViewSet, basename="master-routing")
router.register(r"workorders", ERPWorkOrderViewSet, basename="erp-workorder")
router.register(r"sync-logs", ERPSyncLogViewSet, basename="erp-sync-log")
router.register(r"import", ERPDataImportViewSet, basename="erp-import")

urlpatterns = [
    path("", include(router.urls)),
]
