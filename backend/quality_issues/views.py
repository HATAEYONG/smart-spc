"""
품질 이슈 시스템 Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import QualityIssue, IssueAnalysis4M, ProblemSolvingStep
from .serializers import (
    QualityIssueListSerializer,
    QualityIssueDetailSerializer,
    QualityIssueCreateSerializer,
    QualityIssueUpdateSerializer,
    IssueAnalysis4MSerializer,
    ProblemSolvingStepSerializer
)


class QualityIssueViewSet(viewsets.ModelViewSet):
    """품질 이슈 ViewSet"""
    queryset = QualityIssue.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'severity', 'department']
    search_fields = ['issue_number', 'title', 'product_code', 'product_name', 'defect_type']
    ordering_fields = ['reported_date', 'severity', 'status']
    ordering = ['-reported_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return QualityIssueListSerializer
        elif self.action == 'create':
            return QualityIssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return QualityIssueUpdateSerializer
        return QualityIssueDetailSerializer

    @action(detail=True, methods=['get'])
    def analyses_4m(self, request, pk=None):
        """4M 분석 조회"""
        issue = self.get_object()
        analyses = issue.analyses_4m.all()
        serializer = IssueAnalysis4MSerializer(analyses, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'put'])
    def set_analyses_4m(self, request, pk=None):
        """4M 분석 설정/수정"""
        issue = self.get_object()

        # 기존 분석 삭제
        issue.analyses_4m.all().delete()

        # 새로운 분석 생성
        analyses_data = request.data.get('analyses', [])
        for analysis_data in analyses_data:
            IssueAnalysis4M.objects.create(
                issue=issue,
                category=analysis_data.get('category'),
                description=analysis_data.get('description')
            )

        return Response({'status': 'analyses updated'})

    @action(detail=True, methods=['get'])
    def solving_steps(self, request, pk=None):
        """8단계 문제 해결 조회"""
        issue = self.get_object()
        steps = issue.solving_steps.all()
        serializer = ProblemSolvingStepSerializer(steps, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'put'])
    def set_solving_steps(self, request, pk=None):
        """8단계 문제 해결 설정/수정"""
        issue = self.get_object()

        # 기존 단계 삭제
        issue.solving_steps.all().delete()

        # 새로운 단계 생성
        steps_data = request.data.get('steps', [])
        for step_data in steps_data:
            ProblemSolvingStep.objects.create(
                issue=issue,
                step_number=step_data.get('step_number'),
                step_name=step_data.get('step_name'),
                content=step_data.get('content'),
                completed=step_data.get('completed', False)
            )

        return Response({'status': 'steps updated'})

    @action(detail=True, methods=['post'])
    def complete_step(self, request, pk=None):
        """단계 완료 처리"""
        issue = self.get_object()
        step_number = request.data.get('step_number')

        try:
            step = issue.solving_steps.get(step_number=step_number)
            step.completed = True
            step.save()
            serializer = ProblemSolvingStepSerializer(step)
            return Response(serializer.data)
        except ProblemSolvingStep.DoesNotExist:
            return Response(
                {'error': 'Step not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """품질 이슈 통계"""
        total = QualityIssue.objects.count()
        by_status = {}
        for status_choice in QualityIssue.Status.choices:
            status_key = status_choice[0]
            by_status[status_key] = QualityIssue.objects.filter(
                status=status_key
            ).count()

        by_severity = {}
        for severity_choice in QualityIssue.Severity.choices:
            severity_key = severity_choice[0]
            by_severity[severity_key] = QualityIssue.objects.filter(
                severity=severity_key
            ).count()

        open_issues = QualityIssue.objects.filter(
            status__in=[QualityIssue.Status.OPEN, QualityIssue.Status.INVESTIGATING, QualityIssue.Status.IN_PROGRESS]
        ).count()

        return Response({
            'total': total,
            'by_status': by_status,
            'by_severity': by_severity,
            'open_issues': open_issues
        })
