"""
ERP/MES 연계 시스템 Serializers
"""
from rest_framework import serializers
from .models import ERPIntegration, IntegrationHistory, ManualQualityInput
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 간단 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class IntegrationHistorySerializer(serializers.ModelSerializer):
    """연계 이력 시리얼라이저"""
    system_name = serializers.CharField(source='integration.name', read_only=True)
    system_type = serializers.CharField(source='integration.system_type', read_only=True)
    sync_type_display = serializers.CharField(source='get_sync_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    triggered_by_name = serializers.CharField(source='triggered_by.username', read_only=True)

    class Meta:
        model = IntegrationHistory
        fields = [
            'id', 'sync_id', 'integration', 'system_name', 'system_type',
            'sync_type', 'sync_type_display', 'start_time', 'end_time',
            'duration_seconds', 'status', 'status_display',
            'records_processed', 'records_success', 'records_failed',
            'data_types', 'error_message', 'error_details',
            'triggered_by', 'triggered_by_name', 'notes', 'created_at'
        ]


class ERPIntegrationListSerializer(serializers.ModelSerializer):
    """ERP 연계 목록 조회용 시리얼라이저"""
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    auth_method_display = serializers.CharField(source='get_auth_method_display', read_only=True)

    class Meta:
        model = ERPIntegration
        fields = [
            'id', 'name', 'system_type', 'system_type_display',
            'description', 'endpoint_url', 'auth_method',
            'auth_method_display', 'sync_frequency_minutes',
            'auto_sync', 'last_sync', 'next_sync', 'status',
            'status_display', 'is_active', 'created_at', 'updated_at'
        ]


class ERPIntegrationDetailSerializer(serializers.ModelSerializer):
    """ERP 연계 상세 조회용 시리얼라이저"""
    system_type_display = serializers.CharField(source='get_system_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    auth_method_display = serializers.CharField(source='get_auth_method_display', read_only=True)
    sync_histories = IntegrationHistorySerializer(many=True, read_only=True)

    class Meta:
        model = ERPIntegration
        fields = [
            'id', 'name', 'system_type', 'system_type_display',
            'description', 'endpoint_url', 'auth_method',
            'auth_method_display', 'api_key', 'username', 'password',
            'access_token', 'refresh_token', 'sync_frequency_minutes',
            'auto_sync', 'last_sync', 'next_sync', 'data_types',
            'status', 'status_display', 'last_error', 'is_active',
            'sync_histories', 'created_at', 'updated_at'
        ]


class ERPIntegrationCreateSerializer(serializers.ModelSerializer):
    """ERP 연계 생성용 시리얼라이저"""
    class Meta:
        model = ERPIntegration
        fields = [
            'name', 'system_type', 'description', 'endpoint_url',
            'auth_method', 'api_key', 'username', 'password',
            'sync_frequency_minutes', 'auto_sync', 'data_types'
        ]


class ERPIntegrationUpdateSerializer(serializers.ModelSerializer):
    """ERP 연계 수정용 시리얼라이저"""
    class Meta:
        model = ERPIntegration
        fields = [
            'name', 'description', 'endpoint_url', 'auth_method',
            'api_key', 'username', 'password', 'sync_frequency_minutes',
            'auto_sync', 'data_types', 'status', 'is_active'
        ]


class ManualQualityInputListSerializer(serializers.ModelSerializer):
    """자체 입력 목록 조회용 시리얼라이저"""
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)

    class Meta:
        model = ManualQualityInput
        fields = [
            'id', 'record_number', 'inspection_type', 'inspection_type_display',
            'inspection_date', 'product_code', 'product_name', 'batch_number',
            'lot_number', 'sample_size', 'defect_count', 'defect_rate',
            'department', 'status', 'status_display', 'inspector',
            'inspector_name', 'created_at'
        ]


class ManualQualityInputDetailSerializer(serializers.ModelSerializer):
    """자체 입력 상세 조회용 시리얼라이저"""
    inspection_type_display = serializers.CharField(source='get_inspection_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    inspector_name = serializers.CharField(source='inspector.username', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = ManualQualityInput
        fields = [
            'id', 'record_number', 'inspection_type', 'inspection_type_display',
            'inspection_date', 'product_code', 'product_name', 'batch_number',
            'lot_number', 'sample_size', 'defect_count', 'defect_rate',
            'characteristics', 'defect_details', 'department', 'status',
            'status_display', 'inspector', 'inspector_name', 'approved_by',
            'approved_by_name', 'approved_at', 'notes', 'attachments',
            'created_at', 'updated_at'
        ]


class ManualQualityInputCreateSerializer(serializers.ModelSerializer):
    """자체 입력 생성용 시리얼라이저"""
    class Meta:
        model = ManualQualityInput
        fields = [
            'record_number', 'inspection_type', 'inspection_date',
            'product_code', 'product_name', 'batch_number', 'lot_number',
            'sample_size', 'defect_count', 'defect_rate', 'characteristics',
            'defect_details', 'department', 'notes', 'attachments'
        ]

    def create(self, validated_data):
        # inspector는 현재 로그인한 사용자로 자동 설정
        validated_data['inspector'] = self.context['request'].user
        return super().create(validated_data)


class ManualQualityInputUpdateSerializer(serializers.ModelSerializer):
    """자체 입력 수정용 시리얼라이저"""
    class Meta:
        model = ManualQualityInput
        fields = [
            'inspection_type', 'inspection_date', 'product_name',
            'sample_size', 'defect_count', 'defect_rate',
            'characteristics', 'defect_details', 'status', 'notes',
            'attachments'
        ]
