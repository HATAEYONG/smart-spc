"""
작업지시 관리 시스템 Serializers
"""
from rest_framework import serializers
from .models import WorkOrder, WorkOrderTool, WorkOrderProgress
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 간단 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class WorkOrderToolSerializer(serializers.ModelSerializer):
    """작업지시-치공구 연결 시리얼라이저"""
    tool_code = serializers.CharField(source='tool.code', read_only=True)
    tool_name = serializers.CharField(source='tool.name', read_only=True)

    class Meta:
        model = WorkOrderTool
        fields = [
            'id', 'tool', 'tool_code', 'tool_name',
            'quantity_required', 'usage_hours'
        ]


class WorkOrderProgressSerializer(serializers.ModelSerializer):
    """작업지시 진행 상황 시리얼라이저"""
    reported_by_name = serializers.CharField(source='reported_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = WorkOrderProgress
        fields = [
            'id', 'timestamp', 'status', 'status_display',
            'progress_percentage', 'completed_quantity', 'notes',
            'reported_by', 'reported_by_name'
        ]


class WorkOrderListSerializer(serializers.ModelSerializer):
    """작업지시 목록 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_number', 'product_code', 'product_name',
            'quantity', 'status', 'status_display', 'priority',
            'priority_display', 'start_date', 'target_end_date',
            'assigned_to', 'assigned_to_name', 'equipment',
            'equipment_code', 'equipment_name', 'progress_percentage',
            'predicted_completion_risk'
        ]


class WorkOrderDetailSerializer(serializers.ModelSerializer):
    """작업지시 상세 조회용 시리얼라이저"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    equipment_health_score = serializers.IntegerField(source='equipment.health_score', read_only=True)
    work_order_tools = WorkOrderToolSerializer(many=True, read_only=True)
    progress_logs = WorkOrderProgressSerializer(many=True, read_only=True)

    class Meta:
        model = WorkOrder
        fields = [
            'id', 'order_number', 'product_code', 'product_name',
            'quantity', 'status', 'status_display', 'priority',
            'priority_display', 'start_date', 'target_end_date',
            'actual_end_date', 'equipment', 'equipment_code',
            'equipment_name', 'equipment_health_score', 'assigned_to',
            'assigned_to_name', 'created_by', 'created_by_name',
            'progress_percentage', 'completed_quantity',
            'predicted_completion_risk', 'risk_reasons',
            'estimated_cost', 'actual_cost', 'notes',
            'work_order_tools', 'progress_logs',
            'created_at', 'updated_at'
        ]


class WorkOrderCreateSerializer(serializers.ModelSerializer):
    """작업지시 생성용 시리얼라이저"""
    class Meta:
        model = WorkOrder
        fields = [
            'order_number', 'product_code', 'product_name', 'quantity',
            'priority', 'start_date', 'target_end_date', 'equipment',
            'assigned_to', 'estimated_cost', 'notes'
        ]

    def create(self, validated_data):
        # created_by는 현재 로그인한 사용자로 자동 설정
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class WorkOrderUpdateSerializer(serializers.ModelSerializer):
    """작업지시 수정용 시리얼라이저"""
    class Meta:
        model = WorkOrder
        fields = [
            'product_name', 'quantity', 'status', 'priority',
            'target_end_date', 'actual_end_date', 'equipment',
            'assigned_to', 'progress_percentage', 'completed_quantity',
            'predicted_completion_risk', 'risk_reasons',
            'estimated_cost', 'actual_cost', 'notes'
        ]


class WorkOrderProgressCreateSerializer(serializers.ModelSerializer):
    """작업지시 진행 상황 생성용 시리얼라이저"""
    class Meta:
        model = WorkOrderProgress
        fields = [
            'work_order', 'status', 'progress_percentage',
            'completed_quantity', 'notes'
        ]

    def create(self, validated_data):
        # reported_by는 현재 로그인한 사용자로 자동 설정
        validated_data['reported_by'] = self.context['request'].user

        # 작업지시 진행률 업데이트
        work_order = validated_data['work_order']
        work_order.progress_percentage = validated_data['progress_percentage']
        work_order.completed_quantity = validated_data['completed_quantity']
        work_order.status = validated_data['status']
        work_order.save()

        return super().create(validated_data)
