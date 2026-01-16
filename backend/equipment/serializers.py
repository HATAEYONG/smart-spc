"""
설비 관리 시스템 Serializers
"""
from rest_framework import serializers
from .models import Equipment, EquipmentPart, EquipmentManual, EquipmentRepairHistory, PreventiveMaintenance
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 간단 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class EquipmentPartSerializer(serializers.ModelSerializer):
    """설비 부품 시리얼라이저"""
    class Meta:
        model = EquipmentPart
        fields = [
            'id', 'code', 'name', 'part_number', 'specifications',
            'stock_quantity', 'min_stock', 'unit_price', 'supplier',
            'location', 'created_at', 'updated_at'
        ]


class EquipmentManualSerializer(serializers.ModelSerializer):
    """설비 매뉴얼 시리얼라이저"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    file_type_display = serializers.CharField(source='get_file_type_display', read_only=True)

    class Meta:
        model = EquipmentManual
        fields = [
            'id', 'title', 'file_type', 'file_type_display', 'file_path',
            'file_size', 'version', 'upload_date', 'uploaded_by',
            'uploaded_by_name', 'description', 'tags'
        ]


class EquipmentRepairHistorySerializer(serializers.ModelSerializer):
    """설비 수리 이력 시리얼라이저"""
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    repair_type_display = serializers.CharField(source='get_repair_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = EquipmentRepairHistory
        fields = [
            'id', 'repair_date', 'repair_type', 'repair_type_display',
            'description', 'status', 'status_display', 'reported_by',
            'reported_by_name', 'assigned_to', 'assigned_to_name',
            'parts_used', 'labor_cost', 'parts_cost', 'total_cost',
            'downtime_hours', 'notes', 'created_at', 'updated_at'
        ]


class PreventiveMaintenanceSerializer(serializers.ModelSerializer):
    """예방 보전 시리얼라이저"""
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)

    class Meta:
        model = PreventiveMaintenance
        fields = [
            'id', 'task_number', 'task_name', 'description',
            'frequency', 'frequency_display', 'scheduled_date',
            'status', 'status_display', 'assigned_to', 'assigned_to_name',
            'estimated_duration', 'priority', 'priority_display',
            'last_completed', 'next_due', 'completion_notes',
            'created_at', 'updated_at'
        ]


class EquipmentListSerializer(serializers.ModelSerializer):
    """설비 목록 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id', 'code', 'name', 'type', 'manufacturer', 'model',
            'location', 'status', 'status_display', 'department',
            'health_score', 'predicted_failure_days'
        ]


class EquipmentDetailSerializer(serializers.ModelSerializer):
    """설비 상세 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    parts = EquipmentPartSerializer(many=True, read_only=True)
    manuals = EquipmentManualSerializer(many=True, read_only=True)
    repair_histories = EquipmentRepairHistorySerializer(many=True, read_only=True)
    pm_tasks = PreventiveMaintenanceSerializer(many=True, read_only=True)

    class Meta:
        model = Equipment
        fields = [
            'id', 'code', 'name', 'type', 'manufacturer', 'model',
            'serial_number', 'location', 'installation_date', 'status',
            'status_display', 'department', 'cost', 'specifications',
            'health_score', 'predicted_failure_days', 'parts', 'manuals',
            'repair_histories', 'pm_tasks', 'created_at', 'updated_at'
        ]


class EquipmentCreateSerializer(serializers.ModelSerializer):
    """설비 생성용 시리얼라이저"""
    class Meta:
        model = Equipment
        fields = [
            'code', 'name', 'type', 'manufacturer', 'model',
            'serial_number', 'location', 'installation_date', 'status',
            'department', 'cost', 'specifications', 'health_score'
        ]


class EquipmentUpdateSerializer(serializers.ModelSerializer):
    """설비 수정용 시리얼라이저"""
    class Meta:
        model = Equipment
        fields = [
            'name', 'type', 'location', 'status', 'department',
            'health_score', 'predicted_failure_days', 'specifications'
        ]
