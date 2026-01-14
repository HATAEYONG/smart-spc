from django.contrib import admin
from .models import Equipment, SensorData, MaintenanceRecord, FailurePrediction, MaintenancePlan


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'status', 'location', 'health_score', 'failure_probability', 'availability_current']
    list_filter = ['category', 'status', 'installation_date']
    search_fields = ['code', 'name', 'location', 'manufacturer']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('기본 정보', {
            'fields': ('code', 'name', 'category', 'status', 'location')
        }),
        ('상세 정보', {
            'fields': ('manufacturer', 'model_number', 'serial_number', 'installation_date', 'warranty_expiry')
        }),
        ('용량 정보', {
            'fields': ('rated_capacity', 'current_capacity')
        }),
        ('예지 보전', {
            'fields': ('mtbf_mean_time', 'mttr_mean_time', 'availability_target', 'availability_current',
                      'last_maintenance_date', 'next_maintenance_date', 'failure_probability', 'health_score')
        }),
        ('시스템', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SensorData)
class SensorDataAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'sensor_type', 'value', 'unit', 'is_normal', 'anomaly_score', 'timestamp']
    list_filter = ['sensor_type', 'is_normal', 'timestamp']
    search_fields = ['equipment__code', 'equipment__name', 'sensor_id']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'


@admin.register(MaintenanceRecord)
class MaintenanceRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'record_type', 'status', 'title', 'scheduled_date', 'technician', 'total_cost']
    list_filter = ['record_type', 'status', 'scheduled_date']
    search_fields = ['equipment__code', 'equipment__name', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'scheduled_date'


@admin.register(FailurePrediction)
class FailurePredictionAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'severity', 'failure_probability', 'confidence', 'predicted_failure_date', 'is_acknowledged']
    list_filter = ['severity', 'is_acknowledged', 'prediction_date']
    search_fields = ['equipment__code', 'equipment__name', 'potential_causes', 'recommended_actions']
    readonly_fields = ['prediction_date', 'acknowledged_at']
    date_hierarchy = 'prediction_date'


@admin.register(MaintenancePlan)
class MaintenancePlanAdmin(admin.ModelAdmin):
    list_display = ['equipment', 'name', 'frequency', 'status', 'next_due_date', 'assigned_to', 'estimated_cost']
    list_filter = ['frequency', 'status', 'next_due_date']
    search_fields = ['equipment__code', 'equipment__name', 'name', 'tasks']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'next_due_date'
