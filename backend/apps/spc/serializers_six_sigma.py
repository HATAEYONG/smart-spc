"""
Six Sigma DMAIC Serializers
"""

from rest_framework import serializers
from apps.spc.models.six_sigma import (
    DMAICProject, DefinePhase, MeasurePhase, AnalyzePhase,
    ImprovePhase, ControlPhase, DMAICMilestone, DMAICDocument,
    DMAICRisk, StatisticalTool
)
from django.contrib.auth import get_user_model

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """기본 사용자 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class DMAICProjectListSerializer(serializers.ModelSerializer):
    """DMAIC 프로젝트 목록 시리얼라이저"""
    champion_name = serializers.CharField(source='champion.get_full_name', read_only=True)
    progress_percentage = serializers.ReadOnlyField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = DMAICProject
        fields = [
            'id', 'project_code', 'project_name', 'phase', 'status',
            'priority', 'champion_name', 'progress_percentage',
            'start_date', 'target_end_date', 'days_remaining'
        ]

    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.actual_end_date:
            return 0
        delta = obj.target_end_date - timezone.now().date()
        return max(0, delta.days)


class DMAICProjectDetailSerializer(serializers.ModelSerializer):
    """DMAIC 프로젝트 상세 시리얼라이저"""
    champion = UserBasicSerializer(read_only=True)
    process_owner = UserBasicSerializer(read_only=True)
    team_members = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    progress_percentage = serializers.ReadOnlyField()

    # Phase completions
    define_completed = serializers.SerializerMethodField()
    measure_completed = serializers.SerializerMethodField()
    analyze_completed = serializers.SerializerMethodField()
    improve_completed = serializers.SerializerMethodField()
    control_completed = serializers.SerializerMethodField()

    class Meta:
        model = DMAICProject
        fields = '__all__'

    def get_define_completed(self, obj):
        return hasattr(obj, 'define_phase') and obj.define_phase.is_completed

    def get_measure_completed(self, obj):
        return hasattr(obj, 'measure_phase') and obj.measure_phase.is_completed

    def get_analyze_completed(self, obj):
        return hasattr(obj, 'analyze_phase') and obj.analyze_phase.is_completed

    def get_improve_completed(self, obj):
        return hasattr(obj, 'improve_phase') and obj.improve_phase.is_completed

    def get_control_completed(self, obj):
        return hasattr(obj, 'control_phase') and obj.control_phase.is_completed


class DefinePhaseSerializer(serializers.ModelSerializer):
    """Define 단계 시리얼라이저"""

    class Meta:
        model = DefinePhase
        fields = '__all__'


class MeasurePhaseSerializer(serializers.ModelSerializer):
    """Measure 단계 시리얼라이저"""

    class Meta:
        model = MeasurePhase
        fields = '__all__'


class AnalyzePhaseSerializer(serializers.ModelSerializer):
    """Analyze 단계 시리얼라이저"""

    class Meta:
        model = AnalyzePhase
        fields = '__all__'


class ImprovePhaseSerializer(serializers.ModelSerializer):
    """Improve 단계 시리얼라이저"""

    class Meta:
        model = ImprovePhase
        fields = '__all__'


class ControlPhaseSerializer(serializers.ModelSerializer):
    """Control 단계 시리얼라이저"""

    class Meta:
        model = ControlPhase
        fields = '__all__'


class DMAICMilestoneSerializer(serializers.ModelSerializer):
    """DMAIC 마일스톤 시리얼라이저"""

    class Meta:
        model = DMAICMilestone
        fields = '__all__'


class DMAICDocumentSerializer(serializers.ModelSerializer):
    """DMAIC 문서 시리얼라이저"""
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = DMAICDocument
        fields = '__all__'


class DMAICRiskSerializer(serializers.ModelSerializer):
    """DMAIC 리스크 시리얼라이저"""
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = DMAICRisk
        fields = '__all__'


class StatisticalToolSerializer(serializers.ModelSerializer):
    """통계 도구 시리얼라이저"""
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = StatisticalTool
        fields = '__all__'


# 통계 도구 실행을 위한 Request Serializers

class DescriptiveStatsSerializer(serializers.Serializer):
    """기술 통계 분석 Request"""
    data = serializers.ListField(child=serializers.FloatField())
    variable_name = serializers.CharField(required=False, default='Variable')


class HistogramSerializer(serializers.Serializer):
    """히스토그램 Request"""
    data = serializers.ListField(child=serializers.FloatField())
    bins = serializers.IntegerField(required=False, default=10)
    variable_name = serializers.CharField(required=False, default='Variable')


class ParetoSerializer(serializers.Serializer):
    """파레토도 Request"""
    categories = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.IntegerField())
    chart_title = serializers.CharField(required=False, default='Pareto Chart')


class BoxPlotSerializer(serializers.Serializer):
    """상자 수염 그림 Request"""
    groups = serializers.DictField(child=serializers.ListField(child=serializers.FloatField()))


class CorrelationSerializer(serializers.Serializer):
    """상관 분석 Request"""
    x_data = serializers.ListField(child=serializers.FloatField())
    y_data = serializers.ListField(child=serializers.FloatField())
    x_label = serializers.CharField(required=False, default='X')
    y_label = serializers.CharField(required=False, default='Y')


class TTestSerializer(serializers.Serializer):
    """T-검정 Request"""
    sample1 = serializers.ListField(child=serializers.FloatField())
    sample2 = serializers.ListField(child=serializers.FloatField(), required=False)
    mu0 = serializers.FloatField(required=False, default=0)
    test_type = serializers.ChoiceField(
        choices=['one_sample', 'two_independent', 'paired'],
        default='one_sample'
    )
    alpha = serializers.FloatField(required=False, default=0.05)


class ANOVASerializer(serializers.Serializer):
    """분산 분석 Request"""
    groups = serializers.DictField(child=serializers.ListField(child=serializers.FloatField()))
    alpha = serializers.FloatField(required=False, default=0.05)


class CapabilityAnalysisSerializer(serializers.Serializer):
    """공정능력 분석 Request"""
    data = serializers.ListField(child=serializers.FloatField())
    lsl = serializers.FloatField()
    usl = serializers.FloatField()
    target = serializers.FloatField(required=False)


class GageRRSerializer(serializers.Serializer):
    """Gage R&R 분석 Request"""
    # 데이터 형식: [{operator: str, part: str, measurement: float}, ...]
    measurements = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
