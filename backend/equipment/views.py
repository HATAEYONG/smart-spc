"""
설비 관리 시스템 Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Equipment, EquipmentPart, EquipmentManual, EquipmentRepairHistory, PreventiveMaintenance
from .serializers import (
    EquipmentListSerializer,
    EquipmentDetailSerializer,
    EquipmentCreateSerializer,
    EquipmentUpdateSerializer,
    EquipmentPartSerializer,
    EquipmentManualSerializer,
    EquipmentRepairHistorySerializer,
    PreventiveMaintenanceSerializer
)


class EquipmentViewSet(viewsets.ModelViewSet):
    """설비 ViewSet"""
    queryset = Equipment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'department']
    search_fields = ['code', 'name', 'manufacturer', 'model', 'serial_number']
    ordering_fields = ['code', 'name', 'installation_date', 'health_score']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'list':
            return EquipmentListSerializer
        elif self.action == 'create':
            return EquipmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return EquipmentUpdateSerializer
        return EquipmentDetailSerializer

    @action(detail=True, methods=['get'])
    def health(self, request, pk=None):
        """설비 건강 점수 조회"""
        equipment = self.get_object()
        return Response({
            'health_score': equipment.health_score,
            'predicted_failure_days': equipment.predicted_failure_days,
            'status': 'good' if equipment.health_score >= 85 else 'warning' if equipment.health_score >= 60 else 'critical'
        })

    @action(detail=True, methods=['get'])
    def parts(self, request, pk=None):
        """설비 부품 조회"""
        equipment = self.get_object()
        parts = equipment.parts.all()
        serializer = EquipmentPartSerializer(parts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def manuals(self, request, pk=None):
        """설비 매뉴얼 조회"""
        equipment = self.get_object()
        manuals = equipment.manuals.all()
        serializer = EquipmentManualSerializer(manuals, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def repair_histories(self, request, pk=None):
        """설비 수리 이력 조회"""
        equipment = self.get_object()
        repairs = equipment.repair_histories.all()
        serializer = EquipmentRepairHistorySerializer(repairs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def pm_tasks(self, request, pk=None):
        """예방 보전 작업 조회"""
        equipment = self.get_object()
        tasks = equipment.pm_tasks.all()
        serializer = PreventiveMaintenanceSerializer(tasks, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """설비 통계"""
        total = Equipment.objects.count()
        by_status = {}
        for status_choice in Equipment.Status.choices:
            status_key = status_choice[0]
            by_status[status_key] = Equipment.objects.filter(
                status=status_key
            ).count()

        avg_health_score = Equipment.objects.aggregate(
            avg_health=models.Avg('health_score')
        )['avg_health_score'] or 0

        warning_equipment = Equipment.objects.filter(
            health_score__lt=85
        ).count()

        critical_equipment = Equipment.objects.filter(
            health_score__lt=60
        ).count()

        return Response({
            'total': total,
            'by_status': by_status,
            'avg_health_score': round(avg_health_score, 2),
            'warning_equipment': warning_equipment,
            'critical_equipment': critical_equipment
        })


class PreventiveMaintenanceViewSet(viewsets.ModelViewSet):
    """예방 보전 ViewSet"""
    queryset = PreventiveMaintenance.objects.all()
    serializer_class = PreventiveMaintenanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'frequency', 'priority', 'equipment']
    search_fields = ['task_number', 'task_name', 'description']
    ordering_fields = ['scheduled_date', 'priority', 'status']
    ordering = ['scheduled_date']

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """작업 완료 처리"""
        task = self.get_object()
        task.status = PreventiveMaintenance.Status.COMPLETED
        task.completion_notes = request.data.get('completion_notes', '')
        from datetime import date
        task.last_completed = date.today()
        task.save()

        serializer = PreventiveMaintenanceSerializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """지연된 작업 조회"""
        from datetime import date
        overdue_tasks = PreventiveMaintenance.objects.filter(
            scheduled_date__lt=date.today(),
            status__in=[PreventiveMaintenance.Status.PENDING, PreventiveMaintenance.Status.ASSIGNED]
        )
        serializer = PreventiveMaintenanceSerializer(overdue_tasks, many=True)
        return Response(serializer.data)
