from django.contrib import admin
from .models import ERPIntegration, IntegrationHistory, ManualQualityInput


@admin.register(ERPIntegration)
class ERPIntegrationAdmin(admin.ModelAdmin):
    list_display = ['name', 'system_type', 'status', 'auto_sync', 'last_sync', 'is_active']
    list_filter = ['system_type', 'status', 'is_active', 'auto_sync']
    search_fields = ['name', 'description', 'endpoint_url']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(IntegrationHistory)
class IntegrationHistoryAdmin(admin.ModelAdmin):
    list_display = ['sync_id', 'integration', 'sync_type', 'status', 'start_time', 'records_processed', 'records_success']
    list_filter = ['sync_type', 'status', 'start_time']
    search_fields = ['sync_id', 'integration__name']
    readonly_fields = ['created_at']


@admin.register(ManualQualityInput)
class ManualQualityInputAdmin(admin.ModelAdmin):
    list_display = ['record_number', 'inspection_type', 'inspection_date', 'product_name', 'sample_size', 'defect_rate', 'status', 'department']
    list_filter = ['inspection_type', 'status', 'inspection_date', 'department']
    search_fields = ['record_number', 'product_code', 'product_name', 'batch_number', 'lot_number']
    readonly_fields = ['created_at', 'updated_at']
