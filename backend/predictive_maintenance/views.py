from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.utils import timezone

from .models import Equipment, SensorData, MaintenanceRecord, FailurePrediction, MaintenancePlan
from .serializers import (
    EquipmentSerializer, EquipmentListSerializer,
    SensorDataSerializer,
    MaintenanceRecordSerializer, MaintenanceRecordCreateSerializer,
    FailurePredictionSerializer, FailurePredictionCreateSerializer,
    MaintenancePlanSerializer, MaintenancePlanCreateSerializer
)


class EquipmentViewSet(viewsets.ModelViewSet):
    """설비 ViewSet"""

    queryset = Equipment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['code', 'name', 'location']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return EquipmentListSerializer
        return EquipmentSerializer

    @action(detail=True, methods=['get'])
    def sensor_data(self, request, pk=None):
        """센서 데이터 조회"""
        equipment = self.get_object()
        sensor_type = request.query_params.get('sensor_type')
        hours = int(request.query_params.get('hours', 24))

        queryset = equipment.sensor_data.all()
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)

        from django.utils import timezone
        from datetime import timedelta
        cutoff_time = timezone.now() - timedelta(hours=hours)
        queryset = queryset.filter(timestamp__gte=cutoff_time)

        serializer = SensorDataSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        """점검 이력 조회"""
        equipment = self.get_object()
        records = equipment.maintenance_records.all()

        page = self.paginate_queryset(records)
        if page is not None:
            serializer = MaintenanceRecordSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MaintenanceRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def predictions(self, request, pk=None):
        """고장 예측 조회"""
        equipment = self.get_object()
        predictions = equipment.failure_predictions.all()

        page = self.paginate_queryset(predictions)
        if page is not None:
            serializer = FailurePredictionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = FailurePredictionSerializer(predictions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """설비 대시보드 데이터"""
        total_equipment = Equipment.objects.count()
        operational = Equipment.objects.filter(status='OPERATIONAL').count()
        maintenance = Equipment.objects.filter(status='MAINTENANCE').count()
        breakdown = Equipment.objects.filter(status='BREAKDOWN').count()

        # 고장 위험 설비
        high_risk = Equipment.objects.filter(
            failure_probability__gte=70
        ).count()

        # 가동률 평균
        avg_availability = Equipment.objects.aggregate(
            avg=Avg('availability_current')
        )['avg'] or 0

        # 최근 센서 데이터
        recent_sensor_data = SensorData.objects.select_related('equipment').order_by('-timestamp')[:10]

        # 긴급 예측
        critical_predictions = FailurePrediction.objects.filter(
            severity='CRITICAL',
            is_acknowledged=False
        ).select_related('equipment').order_by('-predicted_failure_date')[:5]

        data = {
            'total_equipment': total_equipment,
            'operational': operational,
            'maintenance': maintenance,
            'breakdown': breakdown,
            'high_risk': high_risk,
            'avg_availability': round(avg_availability, 2),
            'recent_sensor_data': SensorDataSerializer(recent_sensor_data, many=True).data,
            'critical_predictions': FailurePredictionSerializer(critical_predictions, many=True).data,
        }

        return Response(data)


class SensorDataViewSet(viewsets.ModelViewSet):
    """센서 데이터 ViewSet"""

    queryset = SensorData.objects.select_related('equipment').all()
    serializer_class = SensorDataSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'sensor_type', 'is_normal']
    search_fields = ['sensor_id']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """최신 센서 데이터"""
        equipment_id = request.query_params.get('equipment')
        sensor_type = request.query_params.get('sensor_type')

        queryset = self.queryset
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)
        if sensor_type:
            queryset = queryset.filter(sensor_type=sensor_type)

        # 그룹별 최신 데이터
        from django.db.models import Max
        latest_ids = queryset.values('equipment', 'sensor_type').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)

        queryset = self.queryset.filter(id__in=latest_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    """점검/수리 이력 ViewSet"""

    queryset = MaintenanceRecord.objects.select_related('equipment', 'technician').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'record_type', 'status']
    search_fields = ['title', 'description', 'work_performed']
    ordering_fields = ['scheduled_date', 'created_at']
    ordering = ['-scheduled_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return MaintenanceRecordCreateSerializer
        return MaintenanceRecordSerializer

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """점검 시작"""
        record = self.get_object()
        if record.status != 'SCHEDULED':
            return Response(
                {'error': 'Only scheduled maintenance can be started'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.status = 'IN_PROGRESS'
        record.started_at = timezone.now()
        record.save()

        serializer = self.get_serializer(record)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """점검 완료"""
        record = self.get_object()
        if record.status != 'IN_PROGRESS':
            return Response(
                {'error': 'Only in-progress maintenance can be completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        record.status = 'COMPLETED'
        record.completed_at = timezone.now()

        # 수행 작업 등
        work_performed = request.data.get('work_performed')
        parts_replaced = request.data.get('parts_replaced')
        root_cause = request.data.get('root_cause')
        recommendations = request.data.get('recommendations')
        labor_cost = request.data.get('labor_cost')
        parts_cost = request.data.get('parts_cost')

        if work_performed:
            record.work_performed = work_performed
        if parts_replaced:
            record.parts_replaced = parts_replaced
        if root_cause:
            record.root_cause = root_cause
        if recommendations:
            record.recommendations = recommendations
        if labor_cost:
            record.labor_cost = labor_cost
        if parts_cost:
            record.parts_cost = parts_cost

        # 총비용 계산
        if labor_cost or parts_cost:
            total = (labor_cost or 0) + (parts_cost or 0)
            record.total_cost = total

        record.save()

        # 설비 상태 업데이트
        equipment = record.equipment
        equipment.status = 'OPERATIONAL'
        equipment.last_maintenance_date = timezone.now().date()
        equipment.save()

        serializer = self.get_serializer(record)
        return Response(serializer.data)


class FailurePredictionViewSet(viewsets.ModelViewSet):
    """고장 예측 ViewSet"""

    queryset = FailurePrediction.objects.select_related('equipment', 'acknowledged_by').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'severity', 'is_acknowledged']
    search_fields = ['potential_causes', 'recommended_actions']
    ordering_fields = ['prediction_date', 'predicted_failure_date', 'failure_probability']
    ordering = ['-prediction_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return FailurePredictionCreateSerializer
        return FailurePredictionSerializer

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """예측 확인"""
        prediction = self.get_object()
        prediction.is_acknowledged = True
        prediction.acknowledged_by = request.user
        prediction.acknowledged_at = timezone.now()
        prediction.save()

        serializer = self.get_serializer(prediction)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """긴급 예측 조회"""
        predictions = self.queryset.filter(
            severity='CRITICAL',
            is_acknowledged=False
        )

        page = self.paginate_queryset(predictions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)


class MaintenancePlanViewSet(viewsets.ModelViewSet):
    """예방 보전 계획 ViewSet"""

    queryset = MaintenancePlan.objects.select_related('equipment', 'assigned_to').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['equipment', 'frequency', 'status']
    search_fields = ['name', 'description', 'tasks']
    ordering_fields = ['next_due_date', 'name']
    ordering = ['next_due_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return MaintenancePlanCreateSerializer
        return MaintenancePlanSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """계획 완료 처리"""
        plan = self.get_object()

        # 완료된 계획 기반으로 점검 이력 생성
        record = MaintenanceRecord.objects.create(
            equipment=plan.equipment,
            record_type='PREVENTIVE',
            title=f"{plan.name} - {timezone.now().strftime('%Y-%m-%d')}",
            description=plan.description,
            scheduled_date=timezone.now(),
            technician=plan.assigned_to,
            status='COMPLETED',
            completed_at=timezone.now(),
        )

        # 다음 예정일 계산
        if plan.frequency_days:
            from datetime import timedelta
            plan.next_due_date = timezone.now().date() + timedelta(days=plan.frequency_days)
            plan.last_performed_date = timezone.now().date()
            plan.save()

        serializer = MaintenanceRecordSerializer(record)
        return Response(serializer.data)
