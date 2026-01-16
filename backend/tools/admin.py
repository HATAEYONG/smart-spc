from django.contrib import admin
from .models import Tool, ToolRepairHistory


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type', 'status', 'department', 'usage_percentage', 'predicted_remaining_days']
    list_filter = ['status', 'type', 'department', 'purchase_date']
    search_fields = ['code', 'name', 'manufacturer', 'model', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ToolRepairHistory)
class ToolRepairHistoryAdmin(admin.ModelAdmin):
    list_display = ['tool', 'repair_date', 'repair_type', 'status', 'total_cost', 'downtime_hours']
    list_filter = ['repair_type', 'status', 'repair_date']
    search_fields = ['tool__code', 'description']
    readonly_fields = ['created_at', 'updated_at']
