"""
Inspection Admin Configuration
"""
from django.contrib import admin
from .models import ProcessFlow, ProcessStep, InspectionRun, InspectionResult, AIProcessDesignHistory


@admin.register(ProcessFlow)
class ProcessFlowAdmin(admin.ModelAdmin):
    list_display = ['flow_id', 'product_id', 'version', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['flow_id', 'product_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ['step_id', 'flow', 'step_order', 'step_name', 'inspection_type']
    list_filter = ['flow', 'inspection_type']
    search_fields = ['step_id', 'step_name']
    readonly_fields = ['created_at']


@admin.register(InspectionRun)
class InspectionRunAdmin(admin.ModelAdmin):
    list_display = ['run_id', 'flow', 'run_type', 'status', 'inspector_id', 'started_at']
    list_filter = ['run_type', 'status', 'started_at']
    search_fields = ['run_id', 'inspector_id']
    readonly_fields = ['created_at']


@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ['result_id', 'run', 'step', 'sample_id', 'measurement_value', 'is_oos', 'measured_at']
    list_filter = ['run', 'step', 'is_oos', 'measured_at']
    search_fields = ['result_id', 'sample_id']
    readonly_fields = ['created_at']


@admin.register(AIProcessDesignHistory)
class AIProcessDesignHistoryAdmin(admin.ModelAdmin):
    list_display = ['design_id', 'production_volume', 'proposed_flow', 'confidence', 'is_applied', 'created_at']
    list_filter = ['is_applied', 'created_at']
    search_fields = ['design_id', 'product_description', 'quality_requirements']
    readonly_fields = ['created_at']
