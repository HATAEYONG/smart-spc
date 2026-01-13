"""
Django Admin 설정

APS 모델의 관리자 인터페이스
"""
from django.contrib import admin
from .models import (
    BottleneckAnalysis,
    MachineLoadHistory,
    AlgorithmComparison,
    OperationActual,
    ExecutionEvent,
    UnplannedReason,
)
from .scenario_models import Scenario, ScenarioResult, ScenarioComparison
from .ai_llm_models import PredictiveModel, Prediction


# ============================================================================
# Bottleneck Analysis
# ============================================================================
@admin.register(BottleneckAnalysis)
class BottleneckAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'analysis_id', 'mc_cd', 'utilization_rate', 'bottleneck_score',
        'is_bottleneck', 'affected_jobs', 'created_at'
    ]
    list_filter = ['is_bottleneck', 'created_at', 'mc_cd']
    search_fields = ['mc_cd']
    ordering = ['-created_at', '-bottleneck_score']


@admin.register(MachineLoadHistory)
class MachineLoadHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'history_id', 'mc_cd', 'timestamp', 'utilization_rate',
        'active_jobs', 'queued_jobs'
    ]
    list_filter = ['mc_cd', 'timestamp']
    search_fields = ['mc_cd']
    ordering = ['-timestamp']


@admin.register(AlgorithmComparison)
class AlgorithmComparisonAdmin(admin.ModelAdmin):
    list_display = [
        'comparison_id', 'job_count', 'machine_count',
        'ga_makespan', 'best_rule', 'created_at'
    ]
    list_filter = ['best_rule', 'created_at']
    ordering = ['-created_at']


# ============================================================================
# STEP 2: Execution Models
# ============================================================================
@admin.register(OperationActual)
class OperationActualAdmin(admin.ModelAdmin):
    list_display = [
        'actual_id', 'wo_no', 'resource_code', 'proc_time_hr',
        'is_abnormal', 'delay_minutes', 'status', 'actual_start_dt'
    ]
    list_filter = ['status', 'is_abnormal', 'resource_code', 'actual_start_dt']
    search_fields = ['wo_no', 'resource_code', 'operation_nm']
    ordering = ['-actual_start_dt']


@admin.register(ExecutionEvent)
class ExecutionEventAdmin(admin.ModelAdmin):
    list_display = [
        'event_id', 'resource_code', 'event_type', 'duration_minutes',
        'start_dt', 'end_dt'
    ]
    list_filter = ['event_type', 'resource_code', 'start_dt']
    search_fields = ['resource_code', 'event_description']
    ordering = ['-start_dt']


# ============================================================================
# STEP 3: UnplannedReason (미계획 원인 분석)
# ============================================================================
@admin.register(UnplannedReason)
class UnplannedReasonAdmin(admin.ModelAdmin):
    """미계획 원인 분석 관리자 인터페이스"""

    list_display = [
        'reason_id',
        'scenario',
        'wo_no',
        'reason_code',
        'status',
        'delay_hours',
        'confidence',
        'created_at'
    ]

    list_filter = [
        'reason_code',
        'status',
        'created_at',
        'scenario',
    ]

    search_fields = [
        'wo_no',
        'itm_id',
        'mc_cd',
        'explanation',
    ]

    ordering = ['-created_at', 'scenario']

    readonly_fields = [
        'reason_id',
        'created_at',
        'updated_at',
        'get_risk_level',
        'get_recommendation',
    ]

    fieldsets = (
        ('기본 정보', {
            'fields': (
                'reason_id',
                'scenario',
                'wo_no',
                'itm_id',
                'mc_cd',
            )
        }),
        ('원인 분류', {
            'fields': (
                'reason_code',
                'status',
                'confidence',
                'explanation',
            )
        }),
        ('분석 메트릭', {
            'fields': (
                'delay_hours',
                'due_date',
                'priority',
                'analysis_data',
            )
        }),
        ('권장 조치', {
            'fields': (
                'get_risk_level',
                'get_recommendation',
            ),
            'classes': ('collapse',)
        }),
        ('메타데이터', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_risk_level(self, obj):
        """위험 수준"""
        return obj.risk_level
    get_risk_level.short_description = '위험 수준'

    def get_recommendation(self, obj):
        """권장 조치"""
        return obj.get_recommendation()
    get_recommendation.short_description = '권장 조치'


# ============================================================================
# Scenario Models
# ============================================================================
@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = [
        'scenario_id', 'name', 'algorithm', 'status',
        'base_plan_date', 'created_at'
    ]
    list_filter = ['status', 'algorithm', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-created_at']


@admin.register(ScenarioResult)
class ScenarioResultAdmin(admin.ModelAdmin):
    list_display = [
        'result_id', 'scenario', 'makespan', 'total_tardiness',
        'completed_jobs', 'total_jobs', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['scenario__name']
    ordering = ['-created_at']


@admin.register(ScenarioComparison)
class ScenarioComparisonAdmin(admin.ModelAdmin):
    list_display = [
        'comparison_id', 'name', 'created_at'
    ]
    list_filter = ['created_at']
    ordering = ['-created_at']


# ============================================================================
# AI/LLM Models
# ============================================================================
@admin.register(PredictiveModel)
class PredictiveModelAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'model_name', 'model_type', 'algorithm',
        'status', 'version', 'created_at'
    ]
    list_filter = ['model_type', 'status', 'created_at']
    search_fields = ['model_name', 'description']
    ordering = ['-created_at']


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'model', 'prediction_type', 'target_entity',
        'predicted_value', 'confidence_score', 'predicted_date'
    ]
    list_filter = ['prediction_type', 'predicted_date', 'model']
    search_fields = ['target_entity', 'explanation']
    ordering = ['-predicted_date']
