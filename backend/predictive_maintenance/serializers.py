from rest_framework import serializers
from .models import Equipment, SensorData, MaintenanceRecord, FailurePrediction, MaintenancePlan


class EquipmentSerializer(serializers.ModelSerializer):
    """설비 시리얼라이저"""

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'


class EquipmentListSerializer(serializers.ModelSerializer):
    """설비 목록용 시리얼라이저"""

    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    maintenance_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Equipment
        fields = [
            'id', 'code', 'name', 'category', 'category_display',
            'status', 'status_display', 'location', 'health_score',
            'failure_probability', 'availability_current', 'maintenance_overdue'
        ]

    def get_maintenance_overdue(self, obj):
        from django.utils import timezone
        if obj.next_maintenance_date:
            return obj.next_maintenance_date < timezone.now().date()
        return False


class SensorDataSerializer(serializers.ModelSerializer):
    """센서 데이터 시리얼라이저"""

    sensor_type_display = serializers.CharField(source='get_sensor_type_display', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)

    class Meta:
        model = SensorData
        fields = '__all__'


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    """점검/수리 이력 시리얼라이저"""

    record_type_display = serializers.CharField(source='get_record_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    technician_name = serializers.CharField(source='technician.username', read_only=True)

    class Meta:
        model = MaintenanceRecord
        fields = '__all__'


class MaintenanceRecordCreateSerializer(serializers.ModelSerializer):
    """점검/수리 이력 생성용 시리얼라이저"""

    class Meta:
        model = MaintenanceRecord
        fields = [
            'equipment', 'record_type', 'title', 'description',
            'scheduled_date', 'technician', 'estimated_duration'
        ]


class FailurePredictionSerializer(serializers.ModelSerializer):
    """고장 예측 시리얼라이저"""

    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.username', read_only=True)

    class Meta:
        model = FailurePrediction
        fields = '__all__'


class FailurePredictionCreateSerializer(serializers.ModelSerializer):
    """고장 예측 생성용 시리얼라이저"""

    class Meta:
        model = FailurePrediction
        fields = [
            'equipment', 'predicted_failure_date', 'failure_probability',
            'confidence', 'severity', 'potential_causes', 'recommended_actions'
        ]


class MaintenancePlanSerializer(serializers.ModelSerializer):
    """예방 보전 계획 시리얼라이저"""

    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    equipment_code = serializers.CharField(source='equipment.code', read_only=True)
    equipment_name = serializers.CharField(source='equipment.name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    days_until_due = serializers.SerializerMethodField()

    class Meta:
        model = MaintenancePlan
        fields = '__all__'

    def get_days_until_due(self, obj):
        from django.utils import timezone
        if obj.next_due_date:
            today = timezone.now().date()
            delta = obj.next_due_date - today
            return delta.days
        return None


class MaintenancePlanCreateSerializer(serializers.ModelSerializer):
    """예방 보전 계획 생성용 시리얼라이저"""

    class Meta:
        model = MaintenancePlan
        fields = [
            'equipment', 'name', 'description', 'frequency',
            'tasks', 'estimated_duration', 'estimated_cost',
            'start_date', 'assigned_to'
        ]
