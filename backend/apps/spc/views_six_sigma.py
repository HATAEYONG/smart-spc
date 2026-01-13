"""
Six Sigma DMAIC API Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from apps.spc.models.six_sigma import (
    DMAICProject, DefinePhase, MeasurePhase, AnalyzePhase,
    ImprovePhase, ControlPhase, DMAICMilestone, DMAICDocument,
    DMAICRisk, StatisticalTool
)
from apps.sc c.serializers.six_sigma import (
    DMAICProjectListSerializer, DMAICProjectDetailSerializer,
    DefinePhaseSerializer, MeasurePhaseSerializer, AnalyzePhaseSerializer,
    ImprovePhaseSerializer, ControlPhaseSerializer, DMAICMilestoneSerializer,
    DMAICDocumentSerializer, DMAICRiskSerializer, StatisticalToolSerializer,
    DescriptiveStatsSerializer, HistogramSerializer, ParetoSerializer,
    BoxPlotSerializer, CorrelationSerializer, TTestSerializer,
    ANOVASerializer, CapabilityAnalysisSerializer, GageRRSerializer
)
from apps.spc.services.six_sigma_tools import SixSigmaAnalyzer


class DMAICProjectViewSet(viewsets.ModelViewSet):
    """DMAIC ?�로?�트 ViewSet"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = DMAICProject.objects.select_related(
            'champion', 'process_owner', 'created_by'
        ).prefetch_related('team_members')

        # ?�터�?        phase = self.request.query_params.get('phase')
        status_param = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')

        if phase:
            queryset = queryset.filter(phase=phase)
        if status_param:
            queryset = queryset.filter(status=status_param)
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return DMAICProjectListSerializer
        return DMAICProjectDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """DMAIC ?�?�보???�이??""
        projects = self.get_queryset()

        total_projects = projects.count()
        by_phase = {}
        for phase_choice, _ in DMAICProject.PHASE_CHOICES:
            by_phase[phase_choice] = projects.filter(phase=phase_choice).count()

        by_status = {}
        for status_choice, _ in DMAICProject.STATUS_CHOICES:
            by_status[status_choice] = projects.filter(status=status_choice).count()

        by_priority = {}
        for priority_choice, _ in DMAICProject.PRIORITY_CHOICES:
            by_priority[priority_choice] = projects.filter(priority=priority_choice).count()

        # 최근 ?�로?�트
        recent_projects = projects[:5]
        recent_data = DMAICProjectListSerializer(recent_projects, many=True).data

        return Response({
            'total_projects': total_projects,
            'by_phase': by_phase,
            'by_status': by_status,
            'by_priority': by_priority,
            'recent_projects': recent_data,
        })

    @action(detail=True, methods=['post'])
    def advance_phase(self, request, pk=None):
        """?�음 ?�계�?진행"""
        project = self.get_object()

        phase_order = ['DEFINE', 'MEASURE', 'ANALYZE', 'IMPROVE', 'CONTROL', 'CLOSED']
        current_index = phase_order.index(project.phase)

        if current_index < len(phase_order) - 1:
            project.phase = phase_order[current_index + 1]
            project.save()

            return Response({
                'message': f'Phase advanced to {project.phase}',
                'current_phase': project.phase,
                'progress': project.progress_percentage
            })

        return Response(
            {'error': 'Project is already in the final phase'},
            status=status.HTTP_400_BAD_REQUEST
        )


class DefinePhaseViewSet(viewsets.ModelViewSet):
    """Define ?�계 ViewSet"""
    serializer_class = DefinePhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DefinePhase.objects.select_related('project')


class MeasurePhaseViewSet(viewsets.ModelViewSet):
    """Measure ?�계 ViewSet"""
    serializer_class = MeasurePhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MeasurePhase.objects.select_related('project')


class AnalyzePhaseViewSet(viewsets.ModelViewSet):
    """Analyze ?�계 ViewSet"""
    serializer_class = AnalyzePhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return AnalyzePhase.objects.select_related('project')


class ImprovePhaseViewSet(viewsets.ModelViewSet):
    """Improve ?�계 ViewSet"""
    serializer_class = ImprovePhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ImprovePhase.objects.select_related('project')


class ControlPhaseViewSet(viewsets.ModelViewSet):
    """Control ?�계 ViewSet"""
    serializer_class = ControlPhaseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ControlPhase.objects.select_related('project')


class DMAICMilestoneViewSet(viewsets.ModelViewSet):
    """DMAIC 마일?�톤 ViewSet"""
    serializer_class = DMAICMilestoneSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DMAICMilestone.objects.select_related('project')


class DMAICDocumentViewSet(viewsets.ModelViewSet):
    """DMAIC 문서 ViewSet"""
    serializer_class = DMAICDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DMAICDocument.objects.select_related('project', 'uploaded_by')

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class DMAICRiskViewSet(viewsets.ModelViewSet):
    """DMAIC 리스??ViewSet"""
    serializer_class = DMAICRiskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DMAICRisk.objects.select_related('project', 'owner')


class StatisticalToolViewSet(viewsets.ModelViewSet):
    """?�계 ?�구 ViewSet - Minitab ?��???""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StatisticalTool.objects.select_related('project', 'created_by')

    def get_serializer_class(self):
        return StatisticalToolSerializer

    @action(detail=False, methods=['post'])
    def descriptive_statistics(self, request):
        """기술 ?�계 분석"""
        serializer = DescriptiveStatsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data['data']
        variable_name = serializer.validated_data.get('variable_name', 'Variable')

        result = SixSigmaAnalyzer.descriptive_statistics(data)

        return Response({
            'variable_name': variable_name,
            'analysis_type': 'Descriptive Statistics',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def histogram(self, request):
        """?�스?�그???�성"""
        serializer = HistogramSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data['data']
        bins = serializer.validated_data.get('bins', 10)
        variable_name = serializer.validated_data.get('variable_name', 'Variable')

        histogram = SixSigmaAnalyzer.histogram_data(data, bins)
        descriptive = SixSigmaAnalyzer.descriptive_statistics(data)

        return Response({
            'variable_name': variable_name,
            'analysis_type': 'Histogram',
            'histogram': histogram,
            'statistics': descriptive,
        })

    @action(detail=False, methods=['post'])
    def pareto(self, request):
        """?�레?�도 ?�성"""
        serializer = ParetoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        categories = serializer.validated_data['categories']
        values = serializer.validated_data['values']
        chart_title = serializer.validated_data.get('chart_title', 'Pareto Chart')

        result = SixSigmaAnalyzer.pareto_data(categories, values)

        return Response({
            'chart_title': chart_title,
            'analysis_type': 'Pareto Chart',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def box_plot(self, request):
        """?�자 ?�염 그림 ?�성"""
        serializer = BoxPlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        groups = serializer.validated_data['groups']

        result = SixSigmaAnalyzer.box_plot_data(groups)

        return Response({
            'analysis_type': 'Box Plot',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def correlation(self, request):
        """?��? 분석"""
        serializer = CorrelationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        x_data = serializer.validated_data['x_data']
        y_data = serializer.validated_data['y_data']
        x_label = serializer.validated_data.get('x_label', 'X')
        y_label = serializer.validated_data.get('y_label', 'Y')

        result = SixSigmaAnalyzer.correlation_analysis(x_data, y_data)

        return Response({
            'x_label': x_label,
            'y_label': y_label,
            'analysis_type': 'Correlation Analysis',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def t_test(self, request):
        """T-검??""
        serializer = TTestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = SixSigmaAnalyzer.t_test(
            sample1=serializer.validated_data['sample1'],
            sample2=serializer.validated_data.get('sample2'),
            mu0=serializer.validated_data.get('mu0', 0),
            test_type=serializer.validated_data.get('test_type', 'one_sample'),
            alpha=serializer.validated_data.get('alpha', 0.05),
        )

        return Response({
            'analysis_type': 'T-Test',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def anova(self, request):
        """?�원분산분석 (One-Way ANOVA)"""
        serializer = ANOVASerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        groups = serializer.validated_data['groups']
        alpha = serializer.validated_data.get('alpha', 0.05)

        result = SixSigmaAnalyzer.anova(groups, alpha)

        return Response({
            'analysis_type': 'One-Way ANOVA',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def capability_analysis(self, request):
        """공정?�력 분석"""
        serializer = CapabilityAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data['data']
        lsl = serializer.validated_data['lsl']
        usl = serializer.validated_data['usl']
        target = serializer.validated_data.get('target')

        result = SixSigmaAnalyzer.capability_analysis(data, lsl, usl, target)

        return Response({
            'analysis_type': 'Process Capability Analysis',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def gage_rr(self, request):
        """Gage R&R 분석"""
        serializer = GageRRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        measurements = serializer.validated_data['measurements']

        result = SixSigmaAnalyzer.gage_rr(measurements)

        return Response({
            'analysis_type': 'Gage R&R Analysis',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def run_chart(self, request):
        """??차트"""
        data = request.data.get('data', [])

        if not data:
            return Response(
                {'error': 'Data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = SixSigmaAnalyzer.run_chart(data)

        return Response({
            'analysis_type': 'Run Chart',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def scatter_plot(self, request):
        """?�점??""
        x_data = request.data.get('x_data', [])
        y_data = request.data.get('y_data', [])

        if not x_data or not y_data:
            return Response(
                {'error': 'Both x_data and y_data are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = SixSigmaAnalyzer.scatter_plot(x_data, y_data)

        return Response({
            'analysis_type': 'Scatter Plot',
            'results': result,
        })

    @action(detail=False, methods=['post'])
    def save_analysis(self, request):
        """분석 결과 ?�??""
        project_id = request.data.get('project_id')
        tool_type = request.data.get('tool_type')
        tool_name = request.data.get('tool_name')
        input_data = request.data.get('input_data')
        result_summary = request.data.get('result_summary')
        result_data = request.data.get('result_data')
        chart_data = request.data.get('chart_data')
        interpretation = request.data.get('interpretation')

        # 분석 ?�행
        if tool_type == 'DESCRIPTIVE':
            analysis = SixSigmaAnalyzer.descriptive_statistics(input_data)
        elif tool_type == 'HISTOGRAM':
            analysis = SixSigmaAnalyzer.histogram_data(input_data)
        elif tool_type == 'CAPABILITY':
            analysis = SixSigmaAnalyzer.capability_analysis(
                input_data,
                request.data.get('lsl'),
                request.data.get('usl'),
                request.data.get('target')
            )
        else:
            analysis = {}

        # DB ?�??        tool = StatisticalTool.objects.create(
            project_id=project_id,
            tool_type=tool_type,
            tool_name=tool_name,
            input_data=input_data,
            result_summary=result_summary,
            result_data=result_data or analysis,
            chart_data=chart_data,
            interpretation=interpretation,
            created_by=request.user
        )

        serializer = StatisticalToolSerializer(tool)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
