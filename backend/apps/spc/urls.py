from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from . import views
from apps.spc import views_master_data as master_data

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'inspection-plans', views.InspectionPlanViewSet, basename='inspection-plan')
router.register(r'measurements', views.QualityMeasurementViewSet, basename='measurement')
router.register(r'control-charts', views.ControlChartViewSet, basename='control-chart')
router.register(r'process-capability', views.ProcessCapabilityViewSet, basename='process-capability')
router.register(r'run-rule-violations', views.RunRuleViolationViewSet, basename='run-rule-violation')
router.register(r'alerts', views.QualityAlertViewSet, basename='alert')
router.register(r'reports', views.QualityReportViewSet, basename='report')
router.register(r'chatbot', views.ChatbotViewSet, basename='chatbot')
router.register(r'advanced-charts', views.AdvancedControlChartViewSet, basename='advanced-chart')
router.register(r'time-series', views.TimeSeriesAnalysisViewSet, basename='time-series')
router.register(r'ai-prompts', views.AIPromptViewSet, basename='ai-prompt')

# Six Sigma DMAIC URLs - Temporarily disabled due to encoding issues
# six_sigma_router = DefaultRouter()
# six_sigma_router.register(r'projects', six_sigma.DMAICProjectViewSet, basename='dmaic-project')
# ...

# Master Data URLs
master_data_router = DefaultRouter()
master_data_router.register(r'items', master_data.QualityItemMasterViewSet, basename='quality-item')
master_data_router.register(r'processes', master_data.QualityProcessMasterViewSet, basename='quality-process')
master_data_router.register(r'characteristics', master_data.QualityCharacteristicMasterViewSet, basename='quality-characteristic')
master_data_router.register(r'instruments', master_data.MeasurementInstrumentMasterViewSet, basename='measurement-instrument')
master_data_router.register(r'systems', master_data.MeasurementSystemMasterViewSet, basename='measurement-system')
master_data_router.register(r'standards', master_data.InspectionStandardMasterViewSet, basename='inspection-standard')
master_data_router.register(r'sync-logs', master_data.QualitySyncLogViewSet, basename='quality-sync-log')

# Six Sigma dummy endpoint (placeholder for future implementation)
@api_view(['GET'])
@permission_classes([AllowAny])
def six_sigma_dashboard(request):
    """Six Sigma dashboard placeholder"""
    return Response({
        'total_projects': 0,
        'active_projects': 0,
        'completed_projects': 0,
        'avg_dpmo': 0,
        'projects_by_phase': {
            'Define': 0,
            'Measure': 0,
            'Analyze': 0,
            'Improve': 0,
            'Control': 0,
        },
        'by_phase': {
            'Define': 0,
            'Measure': 0,
            'Analyze': 0,
            'Improve': 0,
            'Control': 0,
        },
        'by_status': {
            'NOT_STARTED': 0,
            'IN_PROGRESS': 0,
            'COMPLETED': 0,
            'ON_HOLD': 0,
        },
        'by_priority': {
            'CRITICAL': 0,
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
        },
        'recent_projects': []
    })

urlpatterns = [
    path('', include(router.urls)),
    path('six-sigma/projects/dashboard/', six_sigma_dashboard, name='six-sigma-dashboard'),
    path('master-data/', include(master_data_router.urls)),
]
