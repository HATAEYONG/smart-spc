"""
치공구 관리 시스템 Serializers
"""
from rest_framework import serializers
from .models import Tool, ToolRepairHistory
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 간단 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ToolRepairHistorySerializer(serializers.ModelSerializer):
    """치공구 수리 이력 시리얼라이저"""
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    repair_type_display = serializers.CharField(source='get_repair_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ToolRepairHistory
        fields = [
            'id', 'repair_date', 'repair_type', 'repair_type_display',
            'description', 'status', 'status_display', 'reported_by',
            'reported_by_name', 'assigned_to', 'assigned_to_name',
            'labor_cost', 'parts_cost', 'total_cost', 'downtime_hours',
            'notes', 'created_at', 'updated_at'
        ]


class ToolListSerializer(serializers.ModelSerializer):
    """치공구 목록 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    usage_percentage = serializers.ReadOnlyField()
    replacement_urgency = serializers.ReadOnlyField()

    class Meta:
        model = Tool
        fields = [
            'id', 'code', 'name', 'type', 'manufacturer', 'model',
            'location', 'status', 'status_display', 'department',
            'expected_life_days', 'predicted_remaining_days',
            'usage_count', 'usage_percentage', 'replacement_urgency',
            'optimal_replacement_date'
        ]


class ToolDetailSerializer(serializers.ModelSerializer):
    """치공구 상세 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    usage_percentage = serializers.ReadOnlyField()
    replacement_urgency = serializers.ReadOnlyField()
    repair_histories = ToolRepairHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Tool
        fields = [
            'id', 'code', 'name', 'type', 'manufacturer', 'model',
            'serial_number', 'location', 'purchase_date', 'status',
            'status_display', 'department', 'cost', 'specifications',
            'expected_life_days', 'predicted_remaining_days',
            'usage_count', 'total_usage_hours', 'usage_percentage',
            'replacement_urgency', 'optimal_replacement_date',
            'last_replacement_date', 'repair_histories',
            'created_at', 'updated_at'
        ]


class ToolCreateSerializer(serializers.ModelSerializer):
    """치공구 생성용 시리얼라이저"""
    class Meta:
        model = Tool
        fields = [
            'code', 'name', 'type', 'manufacturer', 'model',
            'serial_number', 'location', 'purchase_date', 'status',
            'department', 'cost', 'specifications',
            'expected_life_days', 'predicted_remaining_days'
        ]


class ToolUpdateSerializer(serializers.ModelSerializer):
    """치공구 수정용 시리얼라이저"""
    class Meta:
        model = Tool
        fields = [
            'name', 'status', 'location', 'department',
            'predicted_remaining_days', 'usage_count',
            'total_usage_hours', 'optimal_replacement_date',
            'last_replacement_date'
        ]
