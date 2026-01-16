from django.contrib import admin
from .models import Equipment, EquipmentPart, EquipmentManual, EquipmentRepairHistory, PreventiveMaintenance


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'type', 'status', 'department', 'health_score', 'installation_date']
    list_filter = ['status', 'type', 'department', 'installation_date']
    search_fields = ['code', 'name', 'manufacturer', 'model', 'serial_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EquipmentPart)
class EquipmentPartAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'equipment', 'stock_quantity', 'min_stock', 'unit_price']
    list_filter = ['equipment', 'supplier']
    search_fields = ['code', 'name', 'part_number']


@admin.register(EquipmentManual)
class EquipmentManualAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'title', 'file_type', 'version', 'upload_date']
    list_filter = ['file_type', 'upload_date']
    search_fields = ['equipment__code', 'title', 'description']


@admin.register(EquipmentRepairHistory)
class EquipmentRepairHistoryAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'repair_date', 'repair_type', 'status', 'total_cost', 'downtime_hours']
    list_filter = ['repair_type', 'status', 'repair_date']
    search_fields = ['equipment__code', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PreventiveMaintenance)
class PreventiveMaintenanceAdmin(admin.ModelAdmin):
    list_display = ['task_number', 'task_name', 'equipment', 'frequency', 'scheduled_date', 'status', 'priority']
    list_filter = ['frequency', 'status', 'priority', 'scheduled_date']
    search_fields = ['task_number', 'task_name', 'description']
    readonly_fields = ['created_at', 'updated_at']
