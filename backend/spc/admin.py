"""
SPC Admin Configuration
"""
from django.contrib import admin
from .models import SamplingRule, SpcChartDefinition, SpcPoint, SpcEvent


@admin.register(SamplingRule)
class SamplingRuleAdmin(admin.ModelAdmin):
    list_display = ['rule_id', 'standard', 'aql', 'lot_size_from', 'lot_size_to', 'sample_size', 'accept_limit', 'reject_limit']
    list_filter = ['standard', 'aql']
    search_fields = ['rule_id', 'standard']
    readonly_fields = ['created_at']


@admin.register(SpcChartDefinition)
class SpcChartDefinitionAdmin(admin.ModelAdmin):
    list_display = ['chart_def_id', 'parameter_id', 'chart_type', 'sample_size', 'ucl', 'cl', 'lcl', 'is_active']
    list_filter = ['chart_type', 'is_active', 'created_at']
    search_fields = ['chart_def_id', 'parameter_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(SpcPoint)
class SpcPointAdmin(admin.ModelAdmin):
    list_display = ['point_id', 'chart_def', 'timestamp', 'sample_id', 'value', 'mean', 'range_val']
    list_filter = ['chart_def', 'timestamp']
    search_fields = ['point_id', 'sample_id']
    readonly_fields = ['created_at']


@admin.register(SpcEvent)
class SpcEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'chart_def', 'event_type', 'triggered_at', 'severity', 'status', 'assigned_to']
    list_filter = ['event_type', 'severity', 'status', 'triggered_at']
    search_fields = ['event_id', 'description', 'assigned_to']
    readonly_fields = ['created_at', 'resolved_at']
