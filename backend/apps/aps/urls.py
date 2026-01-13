from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .performance_views import PerformanceMetricsViewSet
from .scenario_views import ScenarioViewSet, ScenarioComparisonViewSet
from .constraint_views import (
    ConstraintViewSet,
    ConstraintViolationViewSet,
    ConstraintGroupViewSet,
    ConstraintTemplateViewSet,
)
from .sequence_views import (
    JobSequenceViewSet,
    SequenceOptimizationViewSet,
    SequenceComparisonViewSet,
)
from .monitoring_views import MonitoringViewSet, AlertViewSet
from .report_views import ReportViewSet, ExportViewSet, ReportTemplateViewSet
from .settings_views import (
    UserSettingsViewSet,
    PresetViewSet,
    UserActivityViewSet,
    SystemConfigurationViewSet,
)
from .ai_llm_views import ChatBotViewSet, PredictiveAnalyticsViewSet, SmartRecommendationViewSet, AIInsightViewSet

router = DefaultRouter()
router.register(r'plans', views.PlansViewSet, basename='plans')
router.register(r'comparison', views.AlgorithmComparisonViewSet, basename='comparison')
router.register(r'bottleneck', views.BottleneckAnalysisViewSet, basename='bottleneck')
router.register(r'performance', PerformanceMetricsViewSet, basename='performance')
router.register(r'scenarios', ScenarioViewSet, basename='scenarios')
router.register(r'scenario-comparisons', ScenarioComparisonViewSet, basename='scenario-comparisons')
router.register(r'constraints', ConstraintViewSet, basename='constraints')
router.register(r'violations', ConstraintViolationViewSet, basename='violations')
router.register(r'constraint-groups', ConstraintGroupViewSet, basename='constraint-groups')
router.register(r'constraint-templates', ConstraintTemplateViewSet, basename='constraint-templates')
router.register(r'job-sequences', JobSequenceViewSet, basename='job-sequences')
router.register(r'sequence-optimizations', SequenceOptimizationViewSet, basename='sequence-optimizations')
router.register(r'sequence-comparisons', SequenceComparisonViewSet, basename='sequence-comparisons')
router.register(r'monitoring', MonitoringViewSet, basename='monitoring')
router.register(r'alerts', AlertViewSet, basename='alerts')
router.register(r'reports', ReportViewSet, basename='reports')
router.register(r'exports', ExportViewSet, basename='exports')
router.register(r'report-templates', ReportTemplateViewSet, basename='report-templates')
router.register(r'user-settings', UserSettingsViewSet, basename='user-settings')
router.register(r'presets', PresetViewSet, basename='presets')
router.register(r'user-activity', UserActivityViewSet, basename='user-activity')
router.register(r'system-config', SystemConfigurationViewSet, basename='system-config')

# AI & LLM Features
router.register(r'ai/chatbot', ChatBotViewSet, basename='ai-chatbot')
router.register(r'ai/predictive-analytics', PredictiveAnalyticsViewSet, basename='ai-predictive-analytics')
router.register(r'ai/recommendations', SmartRecommendationViewSet, basename='ai-recommendations')
router.register(r'ai/insights', AIInsightViewSet, basename='ai-insights')

urlpatterns = [
    path('', include(router.urls)),
]
