"""
작업지시 관리 시스템 Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import WorkOrder, WorkOrderTool, WorkOrderProgress
from .serializers import (
    WorkOrderListSerializer,
    WorkOrderDetailSerializer,
    WorkOrderCreateSerializer,
    WorkOrderUpdateSerializer,
    WorkOrderToolSerializer,
    WorkOrderProgressSerializer,
    WorkOrderProgressCreateSerializer
)


class WorkOrderViewSet(viewsets.ModelViewSet):
    """작업지시 ViewSet"""
    queryset = WorkOrder.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'equipment', 'assigned_to']
    search_fields = ['order_number', 'product_code', 'product_name']
    ordering_fields = ['start_date', 'target_end_date', 'priority', 'status']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return WorkOrderListSerializer
        elif self.action == 'create':
            return WorkOrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return WorkOrderUpdateSerializer
        return WorkOrderDetailSerializer

    @action(detail=True, methods=['get'])
    def analyze_risk(self, request, pk=None):
        """작업 완료 위험도 분석"""
        work_order = self.get_object()
        risk_reasons = []

        # 설비 건강 점수 확인
        if work_order.equipment:
            if work_order.equipment.health_score < 60:
                risk_reasons.append('설비 건강 점수 낮음 (60점 미만)')
                work_order.predicted_completion_risk = 'HIGH'
            elif work_order.equipment.health_score < 85:
                risk_reasons.append('설비 건강 점수 주의 (85점 미만)')
                if work_order.predicted_completion_risk != 'HIGH':
                    work_order.predicted_completion_risk = 'MEDIUM'

        # 할당된 치공구 확인
        work_order_tools = work_order.work_order_tools.all()
        for wot in work_order_tools:
            if wot.tool and wot.tool.predicted_remaining_days and wot.tool.predicted_remaining_days < 7:
                risk_reasons.append(f'치공구 {wot.tool.code} 잔존 수명 부족')
                work_order.predicted_completion_risk = 'HIGH'

        # 담당자 미할당
        if not work_order.assigned_to:
            risk_reasons.append('담당자 미할당')
            if work_order.predicted_completion_risk != 'HIGH':
                work_order.predicted_completion_risk = 'MEDIUM'

        # 진행률 확인
        if work_order.progress_percentage == 0:
            from datetime import date
            if work_order.start_date <= date.today():
                risk_reasons.append('시작일 지연仍未 시작')
                work_order.predicted_completion_risk = 'HIGH'

        work_order.risk_reasons = risk_reasons
        work_order.save()

        return Response({
            'order_number': work_order.order_number,
            'predicted_completion_risk': work_order.predicted_completion_risk,
            'risk_reasons': risk_reasons
        })

    @action(detail=True, methods=['get'])
    def progress_logs(self, request, pk=None):
        """진행 상황 로그 조회"""
        work_order = self.get_object()
        logs = work_order.progress_logs.all()
        serializer = WorkOrderProgressSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_progress(self, request, pk=None):
        """진행 상황 추가"""
        work_order = self.get_object()
        serializer = WorkOrderProgressCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(work_order=work_order)

            # 작업지시 진행률 업데이트
            work_order.progress_percentage = serializer.data['progress_percentage']
            work_order.completed_quantity = serializer.data['completed_quantity']
            work_order.status = serializer.data['status']
            if work_order.progress_percentage >= 100:
                from datetime import date
                work_order.actual_end_date = date.today()
            work_order.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """작업지시 통계"""
        total = WorkOrder.objects.count()
        by_status = {}
        for status_choice in WorkOrder.Status.choices:
            status_key = status_choice[0]
            by_status[status_key] = WorkOrder.objects.filter(
                status=status_key
            ).count()

        by_priority = {}
        for priority_choice in WorkOrder.Priority.choices:
            priority_key = priority_choice[0]
            by_priority[priority_key] = WorkOrder.objects.filter(
                priority=priority_key
            ).count()

        high_risk = WorkOrder.objects.filter(
            predicted_completion_risk='HIGH'
        ).count()

        from datetime import date
        overdue = WorkOrder.objects.filter(
            target_end_date__lt=date.today(),
            status__in=[WorkOrder.Status.PENDING, WorkOrder.Status.IN_PROGRESS]
        ).count()

        return Response({
            'total': total,
            'by_status': by_status,
            'by_priority': by_priority,
            'high_risk': high_risk,
            'overdue': overdue
        })


class WorkOrderToolViewSet(viewsets.ModelViewSet):
    """작업지시-치공구 연결 ViewSet"""
    queryset = WorkOrderTool.objects.all()
    serializer_class = WorkOrderToolSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['work_order', 'tool']
    ordering_fields = ['work_order', 'tool']
    ordering = ['work_order']
