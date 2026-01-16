"""
치공구 관리 시스템 Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Tool, ToolRepairHistory
from .serializers import (
    ToolListSerializer,
    ToolDetailSerializer,
    ToolCreateSerializer,
    ToolUpdateSerializer,
    ToolRepairHistorySerializer
)


class ToolViewSet(viewsets.ModelViewSet):
    """치공구 ViewSet"""
    queryset = Tool.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'type', 'department']
    search_fields = ['code', 'name', 'manufacturer', 'model', 'serial_number']
    ordering_fields = ['code', 'name', 'purchase_date', 'usage_count']
    ordering = ['code']

    def get_serializer_class(self):
        if self.action == 'list':
            return ToolListSerializer
        elif self.action == 'create':
            return ToolCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ToolUpdateSerializer
        return ToolDetailSerializer

    @action(detail=True, methods=['get'])
    def prediction(self, request, pk=None):
        """치공구 수명 예측"""
        tool = self.get_object()
        usage_pct = tool.usage_percentage

        # 예측 로직
        if usage_pct >= 97:
            risk_level = 'CRITICAL'
            recommendation = '즉시 교체 필요'
        elif usage_pct >= 90:
            risk_level = 'URGENT'
            recommendation = '긴급 교체 권장'
        elif usage_pct >= 70:
            risk_level = 'WARNING'
            recommendation = '교체 준비 필요'
        else:
            risk_level = 'NORMAL'
            recommendation = '정상 사용 가능'

        return Response({
            'tool_code': tool.code,
            'tool_name': tool.name,
            'usage_percentage': round(usage_pct, 2),
            'predicted_remaining_days': tool.predicted_remaining_days,
            'risk_level': risk_level,
            'recommendation': recommendation,
            'optimal_replacement_date': tool.optimal_replacement_date
        })

    @action(detail=True, methods=['get'])
    def repair_histories(self, request, pk=None):
        """치공구 수리 이력 조회"""
        tool = self.get_object()
        repairs = tool.repair_histories.all()
        serializer = ToolRepairHistorySerializer(repairs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """치공구 통계"""
        total = Tool.objects.count()
        by_status = {}
        for status_choice in Tool.Status.choices:
            status_key = status_choice[0]
            by_status[status_key] = Tool.objects.filter(
                status=status_key
            ).count()

        from django.db.models import Avg
        avg_usage_pct = 0
        for tool in Tool.objects.all():
            avg_usage_pct += tool.usage_percentage
        avg_usage_pct = avg_usage_pct / total if total > 0 else 0

        replacement_needed = Tool.objects.filter(
            predicted_remaining_days__lte=7
        ).count()

        return Response({
            'total': total,
            'by_status': by_status,
            'avg_usage_percentage': round(avg_usage_pct, 2),
            'replacement_needed': replacement_needed
        })
