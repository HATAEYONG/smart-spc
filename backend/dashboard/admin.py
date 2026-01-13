"""
Dashboard Admin Configuration
"""
from django.contrib import admin
from .models import DashboardKPI, TopDefect, Alert, AIInsight


@admin.register(DashboardKPI)
class DashboardKPIAdmin(admin.ModelAdmin):
    list_display = ['period', 'copq_rate', 'total_copq', 'total_qcost', 'oos_count', 'spc_open_events']
    list_filter = ['period']
    search_fields = ['period']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TopDefect)
class TopDefectAdmin(admin.ModelAdmin):
    list_display = ['period', 'defect', 'count', 'cost']
    list_filter = ['period', 'defect']
    search_fields = ['period', 'defect']
    readonly_fields = ['created_at']


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'type', 'severity', 'title', 'status', 'created_at']
    list_filter = ['type', 'severity', 'status', 'created_at']
    search_fields = ['event_id', 'title', 'description']
    readonly_fields = ['created_at', 'resolved_at']


@admin.register(AIInsight)
class AIInsightAdmin(admin.ModelAdmin):
    list_display = ['ai_id', 'period', 'title', 'insight_type', 'confidence', 'actionable', 'created_at']
    list_filter = ['period', 'insight_type', 'actionable', 'created_at']
    search_fields = ['ai_id', 'title', 'summary']
    readonly_fields = ['created_at']
