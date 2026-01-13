"""
QA Admin Configuration
"""
from django.contrib import admin
from .models import (
    QaProcess, QaChecklistItem, QaAssessment, QaFinding,
    Capa, CapaAction, AIRootCauseAnalysisHistory
)


@admin.register(QaProcess)
class QaProcessAdmin(admin.ModelAdmin):
    list_display = ['qa_process_id', 'process_type', 'title', 'scheduled_at', 'status']
    list_filter = ['process_type', 'status', 'scheduled_at']
    search_fields = ['qa_process_id', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(QaChecklistItem)
class QaChecklistItemAdmin(admin.ModelAdmin):
    list_display = ['item_id', 'qa_process', 'check_point', 'is_compliant']
    list_filter = ['qa_process', 'is_compliant']
    search_fields = ['item_id', 'check_point', 'requirement']
    readonly_fields = ['created_at']


@admin.register(QaAssessment)
class QaAssessmentAdmin(admin.ModelAdmin):
    list_display = ['assessment_id', 'qa_process', 'assessed_at', 'assessed_by', 'overall_score']
    list_filter = ['qa_process', 'assessed_at']
    search_fields = ['assessment_id', 'assessed_by', 'conclusion']
    readonly_fields = ['created_at']


@admin.register(QaFinding)
class QaFindingAdmin(admin.ModelAdmin):
    list_display = ['finding_id', 'qa_process', 'severity', 'is_resolved', 'created_at']
    list_filter = ['qa_process', 'severity', 'is_resolved', 'created_at']
    search_fields = ['finding_id', 'description', 'root_cause']
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(Capa)
class CapaAdmin(admin.ModelAdmin):
    list_display = ['capa_id', 'source_type', 'source_id', 'title', 'severity', 'status', 'assigned_to', 'opened_at']
    list_filter = ['source_type', 'severity', 'status', 'opened_at']
    search_fields = ['capa_id', 'title', 'description', 'assigned_to']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CapaAction)
class CapaActionAdmin(admin.ModelAdmin):
    list_display = ['action_id', 'capa', 'action_type', 'assignee', 'due_date', 'status']
    list_filter = ['capa', 'action_type', 'status', 'due_date']
    search_fields = ['action_id', 'description', 'assignee']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']


@admin.register(AIRootCauseAnalysisHistory)
class AIRootCauseAnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ['analysis_id', 'root_cause', 'confidence', 'is_applied', 'created_at']
    list_filter = ['is_applied', 'created_at']
    search_fields = ['analysis_id', 'problem_description', 'defect_details', 'root_cause']
    readonly_fields = ['created_at']
