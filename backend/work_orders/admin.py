from django.contrib import admin
from .models import WorkOrder, WorkOrderTool, WorkOrderProgress


@admin.register(WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'product_name', 'quantity', 'status', 'priority', 'start_date', 'target_end_date', 'equipment', 'assigned_to']
    list_filter = ['status', 'priority', 'start_date', 'target_end_date']
    search_fields = ['order_number', 'product_code', 'product_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(WorkOrderTool)
class WorkOrderToolAdmin(admin.ModelAdmin):
    list_display = ['work_order', 'tool', 'quantity_required', 'usage_hours']
    list_filter = ['work_order', 'tool']
    search_fields = ['work_order__order_number', 'tool__code']


@admin.register(WorkOrderProgress)
class WorkOrderProgressAdmin(admin.ModelAdmin):
    list_display = ['work_order', 'timestamp', 'status', 'progress_percentage', 'completed_quantity', 'reported_by']
    list_filter = ['status', 'timestamp']
    search_fields = ['work_order__order_number']
    readonly_fields = ['timestamp']
