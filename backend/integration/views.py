"""
ERP/MES 연계 시스템 Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import ERPIntegration, IntegrationHistory, ManualQualityInput
from .serializers import (
    ERPIntegrationListSerializer,
    ERPIntegrationDetailSerializer,
    ERPIntegrationCreateSerializer,
    ERPIntegrationUpdateSerializer,
    IntegrationHistorySerializer,
    ManualQualityInputListSerializer,
    ManualQualityInputDetailSerializer,
    ManualQualityInputCreateSerializer,
    ManualQualityInputUpdateSerializer
)


class ERPIntegrationViewSet(viewsets.ModelViewSet):
    """ERP 연계 ViewSet"""
    queryset = ERPIntegration.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['system_type', 'status', 'is_active']
    search_fields = ['name', 'description', 'endpoint_url']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return ERPIntegrationListSerializer
        elif self.action == 'create':
            return ERPIntegrationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ERPIntegrationUpdateSerializer
        return ERPIntegrationDetailSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """연결 테스트"""
        integration = self.get_object()

        # 실제 연결 테스트 로직 (여기서는 시뮬레이션)
        try:
            # TODO: 실제 API 연결 테스트 구현
            integration.status = ERPIntegration.Status.CONNECTED
            integration.last_error = ''
            integration.save()

            return Response({
                'status': 'success',
                'message': '연결 성공'
            })
        except Exception as e:
            integration.status = ERPIntegration.Status.ERROR
            integration.last_error = str(e)
            integration.save()

            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """수동 동기화 실행"""
        integration = self.get_object()

        # 동기화 ID 생성
        from datetime import datetime
        sync_id = f"SYNC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # 동기화 이력 생성
        history = IntegrationHistory.objects.create(
            sync_id=sync_id,
            integration=integration,
            sync_type=IntegrationHistory.SyncType.MANUAL,
            start_time=datetime.now(),
            status=IntegrationHistory.Status.IN_PROGRESS,
            triggered_by=request.user if request.user.is_authenticated else None
        )

        # 실제 동기화 로직 (여기서는 시뮬레이션)
        try:
            # TODO: 실제 동기화 로직 구현
            import time
            time.sleep(1)  # 시뮬레이션

            history.end_time = datetime.now()
            history.duration_seconds = int((history.end_time - history.start_time).total_seconds())
            history.status = IntegrationHistory.Status.SUCCESS
            history.records_processed = 100
            history.records_success = 100
            history.records_failed = 0
            history.data_types = integration.data_types
            history.save()

            integration.last_sync = datetime.now()
            integration.save()

            serializer = IntegrationHistorySerializer(history)
            return Response(serializer.data)

        except Exception as e:
            history.end_time = datetime.now()
            history.duration_seconds = int((history.end_time - history.start_time).total_seconds())
            history.status = IntegrationHistory.Status.FAILED
            history.error_message = str(e)
            history.save()

            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def sync_history(self, request, pk=None):
        """동기화 이력 조회"""
        integration = self.get_object()
        histories = integration.sync_histories.all()[:50]  # 최근 50건
        serializer = IntegrationHistorySerializer(histories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """연계 통계"""
        total = ERPIntegration.objects.count()
        active = ERPIntegration.objects.filter(is_active=True).count()
        connected = ERPIntegration.objects.filter(status=ERPIntegration.Status.CONNECTED).count()

        recent_syncs = IntegrationHistory.objects.filter(
            status=IntegrationHistory.Status.SUCCESS
        ).count()

        failed_syncs = IntegrationHistory.objects.filter(
            status=IntegrationHistory.Status.FAILED
        ).count()

        return Response({
            'total': total,
            'active': active,
            'connected': connected,
            'recent_syncs': recent_syncs,
            'failed_syncs': failed_syncs
        })


class IntegrationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """연계 이력 ViewSet (읽기 전용)"""
    queryset = IntegrationHistory.objects.all()
    serializer_class = IntegrationHistorySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['integration', 'sync_type', 'status']
    search_fields = ['sync_id']
    ordering_fields = ['start_time']
    ordering = ['-start_time']


class ManualQualityInputViewSet(viewsets.ModelViewSet):
    """자체 입력 ViewSet"""
    queryset = ManualQualityInput.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['inspection_type', 'status', 'department']
    search_fields = ['record_number', 'product_code', 'product_name', 'batch_number', 'lot_number']
    ordering_fields = ['inspection_date', 'created_at']
    ordering = ['-inspection_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return ManualQualityInputListSerializer
        elif self.action == 'create':
            return ManualQualityInputCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ManualQualityInputUpdateSerializer
        return ManualQualityInputDetailSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """승인 처리"""
        record = self.get_object()
        record.status = ManualQualityInput.Status.APPROVED
        record.approved_by = request.user
        from datetime import datetime
        record.approved_at = datetime.now()
        record.save()

        serializer = ManualQualityInputDetailSerializer(record)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """반려 처리"""
        record = self.get_object()
        record.status = ManualQualityInput.Status.REJECTED
        record.approved_by = request.user
        from datetime import datetime
        record.approved_at = datetime.now()
        record.notes = request.data.get('notes', record.notes)
        record.save()

        serializer = ManualQualityInputDetailSerializer(record)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """자체 입력 통계"""
        total = ManualQualityInput.objects.count()
        by_type = {}
        for type_choice in ManualQualityInput.InspectionType.choices:
            type_key = type_choice[0]
            by_type[type_key] = ManualQualityInput.objects.filter(
                inspection_type=type_key
            ).count()

        by_status = {}
        for status_choice in ManualQualityInput.Status.choices:
            status_key = status_choice[0]
            by_status[status_key] = ManualQualityInput.objects.filter(
                status=status_key
            ).count()

        from django.db.models import Avg
        avg_defect_rate = ManualQualityInput.objects.aggregate(
            avg_rate=Avg('defect_rate')
        )['avg_rate'] or 0

        return Response({
            'total': total,
            'by_type': by_type,
            'by_status': by_status,
            'avg_defect_rate': round(avg_defect_rate, 2)
        })
